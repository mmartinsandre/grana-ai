import matplotlib.pyplot as plt
import io
from telegram import Update
from telegram.ext import ContextTypes
from data_manager import DataManager

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
    
    # Create pie chart
    plt.figure(figsize=(10, 6))
    plt.pie(categories.values(), labels=categories.keys(), autopct='%1.1f%%')
    plt.title("Spending by Category")
    
    # Save plot to buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    # Send plot to user
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=buf)
    
    # Prepare text report
    report = "Spending Analysis:\n\n"
    total_spending = sum(categories.values())
    for category, amount in categories.items():
        percentage = (amount / total_spending) * 100
        report += f"{category}: {amount:.2f} ({percentage:.2f}%)\n"
    
    await update.message.reply_text(report)
