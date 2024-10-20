import io
from telegram import Update
from telegram.ext import ContextTypes
from data_manager import DataManager
import plotly.graph_objects as go

async def analytics_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    dm = DataManager()
    
    # Get user's transactions
    transactions = dm.get_user_transactions(user_id)
    
    # Prepare data for visualization
    categories = {}
    for transaction in transactions:
        if transaction['category'] in categories:
            categories[transaction['category']] += transaction['amount']
        else:
            categories[transaction['category']] = transaction['amount']
    
    # Create pie chart using Plotly
    fig = go.Figure(data=[go.Pie(labels=list(categories.keys()), values=list(categories.values()))])
    fig.update_layout(title_text="Gastos por Categoria")
    
    # Save plot to buffer
    img_bytes = fig.to_image(format="png")
    
    # Send plot to user
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=img_bytes)
    
    # Prepare text report
    report = "Análise de Gastos:\n\n"
    total_spending = sum(categories.values())
    for category, amount in categories.items():
        percentage = (amount / total_spending) * 100
        report += f"{category}: {amount:.2f} ({percentage:.2f}%)\n"
    
    await update.message.reply_text(report)
