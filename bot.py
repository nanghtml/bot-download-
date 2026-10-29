import asyncio
import logging
import os
import re
import shutil
import uuid
from pathlib import Path

import yt_dlp
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
log = logging.getLogger("downloader-bot")

TOKEN = os.getenv("BOT_TOKEN", "")
MAX_MB = int(os.getenv("MAX_MB", "50"))  # Bot API ធម្មតា = 50MB
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)
URL_RE = re.compile(r"https?://\S+")

# ដាក់កំណត់ចំនួនទាញយកព្រមគ្នា ដើម្បីកុំឱ្យ server ធ្ងន់
SEMAPHORE = asyncio.Semaphore(3)


def download_media(url: str, mode: str, workdir: Path) -> Path:
    """ទាញយកមេឌៀ (ដំណើរការក្នុង thread ដាច់ដោយឡែក)។"""
    opts = {
        "outtmpl": str(workdir / "%(title).60s [%(id)s].%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "restrictfilenames": False,
        "max_filesize": MAX_MB * 1024 * 1024,
    }
    # បើមាន cookies (សម្រាប់ Instagram/Facebook ឯកជន)
    if Path("cookies.txt").exists():
        opts["cookiefile"] = "cookies.txt"

    if mode == "audio":
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ]
    elif mode == "720":
        opts["format"] = (
            "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]/best"
        )
        opts["merge_output_format"] = "mp4"
    else:  # best
        opts["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best"
        opts["merge_output_format"] = "mp4"

    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

    files = [p for p in workdir.iterdir() if p.is_file()]
    if not files:
        raise RuntimeError("រកមិនឃើញឯកសារ (ប្រហែលធំជាងកំណត់)")
    return max(files, key=lambda p: p.stat().st_size)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "សួស្តី! 👋\n"
        "ផ្ញើ link ពី YouTube, TikTok, Facebook, Instagram, Twitter/X "
        "ឬវេទិកាផ្សេងៗមកខ្ញុំ ហើយខ្ញុំនឹងទាញយកឱ្យ។"
    )


async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    match = URL_RE.search(update.message.text or "")
    if not match:
        await update.message.reply_text("សូមផ្ញើ link ត្រឹមត្រូវ (ចាប់ផ្តើមដោយ http)។")
        return

    context.user_data["url"] = match.group(0)
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🎬 វីដេអូ 720p", callback_data="720"),
                InlineKeyboardButton("🎬 គុណភាពល្អបំផុត", callback_data="best"),
            ],
            [InlineKeyboardButton("🎵 សំឡេង MP3", callback_data="audio")],
        ]
    )
    await update.message.reply_text("ជ្រើសរើសទម្រង់៖", reply_markup=keyboard)


async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    url = context.user_data.get("url")
    if not url:
        await query.edit_message_text("សូមផ្ញើ link ម្តងទៀត។")
        return

    mode = query.data
    await query.edit_message_text("⏳ កំពុងទាញយក...")

    workdir = DOWNLOAD_DIR / uuid.uuid4().hex
    workdir.mkdir(parents=True, exist_ok=True)
    chat_id = query.message.chat_id

    try:
        async with SEMAPHORE:
            loop = asyncio.get_running_loop()
            path = await loop.run_in_executor(
                None, download_media, url, mode, workdir
            )

        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > MAX_MB:
            await query.edit_message_text(
                f"❌ ឯកសារធំពេក ({size_mb:.1f}MB) លើសកំណត់ {MAX_MB}MB។ "
                "សាកល្បងជ្រើស 720p ឬ MP3។"
            )
            return

        await query.edit_message_text("📤 កំពុងផ្ញើ...")
        with open(path, "rb") as f:
            if mode == "audio":
                await context.bot.send_audio(
                    chat_id, f, read_timeout=120, write_timeout=120
                )
            else:
                await context.bot.send_video(
                    chat_id,
                    f,
                    supports_streaming=True,
                    read_timeout=120,
                    write_timeout=120,
                )
        await query.edit_message_text("✅ រួចរាល់!")
    except Exception as e:  # noqa: BLE001
        log.exception("Download failed")
        msg = str(e)
        if len(msg) > 300:
            msg = msg[:300] + "..."
        await query.edit_message_text(f"❌ បរាជ័យ៖ {msg}")
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def main():
    if not TOKEN:
        raise SystemExit("សូមកំណត់ BOT_TOKEN (មើល README.md)")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(handle_choice))
    log.info("Bot started")
    app.run_polling()


if __name__ == "__main__":
    main()
