# YouTube İndirici Telegram Botu 🎞️🎵

Bu bot, kullanıcılardan aldığı YouTube video linklerini, isteğe bağlı olarak video veya müzik formatında indirip Telegram üzerinden gönderen bir araçtır. `yt-dlp` ve `python-telegram-bot` kütüphaneleri kullanılarak geliştirilmiştir.

---

## Özellikler ✨

* **YouTube Link İşleme**: Gönderilen YouTube video linklerini otomatik olarak tanır.
* **Video/Müzik İndirme Seçeneği**: Kullanıcılara videoyu MP4 olarak mı yoksa müziği MP3 olarak mı indireceklerini seçme imkanı sunar.
* **İlerleme Çubuğu**: İndirme işlemi sırasında kullanıcıya dinamik bir ilerleme çubuğu gösterir.
* **Video Bilgisi ve Thumbnail**: Video başlığını ve thumbnail'ini göstererek kullanıcıya indirme öncesi bilgi verir.
* **Hata Yönetimi**: İndirme sırasında oluşabilecek hataları (geçersiz link, dosya boyutu limiti vb.) yönetir ve kullanıcıya bilgi verir.
* **Geçici Dosya Temizliği**: İndirme tamamlandıktan sonra sunucuda yer kaplamaması için geçici dosyaları otomatik olarak siler.

---

## Kurulum 🚀

Botu kendi sunucunuzda veya yerel makinenizde çalıştırmak için aşağıdaki adımları takip edin.

### Ön Gereksinimler

* **Python 3.8+**: Sisteminizde Python yüklü olmalıdır.
* **`yt-dlp`**: Video ve ses indirme işlemleri için gereklidir.
    ```bash
    sudo apt install yt-dlp # Debian/Ubuntu için
    # veya
    pip install yt-dlp
    ```
* **`ffmpeg`**: Ses/video dönüştürme ve birleştirme işlemleri için gereklidir.
    ```bash
    sudo apt install ffmpeg # Debian/Ubuntu için
    # veya
    brew install ffmpeg # macOS için
    ```

### Adımlar

1.  **Depoyu Klonlayın**:
    ```bash
    git clone [git clone https://github.com/kilic142100/youtube_downloader_bot.git](git clone https://github.com/kilic142100/youtube_downloader_bot.git)
    cd youtube_downloader_bot
    ```

2.  **Sanal Ortam Oluşturun (Önerilir)**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate # Linux/macOS
    # veya
    .\venv\Scripts\activate # Windows
    ```

3.  **Gerekli Kütüphaneleri Yükleyin**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Bot Token'ınızı Ayarlayın**:
    Botunuzu çalıştırmadan önce, Telegram'dan aldığınız bot token'ınızı kod içerisine yapıştırmanız gerekmektedir. `bot.py` dosyasını açın ve `TELEGRAM_BOT_TOKEN` değişkenini kendi token'ınızla değiştirin:
    ```python
    TELEGRAM_BOT_TOKEN = "7809806761:AAE_PIqcw4usIo2gJ8xD-gwdN5S3CPkfph8" # Kendi token'ınızla değiştirin!
    ```
    *İpucu: Hassas bilgileri (API anahtarları gibi) doğrudan koda yazmak yerine, ortam değişkenleri (environment variables) kullanarak yönetmek daha güvenlidir. Gelecekte projenizi büyütürseniz bunu düşünebilirsiniz.*

5.  **Botu Çalıştırın**:
    ```bash
    python3 bot.py
    ```
    Botunuz başarıyla başlatıldığında konsolda "Bot başlatılıyor..." mesajını göreceksiniz.

---

## Kullanım 💡

Botu Telegram'da başlattıktan sonra (`/start` komutu ile):

1.  Bota bir YouTube video linki gönderin.
2.  Bot size videoyu "Video Olarak İndir" veya "Müzik Olarak İndir" seçenekleriyle sunacaktır.
3.  İstediğiniz seçeneğe tıklayın.
4.  Bot, videoyu veya müziği indirip size gönderecektir.

---

## Destek ve Katkıda Bulunma 🤝

Her türlü geri bildirim ve katkı memnuniyetle karşılanır!

* Herhangi bir sorunla karşılaşırsanız veya yeni bir özellik önermek isterseniz, lütfen bir [Issue](https://github.com/KULLANICI_ADIN/youtube_downloader_bot/issues) açın.
* Koda katkıda bulunmak isterseniz, lütfen [Fork](https://docs.github.com/en/get-started/quickstart/fork-a-repo) edin, değişikliklerinizi yapın ve bir [Pull Request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-with-pull-requests/creating-a-pull-request) gönderin.

---

## Lisans 📄

Bu proje MIT Lisansı altında lisanslanmıştır. Daha fazla bilgi için [LICENSE](LICENSE) dosyasına bakın.

---

## İletişim ✉️

* **Telegram**: [@TelegramKullanıcıAdın](https://t.me/TelegramKullanıcıAdın) (örnek)
* **E-posta**: [eposta@example.com](mailto:eposta@example.com) (örnek)
