from flask import Flask, request, render_template_string, send_file
import yt_dlp
import os

app = Flask(__name__)
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Evrensel Video İndirici</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; color: #333; display: flex; flex-direction: column; align-items: center; padding-top: 100px; }
        .container { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; max-width: 600px; width: 100%; }
        h1 { color: #2c3e50; }
        input[type="text"] { width: 80%; padding: 12px; margin: 20px 0; border: 1px solid #ccc; border-radius: 5px; font-size: 16px; }
        button { padding: 12px 25px; background-color: #3498db; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; transition: background 0.3s; }
        button:hover { background-color: #2980b9; }
        .message { margin-top: 20px; color: #e74c3c; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Evrensel Video İndirici</h1>
        <p>YouTube, Twitter, Instagram, TikTok, Vimeo ve daha birçok siteden video indirin.</p>
        <form method="POST">
            <input type="text" name="url" placeholder="Video bağlantısını buraya yapıştırın..." required>
            <br>
            <button type="submit">Videoyu İndir</button>
        </form>
        {% if message %}
            <div class="message">{{ message }}</div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    if request.method == "POST":
        url = request.form.get("url")
        if url:
            ydl_opts = {
                'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
                'format': 'best',
                'quiet': True,
                'no_warnings': True
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                    return send_file(filename, as_attachment=True)
            except Exception as e:
                message = f"Bir hata oluştu: Videoyu indiremedik veya bağlantı desteklenmiyor."
                print(e)

    return render_template_string(HTML, message=message)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
