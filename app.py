from flask import Flask, request, send_file, render_template
import yt_dlp
import os
import uuid
import re

app = Flask(__name__)

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']

    # Get video info first
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
        except Exception as e:
            return f"Error getting info: {str(e)}"

    title = sanitize_filename(info.get("title", "audio"))
    uuid_filename = f"{uuid.uuid4()}"

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': uuid_filename,  # store as UUID without extension
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }],
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        return f"Download error: {str(e)}"

    final_file = uuid_filename + '.mp3'

    try:
        response = send_file(final_file, as_attachment=True, download_name=title + '.mp3')
    except Exception as e:
        return f"Send error: {str(e)}"
    finally:
        if os.path.exists(final_file):
            os.remove(final_file)

    return response

if __name__ == '__main__':
    app.run(debug=True)
