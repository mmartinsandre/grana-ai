from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from data_manager import DataManager

async def delete_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    dm = DataManager()
    user_data = dm.get_user_data(user_id)
    
    if not context.args:
        await update.message.reply_text("Por favor, use o formato: /delete <número da transação>")
        return

    try:
        index = int(context.args[0]) - 1
        if index < 0 or index >= len(user_data.get("transactions", [])):
            await update.message.reply_text("Número de transação inválido.")
            return

        deleted = user_data["transactions"].pop(index)
        dm.set_user_data(user_id, user_data)
        await update.message.reply_text(
            f"Transação removida: {deleted['amount']} - {deleted['category']} - {deleted['description']} ({deleted['date']})"
        )
    except ValueError:
        await update.message.reply_text("Por favor, forneça um número válido para a transação.")

delete_transaction_handler = CommandHandler("delete", delete_transaction)
