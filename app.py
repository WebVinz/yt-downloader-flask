import os
import uuid
import subprocess
from flask import Flask, request, render_template, send_file
from yt_dlp import YoutubeDL

FFMPEG_FOLDER = "ffmpeg"
FFMPEG_BIN = os.path.join(os.getcwd(), FFMPEG_FOLDER, "ffmpeg")

# Jika ffmpeg belum ada, download versi pre-built yang sudah executable
if not os.path.exists(FFMPEG_BIN):
    print("⏬ Downloading static ffmpeg binary...")
    os.makedirs(FFMPEG_FOLDER, exist_ok=True)
    subprocess.run(f"curl -Lo {FFMPEG_BIN} https://github.com/yt-dlp/FFmpeg-Builds/releases/latest/download/ffmpeg-linux64", shell=True)
    subprocess.run(f"chmod +x {FFMPEG_BIN}", shell=True)

# Tambahkan ke PATH
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + ":" + os.environ["PATH"]

# Debug
print("✅ ffmpeg path:", FFMPEG_BIN)
print("✅ ffmpeg version:\n", subprocess.getoutput(f"{FFMPEG_BIN} -version"))
print("✅ ffmpeg exists:", os.path.exists(FFMPEG_BIN))
print("✅ ffmpeg is executable:", os.access(FFMPEG_BIN, os.X_OK))

# === Flask App ===
app = Flask(__name__)
os.makedirs("downloads", exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    quality = request.form['quality']
    filename = f"{uuid.uuid4()}.mp4"
    filepath = os.path.join("downloads", filename)

    ydl_opts = {
        'format': f'bestvideo[height<={quality}]+bestaudio/best',
        'outtmpl': filepath,
        'ffmpeg_location': FFMPEG_BIN,  # harus path ke file ffmpeg
        'merge_output_format': 'mp4',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
        'postprocessor_args': ['-c:v', 'copy', '-c:a', 'aac'],
        'prefer_ffmpeg': True,
        'noplaylist': True,
        'quiet': True
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return f"<h2>Download Error:</h2><pre>{str(e)}</pre>", 500

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
