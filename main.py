import os
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")

def get_btc_price():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    r = requests.get(url)
    return float(r.json()["price"])

def calculate_lot(btc_price, stop_loss, capital=10000, invest_pct=0.10, risk=250):
    invest = capital * invest_pct
    lot_by_risk = (risk / stop_loss) * btc_price / 100000
    lot_by_capital = invest / btc_price
    return round(min(lot_by_risk, lot_by_capital), 3)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hey! Schick mir einfach deinen Stop-Loss in Dollar (z. B. 250), und ich berechne deine Lotgröße für BTC/USD.")

def handle_message(update: Update, context: CallbackContext):
    try:
        sl = float(update.message.text.strip())
        btc_price = get_btc_price()
        lot = calculate_lot(btc_price, sl)
        msg = (
            f"Aktueller BTC/USD-Preis: {btc_price:.2f} $
"
            f"Stop-Loss: {sl} $
"
            f"Empfohlene Lotgröße: *{lot} Lots*
"
            f"(Risiko: max 250 $, Invest: 10 % von 10.000 $)"
        )
        update.message.reply_text(msg, parse_mode='Markdown')
    except Exception as e:
        update.message.reply_text("Bitte sende nur eine Zahl (z. B. 250).")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()