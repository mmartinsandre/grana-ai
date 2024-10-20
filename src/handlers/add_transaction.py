from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from data_manager import DataManager
from datetime import datetime

AMOUNT, CATEGORY, DESCRIPTION, DATE = range(4)

async def start_add_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Vamos adicionar uma transação. Qual é o valor?",
        reply_markup=ReplyKeyboardRemove()
    )
    return AMOUNT

async def amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['amount'] = float(update.message.text.replace(',', '.'))
    await update.message.reply_text("Qual é a categoria? (Ex: Alimentação, Transporte, etc.)")
    return CATEGORY

async def category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['category'] = update.message.text
    await update.message.reply_text("Adicione uma descrição para a transação.")
    return DESCRIPTION

async def description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['description'] = update.message.text
    await update.message.reply_text("Qual é a data da transação? (Formato: DD/MM/AAAA)")
    return DATE

async def date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    date_str = update.message.text
    try:
        date = datetime.strptime(date_str, "%d/%m/%Y")
        context.user_data['date'] = date_str

        dm = DataManager()
        user_data = dm.get_user_data(user_id)
        user_data["transactions"].append({
            "amount": context.user_data['amount'],
            "category": context.user_data['category'],
            "description": context.user_data['description'],
            "date": context.user_data['date']
        })
        dm.set_user_data(user_id, user_data)

        await update.message.reply_text(
            f"Transação adicionada: {context.user_data['amount']} - "
            f"{context.user_data['category']} - {context.user_data['description']} ({context.user_data['date']})"
        )
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Data inválida. Por favor, use o formato DD/MM/AAAA.")
        return DATE

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Operação cancelada.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

add_transaction_handler = ConversationHandler(
    entry_points=[CommandHandler('add', start_add_transaction)],
    states={
        AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, amount)],
        CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, category)],
        DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, description)],
        DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, date)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)
