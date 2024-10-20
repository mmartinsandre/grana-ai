from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from data_manager import DataManager
from datetime import datetime

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    dm = DataManager()
    user_data = dm.get_user_data(user_id)
    transactions = user_data.get("transactions", [])
    today = datetime.now()

    valid_transactions = [t for t in transactions if datetime.strptime(t['date'], "%d/%m/%Y") <= today]
    total = sum(t['amount'] for t in valid_transactions)
    currency = dm.get_user_currency(user_id)
    currency_symbol = 'R$' if currency == 'BRL' else currency
    await update.message.reply_text(f"Seu saldo atual é: {currency_symbol} {total:.2f}")

balance_handler = CommandHandler("balance", balance)
