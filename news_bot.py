import os
import logging
import feedparser
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get token from environment
TOKEN = "8326722997:AAFBv3CBTaET-j-pmvkRT5Fumx71vCNsuzg"

# News Feeds (India focused + International)
NEWS_FEEDS = {
    "english": "http://feeds.bbci.co.uk/news/rss.xml",
    "hindi": "https://www.bbc.com/hindi/index.xml",
    "geo": "https://www.aljazeera.com/xml/rss/all.xml",
    "finance": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "career": "https://economictimes.indiatimes.com/jobs/rssfeeds/15626960.cms",
    "toi": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
    "hindu": "https://www.thehindu.com/feeder/default.rss",
    "indianexpress": "https://indianexpress.com/feed/"
}

# Fetch top N headlines
def get_headlines(url, limit=5):
    feed = feedparser.parse(url)
    headlines = []
    for entry in feed.entries[:limit]:
        headlines.append(f"🔹 {entry.title}\n{entry.link}")
    return "\n\n".join(headlines)

# Combined headlines from all categories
def get_topnews(limit=2):
    text = "📰 Top Combined News:\n\n"
    for name, url in NEWS_FEEDS.items():
        headlines = get_headlines(url, limit)
        if headlines:
            text += f"📌 {name.capitalize()}:\n{headlines}\n\n"
    return text

# Intro
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Welcome to Hitman News Bot 🕶️\n"
        "Get free latest headlines in English, Hindi, International, Finance, Career, and Indian news.\n\n"
        "Commands:\n"
        "/english - English News\n"
        "/hindi - Hindi News\n"
        "/geo - World & Geopolitics\n"
        "/finance - Banking & Finance\n"
        "/career - Career & Jobs\n"
        "/toi - Times of India\n"
        "/hindu - The Hindu\n"
        "/indianexpress - Indian Express\n"
        "/topnews - Top Combined News\n\n"
        "/notify_on <category> - Hourly updates\n"
        "/notify_off - Stop updates\n\n"
        "Created by Hitman 🚀"
    )
    await update.message.reply_text(text)

# Category commands
async def english(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_headlines(NEWS_FEEDS["english"]))

async def hindi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_headlines(NEWS_FEEDS["hindi"]))

async def geo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_headlines(NEWS_FEEDS["geo"]))

async def finance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_headlines(NEWS_FEEDS["finance"]))

async def career(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_headlines(NEWS_FEEDS["career"]))

async def toi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_headlines(NEWS_FEEDS["toi"]))

async def hindu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_headlines(NEWS_FEEDS["hindu"]))

async def indianexpress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_headlines(NEWS_FEEDS["indianexpress"]))

async def topnews(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_topnews())

# Job for hourly updates
async def send_updates(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    category = job.data
    if category == "topnews":
        headlines = get_topnews()
    else:
        headlines = get_headlines(NEWS_FEEDS[category], 5)
    await context.bot.send_message(job.chat_id, f"⏰ Hourly {category.capitalize()} News:\n\n{headlines}")

# Enable notifications
async def notify_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if len(context.args) != 1 or (context.args[0] not in NEWS_FEEDS and context.args[0] != "topnews"):
        await update.message.reply_text(
            "Please choose a category: english, hindi, geo, finance, career, toi, hindu, indianexpress, topnews\n"
            "Example: /notify_on english"
        )
        return

    category = context.args[0]

    # Remove old job if exists
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    for job in current_jobs:
        job.schedule_removal()

    # Add new job
    context.job_queue.run_repeating(
        send_updates,
        interval=3600,  # every hour
        first=10,       # first after 10s
        chat_id=chat_id,
        name=str(chat_id),
        data=category
    )
    await update.message.reply_text(f"✅ Hourly updates for {category.capitalize()} enabled.")

# Disable notifications
async def notify_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    if not jobs:
        await update.message.reply_text("No active hourly updates.")
        return

    for job in jobs:
        job.schedule_removal()

    await update.message.reply_text("❌ Hourly updates stopped.")

# Main
def main():
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("english", english))
    app.add_handler(CommandHandler("hindi", hindi))
    app.add_handler(CommandHandler("geo", geo))
    app.add_handler(CommandHandler("finance", finance))
    app.add_handler(CommandHandler("career", career))
    app.add_handler(CommandHandler("toi", toi))
    app.add_handler(CommandHandler("hindu", hindu))
    app.add_handler(CommandHandler("indianexpress", indianexpress))
    app.add_handler(CommandHandler("topnews", topnews))
    app.add_handler(CommandHandler("notify_on", notify_on))
    app.add_handler(CommandHandler("notify_off", notify_off))

    app.run_polling()

if __name__ == "__main__":
    main()
