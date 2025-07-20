# modules/utils/telegram_bot.py

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from main import run_pipeline_for_symbol  # This runs your full logic
import pandas as pd
import os
from dotenv import load_dotenv


load_dotenv()
token = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

#LISTED_COMPANIES_PATH = os.path.join("data", "raw", "listed_companies.csv")

# Dynamically locate project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CSV_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "listed_companies.csv")

def resolve_symbol_from_name(name):
    try:
        df = pd.read_csv(CSV_PATH)
        match = df[df['name'].str.contains(name, case=False, na=False)]

        if not match.empty:
            return match.iloc[0]["symbol"]
        else:
            print(f"[WARN] No match found for: {name}")
            return None

    except Exception as e:
        print(f"[ERROR] While resolving symbol: {e}")
        return None

def resolve_symbol(user_input):
    user_input = user_input.strip().upper()

    try:
        df = pd.read_csv(CSV_PATH)
        df["symbol"] = df["symbol"].astype(str).str.upper()
        df["name"] = df["name"].astype(str).str.upper()

        # Check if input matches symbol
        if user_input in df["symbol"].values:
            return user_input

        # Check if input matches company name
        match = df[df["name"].str.contains(user_input)]
        if not match.empty:
            return match.iloc[0]["symbol"]

        return None
    except Exception as e:
        print(f"[ERROR] While resolving symbol: {e}")
        return None


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    print(f"📩 Received from {chat_id}: {text}")

    symbol = resolve_symbol(text)
    if not symbol:
        await context.bot.send_message(chat_id=chat_id, text="❌ Company not found. Please check the name or symbol.")
        return

    await context.bot.send_message(chat_id=chat_id, text=f"🔍 Processing {symbol}...")

    success = run_pipeline_for_symbol(symbol, chat_id)
    if success:
        await context.bot.send_message(chat_id=chat_id, text=f"✅ Report sent for {symbol}")
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"❌ Failed to generate report for {symbol}")


def main():
    import os
    from dotenv import load_dotenv
    load_dotenv()

    token = os.getenv("TELEGRAM_TOKEN")
    app = ApplicationBuilder().token(token).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("🤖 Telegram bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
