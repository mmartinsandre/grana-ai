from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from data_manager import DataManager
from .common import cancel

FREQUENCY, AMOUNT, CATEGORY, DESCRIPTION = range(4)

async def recurring_transaction_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [InlineKeyboardButton("Diário", callback_data='daily'),
         InlineKeyboardButton("Semanal", callback_data='weekly')],
        [InlineKeyboardButton("Mensal", callback_data='monthly'),
         InlineKeyboardButton("Anual", callback_data='yearly')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Selecione a frequência da transação recorrente:", reply_markup=reply_markup)
    return FREQUENCY

async def frequency_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['frequency'] = query.data
    await query.edit_message_text(f"Frequência definida como {query.data}. Agora, digite o valor:")
    return AMOUNT

async def amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['amount'] = float(update.message.text.replace(',', '.'))
    await update.message.reply_text("Digite a categoria:")
    return CATEGORY

async def category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['category'] = update.message.text
    await update.message.reply_text("Enter a description:")
    return DESCRIPTION

async def description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['description'] = update.message.text
    
    # Save recurring transaction to data manager
    dm = DataManager()
    user_data = dm.get_user_data(update.effective_user.id)
    
    if 'recurring_transactions' not in user_data:
        user_data['recurring_transactions'] = []
    
    user_data['recurring_transactions'].append({
        'frequency': context.user_data['frequency'],
        'amount': context.user_data['amount'],
        'category': context.user_data['category'],
        'description': context.user_data['description']
    })
    
    dm.set_user_data(update.effective_user.id, user_data)
    
    await update.message.reply_text("Recurring transaction added successfully!")
    return ConversationHandler.END

recurring_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('recurring', recurring_transaction_handler)],
    states={
        FREQUENCY: [CallbackQueryHandler(frequency_callback)],
        AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, amount)],
        CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, category)],
        DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, description)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
