from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from data_manager import DataManager
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import io

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    dm = DataManager()
    user_data = dm.get_user_data(user_id)
    transactions = user_data.get("transactions", [])
    
    today = datetime.now()
    last_month = today - timedelta(days=30)
    recent_transactions = [
        t for t in transactions 
        if datetime.strptime(t['date'], "%d/%m/%Y") > last_month
    ]
    
    if not recent_transactions:
        await update.message.reply_text("Não há transações registradas no último mês.")
        return
    
    category_totals = {}
    for t in recent_transactions:
        category = t['category']
        amount = t['amount']
        category_totals[category] = category_totals.get(category, 0) + amount
    
    plt.figure(figsize=(10, 6))
    plt.pie(category_totals.values(), labels=category_totals.keys(), autopct='%1.1f%%')
    plt.title("Gastos por Categoria (Último Mês)")

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    report_text = "Relatório do último mês:\n\n"
    for category, total in category_totals.items():
        report_text += f"{category}: {total:.2f}\n"
    
    await update.message.reply_text(report_text)
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=buf
    )

report_handler = CommandHandler("report", report)
