from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler
from data_manager import DataManager
from .common import cancel

CURRENCY = range(1)

async def currency_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    currencies = ['BRL', 'USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'SEK']
    
    keyboard = [
        [InlineKeyboardButton(curr, callback_data=curr) for curr in currencies[i:i+3]]
        for i in range(0, len(currencies), 3)
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("Selecione sua moeda preferida:", reply_markup=reply_markup)
    return CURRENCY

async def currency_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    dm = DataManager()
    user_data = dm.get_user_data(update.effective_user.id)
    user_data['currency'] = query.data
    dm.set_user_data(update.effective_user.id, user_data)
    
    currency_symbol = 'R$' if query.data == 'BRL' else query.data
    await query.edit_message_text(f"Sua moeda preferida foi definida como {currency_symbol}")
    return ConversationHandler.END

currency_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('currency', currency_handler)],
    states={
        CURRENCY: [CallbackQueryHandler(currency_callback)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
    per_message=True
)
