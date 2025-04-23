

from flask import Flask, render_template, request, send_file, after_this_request
import yt_dlp
import os
import glob

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, world!'

# Run the app on the correct port
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Get the port from environment or use 5000 by default
    app.run(host="0.0.0.0", port=port) 

DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']

    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'verbose': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        list_of_files = glob.glob(os.path.join(DOWNLOAD_DIR, '*'))
        latest_file = max(list_of_files, key=os.path.getctime)

        # auto Clean up after sending
        @after_this_request
        def remove_file(response):
            try:
                os.remove(latest_file)
                print("🧹 Cleaned up:", latest_file)
            except Exception as e:
                print("❌ Failed to delete:", e)
            return response

        return send_file(latest_file, as_attachment=True)

    except Exception as e:
        return f"<h3 style='color:red;'>❌ Error: {str(e)}</h3>"

if __name__ == '__main__':
    app.run(debug=True)
