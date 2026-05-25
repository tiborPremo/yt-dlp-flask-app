from flask import Flask, render_template, request, send_file
from urllib.parse import urlparse, urlsplit
import yt_dlp
from yt_dlp import YoutubeDL
import os
import uuid

app = Flask(__name__)

TEMP_DIR = "temp_downloads" 
os.makedirs(TEMP_DIR, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET": 
        return render_template("index.html")
    
    if request.method == "POST":
        whitelist = ["youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be", "music.youtube.com", "www.youtube-nocookie.com"]
        url = request.form.get("url", "").strip()

        if not url or url.strip() == "":    
            return "Missing URl", 400
            
        u = urlsplit(url.strip())

        if u.username or u.password or "@" in url.split('#')[0].split('?')[0]:
            return "Érvénytelen URL formátum (userinfo nem megengedett)", 400
        
        if u.scheme not in ["http", "https"]:
            return "Nem biztonságos link", 400
 
        if u.hostname is None:
            return "Nincs hostname", 400
        
        hostname = u.hostname.lower();

        if hostname not in whitelist:
            return "Nem youtube link", 400
        
        if u.path == "" or u.path == "/":
            return "A YouTube főoldalról nem lehet letölteni, adj meg egy videót!", 400
        
        selectedChoice = request.form.get("select")

        file_id = str(uuid.uuid4())
        output_template = os.path.join(TEMP_DIR, file_id + ".%(ext)s")
        
        if selectedChoice == "mp3":
            ydl_opts = {
                'format' : 'bestaudio/best',
                'postprocessors' : [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec' : 'mp3',
                    'preferredquality' : 192,
                }],
                'outtmpl' : output_template,
                'quiet' : False
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)

                filename = ydl.prepare_filename(info)
                final_file = filename.rsplit(".", 1)[0] + ".mp3"

            return send_file(final_file, as_attachment=True)

        if selectedChoice == "mp4":
            ydl_opts = {
                'format': 'best',
                'outtmpl': output_template,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)

                filename = ydl.prepare_filename(info)
                final_file = filename.rsplit(".", 1)[0] + ".mp4"

            return send_file(final_file, as_attachment=True)

           
            
    return "Minden valid, indulhat a letöltés!", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)