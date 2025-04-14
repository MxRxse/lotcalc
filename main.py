import os
import requests
from dotenv import load_dotenv
from telegram import Bot
from telegram.ext import Updater, CommandHandler
from apscheduler.schedulers.background import BackgroundScheduler
import pytz
import logging
from telegram.error import TimedOut

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
bot = Bot(token=TOKEN)

account_size = 2500  # z. B. 2.500 $
risk_per_trade = account_size * 0.10  # 10 % pro Trade
daily_drawdown_limit = 500  # Maximaler Verlust pro Tag

def get_btc_price():
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        response = requests.get(url, timeout=10)
        data = response.json()
        return float(data["price"])
    except Exception as e:
        logger.error(f"Fehler beim Abruf des BTC-Preises: {e}")
        return None

def send_price(context=None):
    btc_price = get_btc_price()
    if btc_price is None:
        logger.error("Kein BTC-Preis erhalten, überspringe den Sendejob.")
        return
    message = (
        f"Aktueller BTC/USD-Preis: {btc_price:.2f} $\n"
        f"Risiko pro Trade: {risk_per_trade:.2f} $\n"
        f"Maximaler Drawdown: {daily_drawdown_limit:.2f} $"
    )
    try:
        bot.send_message(chat_id=CHAT_ID, text=message)
        logger.info("Nachricht erfolgreich gesendet.")
    except TimedOut as te:
        logger.error(f"TimedOut-Fehler beim Senden der Nachricht: {te}")
    except Exception as e:
        logger.error(f"Fehler beim Senden der Nachricht: {e}")

def start(update, context):
    update.message.reply_text("Steppers LotBot ist aktiv.")

if __name__ == "__main__":
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))

    scheduler = BackgroundScheduler(timezone=pytz.UTC)
    scheduler.add_job(send_price, "interval", hours=1)
    scheduler.start()

    updater.start_polling()
    updater.idle()
