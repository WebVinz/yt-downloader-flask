import os
import uuid
import subprocess
from flask import Flask, request, render_template, send_file
from yt_dlp import YoutubeDL

# === Setup ffmpeg static ===
FFMPEG_FOLDER = "ffmpeg"
FFMPEG_BIN = os.path.join(os.getcwd(), FFMPEG_FOLDER, "ffmpeg")

# Cek apakah ffmpeg sudah ada
if not os.path.exists(FFMPEG_BIN):
    print("⏬ Downloading ffmpeg...")
    subprocess.run("curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz -o ffmpeg.tar.xz", shell=True)
    subprocess.run("mkdir -p tmpffmpeg && tar -xf ffmpeg.tar.xz -C tmpffmpeg --strip-components=1", shell=True)
    subprocess.run(f"mv tmpffmpeg {FFMPEG_FOLDER}", shell=True)
    subprocess.run(f"chmod +x {FFMPEG_BIN}", shell=True)
    subprocess.run("rm -f ffmpeg.tar.xz", shell=True)

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

    # === Download Options ===
    y    ydl_opts = {
        'format': f'bestvideo[height<={quality}]+bestaudio/best',
        'outtmpl': filepath,
        'ffmpeg_location': FFMPEG_BIN,  # BUKAN folder, tapi file binary
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
