import subprocess
import os

# 🛠️ Install ffmpeg at runtime
subprocess.run("curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz | tar -xJ", shell=True)
subprocess.run("mv ffmpeg-* ffmpeg-dir && chmod +x ffmpeg-dir/ffmpeg", shell=True)
os.environ["PATH"] = os.getcwd() + "/ffmpeg-dir:" + os.environ["PATH"]

from flask import Flask, request, render_template, send_file
from yt_dlp import YoutubeDL
import uuid
# ...

app = Flask(__name__)
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    url = request.form['url']
    quality = request.form['quality']

    filename_id = str(uuid.uuid4())  # generate random filename
    output_template = os.path.join(DOWNLOAD_DIR, f"{filename_id}.%(ext)s")

    ydl_opts = {
    'format': f"bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
    'outtmpl': output_template,
    'merge_output_format': 'mp4',
    'quiet': True,
}

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.download([url])

        # cari file hasil download
        downloaded_file = None
        for ext in ['mp4', 'mkv', 'webm']:
            possible_path = os.path.join(DOWNLOAD_DIR, f"{filename_id}.{ext}")
            if os.path.exists(possible_path):
                downloaded_file = possible_path
                break

        if not downloaded_file:
            return "Gagal menemukan file hasil download.", 500

        return send_file(downloaded_file, as_attachment=True)

    except Exception as e:
        return f"Gagal mendownload: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
