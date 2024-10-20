import logging
from telegram.ext import Application, CommandHandler
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

def main():
    config = Config()
    dm = DataManager()

    application = Application.builder().token(config.TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("iniciar", start_handler))
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

    application.run_polling()

if __name__ == '__main__':
    main()
