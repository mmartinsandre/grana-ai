import logging
import os
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update
from config import Config
from handlers import (
    start_handler, 
    help_handler, 
    add_transaction_handler, 
    filter_transactions_handler,
    delete_transaction_handler,
    balance_handler,
    categories_handler,
    report_handler,
    goal_handler,
    recurring_conv_handler,
    budget_conv_handler,
    investment_conv_handler,
    currency_conv_handler,
    analytics_handler,
    reset_command_handler
)
from data_manager import DataManager

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Exception while handling an update: {context.error}")

def main():
    config = Config()
    dm = DataManager()

    try:
        application = Application.builder().token(config.TELEGRAM_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start_handler))
        application.add_handler(CommandHandler("ajuda", help_handler))
        application.add_handler(add_transaction_handler)
        application.add_handler(filter_transactions_handler)
        application.add_handler(delete_transaction_handler)
        application.add_handler(CommandHandler("saldo", balance_handler))
        application.add_handler(categories_handler)
        application.add_handler(CommandHandler("relatorio", report_handler))
        application.add_handler(goal_handler)
        application.add_handler(recurring_conv_handler)
        application.add_handler(budget_conv_handler)
        application.add_handler(investment_conv_handler)
        application.add_handler(currency_conv_handler)
        application.add_handler(CommandHandler("analise", analytics_handler))
        application.add_handler(CommandHandler("resetar", reset_command_handler))

        # Add error handler
        application.add_error_handler(error_handler)

        logger.info("Bot started successfully")
        application.run_polling()
    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")

if __name__ == '__main__':
    main()
