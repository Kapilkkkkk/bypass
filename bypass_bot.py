import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

async def bypass_link(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        # Open the link (try-catch for errors)
        try:
            await page.goto(url, timeout=60000)
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(3)  # Extra wait time for JavaScript-based redirects
            final_url = page.url
        except Exception as e:
            final_url = f"❌ Error: {e}"
        await browser.close()
        return final_url

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Send me a download link, and I'll bypass the ads for you.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text.startswith("http"):
        await update.message.reply_text("⏳ Please wait while I bypass the ads...")
        try:
            final_link = await bypass_link(text)
            await update.message.reply_text(f"✅ Final link:\n{final_link}")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
    else:
        await update.message.reply_text("Send a valid link starting with http:// or https://")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Bot is running...")
    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
