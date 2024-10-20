from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from data_manager import DataManager
from .common import cancel

CATEGORY, AMOUNT, PERIOD = range(3)

async def budget_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    dm = DataManager()
    user_data = dm.get_user_data(user_id)
    categories = user_data.get("categories", [])
    
    keyboard = [[InlineKeyboardButton(cat, callback_data=cat)] for cat in categories]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("Selecione uma categoria para o seu orçamento:", reply_markup=reply_markup)
    return CATEGORY

async def category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['category'] = query.data
    await query.edit_message_text(f"Categoria definida como {query.data}. Agora, digite o valor do orçamento:")
    return AMOUNT

async def amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['amount'] = float(update.message.text.replace(',', '.'))
    
    keyboard = [
        [InlineKeyboardButton("Semanal", callback_data='weekly'),
         InlineKeyboardButton("Mensal", callback_data='monthly')],
        [InlineKeyboardButton("Anual", callback_data='yearly')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("Selecione o período do orçamento:", reply_markup=reply_markup)
    return PERIOD

async def period_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    dm = DataManager()
    user_data = dm.get_user_data(update.effective_user.id)
    
    if 'budgets' not in user_data:
        user_data['budgets'] = []
    
    user_data['budgets'].append({
        'category': context.user_data['category'],
        'amount': context.user_data['amount'],
        'period': query.data
    })
    
    dm.set_user_data(update.effective_user.id, user_data)
    
    await query.edit_message_text(f"Orçamento definido: {context.user_data['amount']} para {context.user_data['category']} ({query.data})")
    return ConversationHandler.END

budget_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('budget', budget_handler)],
    states={
        CATEGORY: [CallbackQueryHandler(category_callback)],
        AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, amount)],
        PERIOD: [CallbackQueryHandler(period_callback)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
