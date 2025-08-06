import os
import uuid
import subprocess
from flask import Flask, request, render_template, send_file
from yt_dlp import YoutubeDL

# ✅ Setup ffmpeg (Runtime untuk Railway atau server)
if not os.path.exists("ffmpeg"):
    subprocess.run("curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz | tar -xJ", shell=True)
    for item in os.listdir():
        if item.startswith("ffmpeg") and os.path.isdir(item):
            os.rename(item, "ffmpeg")
            break
    os.environ["PATH"] = os.getcwd() + "/ffmpeg:" + os.environ["PATH"]

# ✅ Flask setup
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

    # ✅ Ini yang benar: ydl_opts + convert audio ke AAC
    ydl_opts = {
        'format': f'bestvideo[height<={quality}]+bestaudio/best',
        'outtmpl': filepath,
        'merge_output_format': 'mp4',
        'postprocessor_args': [
            '-c:v', 'copy',     # video tidak di-re-encode
            '-c:a', 'aac'       # audio dikonversi ke AAC
        ]
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return send_file(filepath, as_attachment=True)

# ✅ Listen to Railway port
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
