#!/bin/bash

echo "🔧 Gerekli ortam hazırlanıyor..."

# Gerekli sistem araçlarını kontrol et (isteğe bağlı ama faydalı)
command -v ffmpeg >/dev/null 2>&1 || { echo >&2 "❗ ffmpeg kurulu değil. Kurmak için: pkg install ffmpeg"; exit 1; }
command -v yt-dlp >/dev/null 2>&1 || { echo >&2 "❗ yt-dlp kurulu değil. Kurmak için: pkg install yt-dlp"; exit 1; }

# Python ortamı kontrol (isteğe bağlı)
command -v python >/dev/null 2>&1 || { echo >&2 "❗ Python kurulu değil. Kurmak için: pkg install python"; exit 1; }

echo "📦 Gerekli Python kütüphaneleri yükleniyor..."
pip install -r requirements.txt

echo "🚀 Bot başlatılıyor..."
python bot.py
