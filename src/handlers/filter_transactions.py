from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from data_manager import DataManager
from datetime import datetime
from .common import cancel

FILTER_DATE = range(1)

async def filter_transactions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Por favor, forneça uma data de referência no formato DD/MM/AAAA para calcular o saldo do dia.")
    return FILTER_DATE

async def filter_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    date_str = update.message.text
    try:
        reference_date = datetime.strptime(date_str, "%d/%m/%Y")
        dm = DataManager()
        user_data = dm.get_user_data(user_id)
        transactions = user_data.get("transactions", [])
        filtered_transactions = [t for t in transactions if datetime.strptime(t['date'], "%d/%m/%Y") <= reference_date]
        
        if filtered_transactions:
            total = sum(t['amount'] for t in filtered_transactions)
            message = f"Saldo até {date_str}: {total:.2f}\nTransações:\n"
            for i, t in enumerate(filtered_transactions):
                message += f"{i+1}. {t['amount']} - {t['category']} - {t['description']} ({t['date']})\n"
            await update.message.reply_text(message)
        else:
            await update.message.reply_text(f"Não há transações registradas até {date_str}.")
    except ValueError:
        await update.message.reply_text("Data inválida. Por favor, use o formato DD/MM/AAAA.")
    return ConversationHandler.END

filter_transactions_handler = ConversationHandler(
    entry_points=[CommandHandler('filter', filter_transactions)],
    states={
        FILTER_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, filter_date)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
