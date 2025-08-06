import os
import uuid
import subprocess
from flask import Flask, request, render_template, send_file
from yt_dlp import YoutubeDL

# ✅ Download dan siapkan ffmpeg saat runtime (di Railway)
# ✅ Download dan siapkan ffmpeg saat runtime (di Railway)
if not os.path.exists("ffmpeg"):
    subprocess.run(
        "curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz | tar -xJ",
        shell=True,
    )
    for item in os.listdir():
        if item.startswith("ffmpeg") and os.path.isdir(item):
            os.rename(item, "ffmpeg")
            break
    # ⚠️ Tambahkan izin eksekusi
    subprocess.run("chmod +x ffmpeg/ffmpeg ffmpeg/ffprobe", shell=True)

# ✅ Tambahkan ffmpeg ke PATH
os.environ["PATH"] = os.path.abspath("ffmpeg") + ":" + os.environ["PATH"]


# ✅ Inisialisasi Flask
app = Flask(__name__)

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
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
        'postprocessor_args': [
            '-c:v', 'copy',  # jangan encode ulang video
            '-c:a', 'aac'    # convert audio dari opus ke aac
        ]
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return send_file(filepath, as_attachment=True)

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
