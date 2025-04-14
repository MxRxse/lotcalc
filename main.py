import os
import requests
from dotenv import load_dotenv
from telegram import Bot
from telegram.ext import Updater, CommandHandler
from apscheduler.schedulers.background import BackgroundScheduler
import pytz  # Importiert pytz für die Zeitzone

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
bot = Bot(token=TOKEN)

# Risikomanagement-Konstanten
account_size = 2500  # z. B. 2.500 $
risk_per_trade = account_size * 0.10  # 10 % pro Trade
daily_drawdown_limit = 500  # Maximaler Verlust pro Tag

def get_btc_price():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    response = requests.get(url)
    data = response.json()
    return float(data["price"])

def send_price(context=None):
    btc_price = get_btc_price()
    message = (
        f"Aktueller BTC/USD-Preis: {btc_price:.2f} $\n"
        f"Risiko pro Trade: {risk_per_trade:.2f} $\n"
        f"Maximaler Drawdown: {daily_drawdown_limit:.2f} $"
    )
    bot.send_message(chat_id=CHAT_ID, text=message)

def start(update, context):
    update.message.reply_text("Steppers LotBot ist aktiv.")

if __name__ == "__main__":
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))

    scheduler = BackgroundScheduler(timezone=pytz.UTC)  # Setze explizit pytz.UTC als Zeitzone
    scheduler.add_job(send_price, "interval", hours=1)
    scheduler.start()

    updater.start_polling()
    updater.idle()
