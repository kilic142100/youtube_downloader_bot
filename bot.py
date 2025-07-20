import logging
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram.constants import ParseMode
from telegram.error import BadRequest
import subprocess
import os
import asyncio
import re
import json

# --- AYARLAR ---
# Lütfen kendi Telegram Bot Token'ınızı buraya yapıştırın.
# Burayı kendi bot token'ınızla değiştirmeyi unutmayın!
TELEGRAM_BOT_TOKEN = "BOT_TOKEN_BURAYA_YAZ"

# Loglama ayarları
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Kullanıcı verilerini saklamak için sözlük
user_data = {}

# --- YARDIMCI FONKSİYONLAR ---

def create_progress_bar(percentage: float, bar_length: int = 20) -> str:
    """Yüzdelik değere göre metin tabanlı ilerleme çubuğu oluşturur."""
    filled_length = int(bar_length * percentage / 100)
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    return f"`[{bar}] {percentage:.1f}%`"

async def get_video_info(url: str):
    """yt-dlp kullanarak video bilgilerini alır."""
    try:
        command = ["yt-dlp", "--dump-json", "--no-playlist", url]
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode == 0:
            return json.loads(stdout.decode('utf-8'))
        else:
            logger.error(f"Video bilgisi alınamadı (yt-dlp stderr): {stderr.decode('utf-8')}")
            return None
    except Exception as e:
        logger.error(f"Video bilgisi alırken programatik hata: {e}")
        return None

# --- TELEGRAM HANDLER'LARI ---

async def start(update: Update, context):
    """Bot başlatıldığında kullanıcıya hoş geldin mesajı gönderir."""
    await update.message.reply_text(
        'Merhaba! Bana bir YouTube video linki gönderin, ben de sizin için indireyim.\n\n'
        'Video veya müzik olarak indirme seçeneği sunacağım. 😊'
    )

