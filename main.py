import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from yt_dlp import YoutubeDL

# Bot token එක .env ෆයිල් එකෙන් ගන්න
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Logging සදහා සකස් කිරීම
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("කැමති Dailymotion URL එකක් /download ටයිප් කර පතුරන්න.")

# Progress hook function එක
async def progress_hook(d):
    if d['status'] == 'downloading':
        downloaded = d.get('downloaded_bytes', 0)
        total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
        if total:
            percent = downloaded * 100 / total
            text = f"Downloading: {percent:.2f}%"
            try:
                await d['msg'].edit_text(text)
            except Exception:
                pass

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("ශෙයාගැනීම: /download <Dailymotion_URL>")
    url = context.args[0]
    msg = await update.message.reply_text("Download හසුරවමින්... 0%")

    def hook(d):
        d['msg'] = msg
        import asyncio; asyncio.create_task(progress_hook(d))

    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloaded.%(ext)s',
        'noplaylist': True,
        'progress_hooks': [hook]
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        await msg.edit_text("Uploading to Telegram...")
        await update.message.reply_video(video=open(filename, 'rb'))
        os.remove(filename)
        await msg.edit_text("සම්පූර්ණයි! 🙌")
    except Exception as e:
        logger.error(f"Error: {e}")
        await msg.edit_text(f"දෝෂයක්: {e}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("download", download))
    logger.info("Bot ඇරඹුණා...")
    app.run_polling()
