from flask import Flask, request, render_template_string
import os
import requests

app = Flask(__name__)

# ✅ APIキーは環境変数から取得（RenderならDashboard→Environmentで設定）
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

HTML = """
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>YouTube 情報取得</title>
</head>
<body>
<h2>YouTube 動画情報（公式API利用）</h2>
<form method="post">
  <input type="text" name="url" size="50" placeholder="YouTube URLまたは動画ID">
  <button type="submit">取得</button>
</form>

{% if video %}
  <h3>✅ 取得結果</h3>
  <p>タイトル: {{ video.title }}</p>
  <p>チャンネル: {{ video.channel }}</p>
  <p>再生数: {{ video.views }}</p>
  <p>公開日: {{ video.published }}</p>
  <p><a href="https://www.youtube.com/watch?v={{ video.id }}" target="_blank">YouTubeで見る</a></p>
{% elif error %}
  <p style="color:red;">⚠️ {{ error }}</p>
{% endif %}
</body>
</html>
"""

def extract_video_id(url_or_id: str) -> str:
    """
    YouTube URL か ID が渡されても動画IDだけ抽出する。
    """
    if "youtube.com" in url_or_id or "youtu.be" in url_or_id:
        import re
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url_or_id)
        return match.group(1) if match else None
    return url_or_id.strip()

@app.route("/", methods=["GET", "POST"])
def index():
    video = None
    error = None
    if request.method == "POST":
        url = request.form["url"].strip()
        vid = extract_video_id(url)
        if not vid:
            error = "動画IDを抽出できませんでした。"
        elif not YOUTUBE_API_KEY:
            error = "サーバーにAPIキーが設定されていません。"
        else:
            api_url = (
                f"https://www.googleapis.com/youtube/v3/videos"
                f"?part=snippet,statistics&id={vid}&key={YOUTUBE_API_KEY}"
            )
            r = requests.get(api_url)
            data = r.json()
            if "items" in data and data["items"]:
                item = data["items"][0]
                snippet = item["snippet"]
                stats = item.get("statistics", {})
                video = type("V", (), {
                    "id": vid,
                    "title": snippet["title"],
                    "channel": snippet["channelTitle"],
                    "views": stats.get("viewCount", "N/A"),
                    "published": snippet["publishedAt"]
                })
            else:
                error = "動画が見つかりません。APIキーやIDを確認してください。"
    return render_template_string(HTML, video=video, error=error)

if __name__ == "__main__":
    # Renderで動かす場合は host/port は環境変数PORTに合わせる
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
