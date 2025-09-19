from flask import Flask, request, send_from_directory, render_template_string
import yt_dlp
import os

app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

HTML = """
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>YouTube ダウンロード</title>
</head>
<body>
<h2>YouTube ダウンロード（Render版）</h2>
<form method="post">
  <input type="text" name="url" size="50" placeholder="YouTube URLを入力">
  <button type="submit">ダウンロード開始</button>
</form>
{% if filename %}
  <p>✅ 完了: <a href="/downloads/{{ filename }}">こちらから保存</a></p>
{% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    filename = None
    if request.method == "POST":
        url = request.form["url"].strip()
        if url:
            ydl_opts = {
                "outtmpl": f"{DOWNLOAD_FOLDER}/%(title)s.%(ext)s",
                "format": "bestvideo+bestaudio/best",
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = os.path.basename(ydl.prepare_filename(info))
    return render_template_string(HTML, filename=filename)

@app.route("/downloads/<path:filename>")
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    # RenderはPORT環境変数を使用
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
