from flask import Flask, request, render_template_string, send_file
import yt_dlp
import os
import tempfile

app = Flask(__name__)
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Evrensel Video İndirici (IDM Benzeri)</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; color: #333; display: flex; flex-direction: column; align-items: center; padding-top: 50px; }
        .container { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; max-width: 700px; width: 100%; }
        h1 { color: #2c3e50; }
        input[type="text"] { width: 80%; padding: 12px; margin: 20px 0; border: 1px solid #ccc; border-radius: 5px; font-size: 16px; }
        textarea { width: 80%; padding: 12px; margin: 10px 0; border: 1px solid #ccc; border-radius: 5px; font-size: 14px; height: 100px; font-family: monospace; resize: vertical; }
        button { padding: 12px 25px; background-color: #3498db; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; transition: background 0.3s; margin-top: 10px; }
        button:hover { background-color: #2980b9; }
        .message { margin-top: 20px; color: #e74c3c; font-weight: bold; }
        .success { color: #2ecc71; }
        details { text-align: left; margin-top: 20px; padding: 10px; background: #f9f9f9; border-radius: 5px; border: 1px solid #eee; }
        summary { font-weight: bold; cursor: pointer; color: #2c3e50; }
        .help-text { font-size: 13px; color: #7f8c8d; margin-bottom: 10px; display: block; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Evrensel Video İndirici</h1>
        <p>YouTube, Udemy, Twitter, Instagram, TikTok, ve rastgele web sitelerinden (IDM gibi) video indirin.</p>
        <form method="POST">
            <input type="text" name="url" placeholder="Video veya kurs bağlantısını buraya yapıştırın..." required>

            <details>
                <summary>Gelişmiş Seçenekler (Udemy / Şifreli Siteler İçin)</summary>
                <p class="help-text">
                    <strong>Neden gerekli?</strong> Udemy gibi şifreli sitelerden kurs indirmek için oturum açmış olmanız gerekir.<br>
                    <strong>Nasıl yapılır?</strong> Tarayıcınıza "Get cookies.txt LOCALLY" eklentisini kurun. İndirmek istediğiniz siteye (örn. Udemy) giriş yapın. Eklentiye tıklayıp "Export" (Dışa Aktar) seçeneğini seçin. Kopyaladığınız içeriği aşağıdaki kutuya yapıştırın.
                </p>
                <textarea name="cookies" placeholder="cookies.txt içeriğini buraya yapıştırın (İsteğe bağlı)..."></textarea>
            </details>
            <br>
            <button type="submit">Videoyu/Kursu İndir</button>
        </form>
        {% if message %}
            <div class="message {% if success %}success{% endif %}">{{ message }}</div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    success = False

    if request.method == "POST":
        url = request.form.get("url")
        cookies_content = request.form.get("cookies", "").strip()

        if url:
            # yt-dlp options (IDM benzeri genel yakalama ve playlist desteği eklendi)
            ydl_opts = {
                'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', # En iyi kalite mp4
                'quiet': False, # Logları görebilmek için
                'no_warnings': True,
                'noplaylist': False, # Playlist (Udemy kursu vb.) desteği
                'ignoreerrors': True, # Hata veren videoyu atla devam et
            }

            cookie_file_path = None
            if cookies_content:
                # Cookie içeriğini geçici bir dosyaya yaz
                fd, cookie_file_path = tempfile.mkstemp(suffix=".txt", text=True)
                with os.fdopen(fd, 'w') as f:
                    f.write(cookies_content)
                ydl_opts['cookiefile'] = cookie_file_path
                print("Cookies dosyası ayarlandı.")

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)

                    if info:
                        # Eğer bu bir playlist/kurs ise ilk videoyu veya klasörü baz almayıp başarılı mesajı döndürebiliriz
                        # Basitlik açısından ilk inen dosyayı gönderiyoruz veya genel başarılı mesajı
                        if 'entries' in info:
                            message = f"Playlist/Kurs başarıyla indirildi. Dosyalar '{DOWNLOAD_DIR}' klasörüne kaydedildi."
                            success = True
                        else:
                            filename = ydl.prepare_filename(info)
                            return send_file(filename, as_attachment=True)
                    else:
                         message = "Video bulunamadı veya indirilemedi."
            except Exception as e:
                message = f"Bir hata oluştu: {str(e)}"
                print(f"Hata: {e}")
            finally:
                # Geçici cookie dosyasını temizle
                if cookie_file_path and os.path.exists(cookie_file_path):
                    os.remove(cookie_file_path)

    return render_template_string(HTML, message=message, success=success)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
