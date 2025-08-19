import os
import logging
import feedparser
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get token from environment
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Example RSS feeds
NEWS_FEEDS = {
    "english": "http://feeds.bbci.co.uk/news/rss.xml",
    "hindi": "https://www.bbc.com/hindi/index.xml",
    "geo": "https://www.aljazeera.com/xml/rss/all.xml",
    "career": "https://economictimes.indiatimes.com/jobs/rssfeeds/15626960.cms"
}

# Fetch top 5 headlines from a feed
def get_headlines(url, limit=5):
    feed = feedparser.parse(url)
    headlines = []
    for entry in feed.entries[:limit]:
        headlines.append(f"🔹 {entry.title}\n{entry.link}")
    return "\n\n".join(headlines)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 Hello! I am your News Bot.\n"
        "Created by *Hitman* 🕶️\n\n"
        "Here are your options:\n\n"
        "📰 /english - English News\n"
        "📰 /hindi - Hindi News\n"
        "🌍 /geo - International & Geopolitics\n"
        "💼 /career - Career & Jobs\n\n"
        "⏰ /hourly_on - Turn ON hourly news\n"
        "❌ /hourly_off - Turn OFF hourly news"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# Commands for news
async def english(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_headlines(NEWS_FEEDS["english"]))

async def hindi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_headlines(NEWS_FEEDS["hindi"]))

async def geo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_headlines(NEWS_FEEDS["geo"]))

async def career(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_headlines(NEWS_FEEDS["career"]))

# Hourly news job
async def hourly_news(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    headlines = get_headlines(NEWS_FEEDS["english"])
    await context.bot.send_message(job.chat_id, text="🕒 Hourly News Update:\n\n" + headlines)

# Toggle ON
async def hourly_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    if jobs:
        await update.message.reply_text("✅ Hourly updates are already ON.")
    else:
        context.job_queue.run_repeating(
            hourly_news,
            interval=3600,
            first=10,
            chat_id=chat_id,
            name=str(chat_id)
        )
        await update.message.reply_text("⏰ Hourly news updates turned ON.")

# Toggle OFF
async def hourly_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    if not jobs:
        await update.message.reply_text("❌ Hourly updates are already OFF.")
    else:
        for job in jobs:
            job.schedule_removal()
        await update.message.reply_text("🛑 Hourly news updates turned OFF.")

# Set command menu in Telegram
async def set_commands(app):
    await app.bot.set_my_commands([
        BotCommand("start", "Show available options"),
        BotCommand("english", "Get English News"),
        BotCommand("hindi", "Get Hindi News"),
        BotCommand("geo", "Get International & Geopolitics News"),
        BotCommand("career", "Get Career & Jobs News"),
        BotCommand("hourly_on", "Turn ON hourly news updates"),
        BotCommand("hourly_off", "Turn OFF hourly news updates"),
    ])

# Main function
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("english", english))
    app.add_handler(CommandHandler("hindi", hindi))
    app.add_handler(CommandHandler("geo", geo))
    app.add_handler(CommandHandler("career", career))
    app.add_handler(CommandHandler("hourly_on", hourly_on))
    app.add_handler(CommandHandler("hourly_off", hourly_off))

    app.post_init = set_commands  # set command menu when bot starts

    app.run_polling()

if __name__ == "__main__":
    main()