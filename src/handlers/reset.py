from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from data_manager import DataManager

async def reset_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    dm = DataManager()
    dm.reset_user_data(user_id)
    await update.message.reply_text("Your data has been reset. You can start fresh now.")

reset_command_handler = CommandHandler("reset", reset_handler)
