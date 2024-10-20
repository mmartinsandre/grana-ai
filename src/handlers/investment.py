from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from data_manager import DataManager
from .common import cancel

TYPE, AMOUNT, DESCRIPTION = range(3)

async def investment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [InlineKeyboardButton("Ações", callback_data='stock'),
         InlineKeyboardButton("Criptomoedas", callback_data='crypto')],
        [InlineKeyboardButton("Imóveis", callback_data='real_estate'),
         InlineKeyboardButton("Outros", callback_data='other')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Selecione o tipo de investimento:", reply_markup=reply_markup)
    return TYPE

async def type_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['type'] = query.data
    await query.edit_message_text(f"Tipo de investimento definido como {query.data}. Agora, digite o valor investido:")
    return AMOUNT

async def amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['amount'] = float(update.message.text.replace(',', '.'))
    await update.message.reply_text("Digite uma descrição ou nome para este investimento:")
    return DESCRIPTION

async def description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['description'] = update.message.text
    
    dm = DataManager()
    user_data = dm.get_user_data(update.effective_user.id)
    
    if 'investments' not in user_data:
        user_data['investments'] = []
    
    user_data['investments'].append({
        'type': context.user_data['type'],
        'amount': context.user_data['amount'],
        'description': context.user_data['description']
    })
    
    dm.set_user_data(update.effective_user.id, user_data)
    
    await update.message.reply_text("Investimento adicionado com sucesso!")
    return ConversationHandler.END

investment_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('invest', investment_handler)],
    states={
        TYPE: [CallbackQueryHandler(type_callback)],
        AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, amount)],
        DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, description)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
    per_message=True
)
