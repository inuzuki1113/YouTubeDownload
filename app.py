import os
import subprocess
import tempfile
from flask import Flask, render_template, request, jsonify, send_file
import requests
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# --- サムネイルとタイトル取得 ---
def get_video_info(video_url):
    import urllib.parse as urlparse
    from urllib.parse import parse_qs
    # URLから動画IDを取得
    query = urlparse.urlparse(video_url)
    vid = None
    if query.hostname in ("youtu.be",):
        vid = query.path[1:]
    elif query.hostname in ("www.youtube.com", "youtube.com"):
        if query.path == "/watch":
            vid = parse_qs(query.query).get("v", [None])[0]
        elif query.path.startswith("/embed/"):
            vid = query.path.split("/")[2]
    if not vid:
        return None

    api_url = (
        f"https://www.googleapis.com/youtube/v3/videos"
        f"?part=snippet&id={vid}&key={YOUTUBE_API_KEY}"
    )
    r = requests.get(api_url)
    data = r.json()
    if "items" not in data or not data["items"]:
        return None
    snippet = data["items"][0]["snippet"]
    return {
        "title": snippet["title"],
        "thumbnail": snippet["thumbnails"]["high"]["url"]
    }

# --- ダウンロード処理 ---
def download_video(video_url):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    tmp.close()
    cmd = [
        "yt-dlp",
        "-f", "best",
        "-o", tmp.name,
        video_url
    ]
    subprocess.run(cmd, check=True)
    return tmp.name

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        info = get_video_info(url)
        if not info:
            return render_template("index.html", error="動画情報を取得できませんでした")
        return render_template("index.html", info=info, url=url)
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url")
    filepath = download_video(url)
    return send_file(filepath, as_attachment=True, download_name="video.mp4")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
