from flask import Flask, request, render_template, send_file, jsonify
import yt_dlp
import os

app = Flask(__name__)

# Set download folder
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Path to FFmpeg executable
FFMPEG_PATH = r"C:\Users\user\Downloads\ffmpeg-7.1-full_build\ffmpeg-7.1-full_build\bin\ffmpeg.exe"

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
        'merge_output_format': 'mp4',  # Ensure merged output is in MP4 format
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'ffmpeg_location': FFMPEG_PATH,  # Set correct FFmpeg path
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename
    except Exception as e:
        return str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    video_url = request.form.get('url')
    quality = request.form.get('quality', 'best')  # Default to best quality
    
    if not video_url:
        return jsonify({"error": "No URL provided"}), 400
    
    filename = download_yt_video(video_url, quality)
    if not os.path.exists(filename):
        return jsonify({"error": "Download failed. Check server logs."}), 500
    
    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