async def handle_youtube_link(update: Update, context):
    """Kullanıcının gönderdiği YouTube linkini işler ve seçenek sunar."""
    user_message = update.message.text
    chat_id = update.message.chat_id

    # YouTube linklerini yakalamak için daha esnek bir regex
    youtube_regex = re.compile(
        r'(?:https?://)?(?:www\.)?(?:m\.)?(?:youtube\.com|youtu\.be)/'
        r'(?:watch\?v=|embed/|v/|shorts/|playlist\?list=)?([\w-]{11})(?:\S+)?'
    )
    match = youtube_regex.search(user_message)

    if not match:
        await update.message.reply_text("Lütfen geçerli bir YouTube video linki gönderin.")
        return

    video_url = match.group(0) # Eşleşen tam URL'yi al
    user_data[chat_id] = {'url': video_url}

    initial_message = await update.message.reply_text("Video bilgileri alınıyor... ⏳")

    video_info = await get_video_info(video_url)

    if not video_info:
        await initial_message.edit_text(
            "Üzgünüm, bu video hakkında bilgi alınamadı. Link geçersiz veya özel olabilir."
        )
        return

    title = video_info.get('title', 'Bilinmeyen Başlık')
    thumbnail_url = video_info.get('thumbnail')

    keyboard = [
        [InlineKeyboardButton("Video Olarak İndir 🎞️", callback_data="download_video")],
        [InlineKeyboardButton("Müzik Olarak İndir 🎵", callback_data="download_audio")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    caption_text = f"**Video Başlığı:** `{title}`\n\nBu videoyu nasıl indirmek istersiniz?"

    try:
        await initial_message.delete()
        if thumbnail_url:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=thumbnail_url,
                caption=caption_text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text=caption_text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
    except Exception as e:
        logger.error(f"Seçenek mesajı gönderilirken hata: {e}")
        await initial_message.edit_text("Seçenekleri sunarken bir hata oluştu.")

async def handle_callback_query(update: Update, context):
    """Buton tıklamalarını işler."""
    query = update.callback_query
    await query.answer()

    data = query.data
    chat_id = query.message.chat_id

    video_url = user_data.get(chat_id, {}).get('url')
    if not video_url:
        await query.edit_message_caption(caption="Süre doldu veya bir hata oluştu. Lütfen linki tekrar gönderin.")
        return

    try:
        if query.message.photo: # Eğer mesajda fotoğraf varsa caption'ı düzenle
            if data == "download_video":
                await query.edit_message_caption(caption="En iyi kalitede video indiriliyor, lütfen bekleyin...", parse_mode=ParseMode.MARKDOWN)
            elif data == "download_audio":
                await query.edit_message_caption(caption="Müzik indiriliyor, lütfen bekleyin...", parse_mode=ParseMode.MARKDOWN)
        else: # Sadece metin mesajı ise text'i düzenle
            if data == "download_video":
                await query.edit_message_text(text="En iyi kalitede video indiriliyor, lütfen bekleyin...", parse_mode=ParseMode.MARKDOWN)
            elif data == "download_audio":
                await query.edit_message_text(text="Müzik indiriliyor, lütfen bekleyin...", parse_mode=ParseMode.MARKDOWN)
    except BadRequest as e:
        logger.warning(f"Callback mesajı düzenlenirken hata (muhtemelen 'Message is not modified'): {e}")

    # Seçime göre direkt indirmeyi başlat
    if data == "download_video":
        await download_media(update, context, video_url, media_type="video")
    elif data == "download_audio":
        await download_media(update, context, video_url, media_type="audio")

async def download_media(update: Update, context, url: str, media_type: str):
    """Belirtilen URL'den medyayı (video veya ses) indirir ve gönderir."""
    chat_id = update.effective_chat.id
    
    # Yeni bir mesaj olarak indirme durumunu bildir
    status_message = await context.bot.send_message(
        chat_id=chat_id, 
        text="İndirme işlemi hazırlanıyor... ⏳",
        parse_mode=ParseMode.MARKDOWN
    )

    downloaded_file_path = None
    temp_filename_prefix = f"{chat_id}_{int(time.time())}" # Benzersiz ve zaman damgalı prefix
    video_title = "İndirilen Medya"

    try:
        video_info = await get_video_info(url)
        if video_info:
            # Geçersiz karakterleri dosya adından temizle
            video_title = re.sub(r'[\\/:*?"<>|]', '_', video_info.get('title', video_title))
        
        command = ["yt-dlp", "--no-playlist", "--progress", "--newline"]
        
        if media_type == "video":
            # MP4 formatı tercih edilir, en iyi video ve sesi birleştirir.
            # Alternatif olarak en iyi MP4 veya en iyi genel formatı dener.
            format_selection = "bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4]/best"
            output_template = f"{temp_filename_prefix}.%(ext)s"
            command.extend([
                "--format", format_selection,
                "--output", output_template,
                "--merge-output-format", "mp4"
            ])
            expected_ext = "mp4"
        elif media_type == "audio":
            output_template = f"{temp_filename_prefix}.%(ext)s"
            command.extend([
                "--extract-audio", 
                "--audio-format", "mp3", 
                "--audio-quality", "0", 
                "--output", output_template
            ])
            expected_ext = "mp3"
            
        command.append(url)
        
        process = await asyncio.create_subprocess_exec(
            *command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )

        last_update_time = 0
        last_percentage = -1.0 # Son güncellenen yüzdeyi tutmak için
        
        while True:
            line_bytes = await process.stdout.readline()
            if not line_bytes:
                break
            
            line_str = line_bytes.decode('utf-8', errors='ignore').strip()
            
            # İndirme ilerlemesini yakala
            match_download_progress = re.search(r'\[download\]\s+([0-9\.]+)%', line_str)
            if match_download_progress:
                current_percentage = float(match_download_progress.group(1))
                current_time = time.time()
                
                # Sadece %2'den fazla değişim olduğunda veya 100% olduğunda ve en az 1.5 saniye geçtiyse güncelle
                if (current_percentage >= last_percentage + 2 or current_percentage == 100) and \
                   (current_time - last_update_time > 1.5):
                    
                    last_update_time = current_time
                    last_percentage = current_percentage
                    progress_bar = create_progress_bar(current_percentage)
                    try:
                        await status_message.edit_text(
                            text=f"**İndiriliyor:** `{video_title}`\n{progress_bar}",
                            parse_mode=ParseMode.MARKDOWN
                        )
                    except BadRequest as e:
                        if "Message is not modified" not in str(e):
                            logger.warning(f"İlerleme mesajı güncellenirken hata (BadRequest): {e}")
            
            # Post-processing (ffmpeg) ilerlemesini de yakala
            match_post_progress = re.search(r'ETA\s+\d{2}:\d{2}', line_str) # Örnek: "ETA 00:05"
            if "Post-processing" in line_str and match_post_progress:
                current_time = time.time()
                if current_time - last_update_time > 1.5:
                    last_update_time = current_time
                    try:
                        await status_message.edit_text(
                            text=f"**İşleniyor:** `{video_title}`\n`Post-processing...`",
                            parse_mode=ParseMode.MARKDOWN
                        )
                    except BadRequest as e:
                        if "Message is not modified" not in str(e):
                            logger.warning(f"Post-processing mesajı güncellenirken hata (BadRequest): {e}")

        await process.wait() # Sürecin tamamlanmasını bekle

        if process.returncode != 0:
            stderr_output = (await process.stderr.read()).decode('utf-8')
            logger.error(f"yt-dlp hata kodu: {process.returncode}, stderr:\n{stderr_output}")
            error_msg = "Üzgünüm, indirme sırasında bir hata oluştu. 😕"
            
            if "ffmpeg" in stderr_output.lower() and "not found" in stderr_output.lower():
                error_msg += "\n\n**Hata:** `ffmpeg` bulunamadı. Lütfen botun çalıştığı sisteme `ffmpeg` kurun."
            elif "unsupported url" in stderr_output.lower():
                error_msg += "\n\n**Hata:** Girdiğiniz link desteklenmiyor veya geçersiz."
            elif "private video" in stderr_output.lower() or "unavailable" in stderr_output.lower():
                error_msg += "\n\n**Hata:** Video özel veya kullanılamıyor."
            else:
                error_msg += f"\n\nDetay: `{stderr_output.split('ERROR:')[-1].strip()[:150]}...`" if "ERROR:" in stderr_output else ""
            
            await status_message.edit_text(error_msg, parse_mode=ParseMode.MARKDOWN)
            return

        # İndirilen dosyayı doğru şekilde bulma
        # yt-dlp, çıktı dosya adını `--output` şablonuna göre oluşturur.
        # Genellikle temp_filename_prefix ile başlayan ve doğru uzantıyla biten tek bir dosya olur.
        found_files = [f for f in os.listdir('.') if f.startswith(temp_filename_prefix) and f.endswith(f".{expected_ext}")]
        
        if found_files:
            downloaded_file_path = max(found_files, key=os.path.getmtime) # En yeni dosyayı al
        else:
            # Eğer beklenen uzantıyla bulamazsa, merge işlemi sonrası farklı bir uzantı oluşmuş olabilir (örn: .webm -> .mp4)
            # Bu durumda temp_filename_prefix ile başlayan herhangi bir dosyayı ara
            all_temp_files = [f for f in os.listdir('.') if f.startswith(temp_filename_prefix)]
            if all_temp_files:
                downloaded_file_path = max(all_temp_files, key=os.path.getmtime)


        if not downloaded_file_path or not os.path.exists(downloaded_file_path):
            await status_message.edit_text("İndirme tamamlandı ancak dosya bulunamadı. Lütfen tekrar deneyin.")
            return

        file_size_mb = os.path.getsize(downloaded_file_path) / (1024 * 1024)
        logger.info(f"İndirilen dosya boyutu: {file_size_mb:.2f} MB")
        
        # Telegram API dosya boyutu limiti (2000 MB = 2 GB)
        if file_size_mb > 1990: 
            await status_message.edit_text(
                f"Dosya boyutu ({file_size_mb:.2f} MB) çok büyük. Telegram üzerinden gönderilemiyor. "
                "2 GB'dan küçük videoları deneyin. 🚫",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        await status_message.edit_text("Dosya yükleniyor... 📤")
        
        with open(downloaded_file_path, 'rb') as media_file:
            if media_type == "video":
                await context.bot.send_video(
                    chat_id=chat_id, 
                    video=media_file, 
                    caption=f"`{video_title}`",
                    supports_streaming=True, 
                    parse_mode=ParseMode.MARKDOWN,
                    # thumbnail=video_info.get('thumbnail') # Eğer isterseniz thumbnail de ekleyebilirsiniz
                )
            elif media_type == "audio":
                await context.bot.send_audio(
                    chat_id=chat_id, 
                    audio=media_file, 
                    title=video_title,
                    caption=f"`{video_title}`", 
                    parse_mode=ParseMode.MARKDOWN,
                    # thumbnail=video_info.get('thumbnail') # Eğer isterseniz thumbnail de ekleyebilirsiniz
                )
        
        await status_message.delete()
        await context.bot.send_message(chat_id=chat_id, text="İşlem tamamlandı! 🎉")

    except Exception as e:
        logger.error(f"Genel indirme/yükleme hatası: {e}", exc_info=True)
        try:
            await status_message.edit_text(f"Beklenmedik bir hata oluştu: `{type(e).__name__}`. Lütfen tekrar deneyin.")
        except Exception:
            pass # Eğer status_message bile güncellenemiyorsa yapacak bir şey yok
        
    finally:
        # İndirme ile ilgili tüm geçici dosyaları temizle
        for f in os.listdir('.'):
            # temp_filename_prefix ile başlayan tüm dosyaları sil (hem .part hem de final dosyasını kapsar)
            if f.startswith(temp_filename_prefix):
                try:
                    os.remove(f)
                    logger.info(f"Geçici dosya silindi: {f}")
                except OSError as e:
                    logger.error(f"Geçici dosya silinirken hata: {e}")
        
        if chat_id in user_data:
            del user_data[chat_id]

def main():
    """Botu başlatır ve çalıştırır."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex(r'youtube\.com|youtu\.be'), handle_youtube_link))
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    logger.info("Bot başlatılıyor...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    logger.info("Bot durduruldu.")

if __name__ == "__main__":
    main()
