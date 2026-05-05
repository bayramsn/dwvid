document.getElementById('downloadBtn').addEventListener('click', () => {
    chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
        let currentUrl = tabs[0].url;

        // Yeni sekmede uygulamanın arayüzünü açıp URL'yi ekleyebiliriz
        // veya direkt bir API'ye istek atabiliriz. En güvenlisi arayüzü açmak:

        // URL'yi panoya kopyala
        navigator.clipboard.writeText(currentUrl).then(() => {
            alert("Sayfa bağlantısı kopyalandı! Şimdi indirici uygulamasında yapıştırabilirsiniz.");
            window.open('http://localhost:5000', '_blank');
        }).catch(err => {
            console.error('Kopyalama başarısız oldu: ', err);
            // Kopyalanamazsa da sekmeyi aç
            window.open('http://localhost:5000', '_blank');
        });
    });
});
