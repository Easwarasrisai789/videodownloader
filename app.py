from flask import Flask, request, render_template, send_file, jsonify
import yt_dlp
import os

app = Flask(__name__)

# Set up the download folder
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Check if running locally or in deployment
if os.getenv("RENDER") or os.getenv("RAILWAY"):
    FFMPEG_PATH = "/usr/bin/ffmpeg"  # Default FFmpeg path on Linux servers
else:
    FFMPEG_PATH = r"C:\Users\user\Downloads\ffmpeg-7.1-full_build\ffmpeg-7.1-full_build\bin\ffmpeg.exe"  # Local Windows path

# Available video quality options
QUALITY_MAP = {
    "144p": "bestvideo[height<=144]+bestaudio/best",
    "360p": "bestvideo[height<=360]+bestaudio/best",
    "720p": "bestvideo[height<=720]+bestaudio/best",
    "1080p": "bestvideo[height<=1080]+bestaudio/best",
    "best": "bestvideo+bestaudio/best"  # Auto-select best quality
}

def download_yt_video(url, quality):
    ydl_opts = {
        'format': QUALITY_MAP.get(quality, "bestvideo+bestaudio/best"),
        'merge_output_format': 'mp4',
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'ffmpeg_location': FFMPEG_PATH,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = os.path.join(DOWNLOAD_FOLDER, f"{info['title']}.mp4")
            return filename
    except Exception as e:
        return None, str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    video_url = request.form.get('url')
    quality = request.form.get('quality', 'best')

    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    filename, error = download_yt_video(video_url, quality)
    if not filename or not os.path.exists(filename):
        return jsonify({"error": f"Download failed: {error}"}), 500

    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Uses cloud-assigned port
    app.run(host="0.0.0.0", port=port, debug=True)
