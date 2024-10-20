from telegram import Update
from telegram.ext import ContextTypes

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"Olá {user.first_name}! Eu sou o Pataco, seu assistente financeiro. "
        "Use /ajuda para ver a lista de comandos disponíveis."
    )
