import os
import uuid
import subprocess
from flask import Flask, request, render_template, send_file
from yt_dlp import YoutubeDL

FFMPEG_DIR = os.path.abspath("ffmpeg")
FFMPEG_BIN = os.path.join(FFMPEG_DIR, "ffmpeg")
FFPROBE_BIN = os.path.join(FFMPEG_DIR, "ffprobe")

if not os.path.exists(FFMPEG_BIN):
    subprocess.run(
        "curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz | tar -xJ",
        shell=True,
    )
    for item in os.listdir():
        if item.startswith("ffmpeg") and os.path.isdir(item):
            os.rename(item, "ffmpeg")
            break
    subprocess.run("chmod +x ffmpeg/ffmpeg ffmpeg/ffprobe", shell=True)

os.environ["PATH"] = FFMPEG_DIR + ":" + os.environ["PATH"]

# 🧪 Debug cek
print("✅ WHICH ffmpeg:", subprocess.getoutput("which ffmpeg"))
print("✅ ffmpeg version:\n", subprocess.getoutput("ffmpeg -version"))
print("✅ ffmpeg exists:", os.path.exists(FFMPEG_BIN))
print("✅ ffmpeg is executable:", os.access(FFMPEG_BIN, os.X_OK))

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
        'merge_output_format': 'mp4',
        'ffmpeg_location': FFMPEG_BIN,  # ✅ WAJIB pointing ke binary ffmpeg
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
