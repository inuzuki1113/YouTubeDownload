from flask import Flask, render_template, request
import os, re, requests

app = Flask(__name__)

# ✅ 環境変数から取得（ローカルなら直接文字列でもOK）
API_KEY = os.getenv("YOUTUBE_API_KEY", "ここにローカル用のキー")

def extract_video_id(url_or_id: str) -> str:
    """URLまたはIDから動画IDだけを抽出"""
    # すでにIDだけならそのまま返す
    if re.fullmatch(r"[0-9A-Za-z_-]{11}", url_or_id):
        return url_or_id
    # URLからID抽出
    patterns = [
        r"v=([0-9A-Za-z_-]{11})",
        r"youtu\.be/([0-9A-Za-z_-]{11})",
        r"shorts/([0-9A-Za-z_-]{11})"
    ]
    for p in patterns:
        m = re.search(p, url_or_id)
        if m:
            return m.group(1)
    return ""

@app.route("/", methods=["GET", "POST"])
def index():
    title = thumb_url = None
    if request.method == "POST":
        input_text = request.form["url"].strip()
        video_id = extract_video_id(input_text)
        if video_id:
            api_url = (
                "https://www.googleapis.com/youtube/v3/videos"
                f"?id={video_id}&key={API_KEY}&part=snippet"
            )
            r = requests.get(api_url)
            if r.ok:
                data = r.json()
                if data["items"]:
                    snippet = data["items"][0]["snippet"]
                    title = snippet["title"]
                    # 高解像度優先
                    thumb_url = snippet["thumbnails"].get("maxres",
                                snippet["thumbnails"]["high"])["url"]
    return render_template("index.html", title=title, thumb_url=thumb_url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
