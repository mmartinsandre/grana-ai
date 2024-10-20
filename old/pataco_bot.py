import logging
import json
from datetime import datetime, timedelta
import locale
import matplotlib.pyplot as plt
import io
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Configuração de logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração de localidade
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Constantes
AMOUNT, CATEGORY, DESCRIPTION, DATE, FILTER_DATE = range(5)
DATA_FILE = 'user_data.json'

# Dados do usuário
user_data = {}

def save_user_data():
    with open(DATA_FILE, 'w') as f:
        json.dump(user_data, f)

def load_user_data():
    global user_data
    try:
        with open(DATA_FILE, 'r') as f:
            user_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        user_data = {}

def format_currency(value):
    return locale.currency(value, grouping=True, symbol=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Comando /start recebido")
    user = update.effective_user
    user_id = str(user.id)
    if user_id not in user_data:
        user_data[user_id] = {"transactions": [], "goals": []}
    save_user_data()
    await update.message.reply_text(
        f"Olá {user.first_name}! Eu sou o Pataco, seu assistente financeiro. "
        "Aqui estão alguns comandos que você pode usar:\n\n"
        "/add - Adicionar uma transação\n"
        "/filter - Filtrar transações por data\n"
        "/delete - Excluir uma transação\n"
        "/balance - Verificar o saldo atual\n"
        "/categories - Gerenciar categorias\n"
        "/report - Gerar relatório mensal\n"
        "/goal - Definir uma meta de economia\n"
        "/help - Mostrar esta mensagem de ajuda\n\n"
        "Como posso ajudar você hoje?"
    )

async def start_add_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Vamos adicionar uma transação. Qual é o valor?",
        reply_markup=ReplyKeyboardRemove()
    )
    return AMOUNT

async def amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['amount'] = float(update.message.text.replace(',', '.'))
    await update.message.reply_text("Qual é a categoria? (Ex: Alimentação, Transporte, etc.)")
    return CATEGORY

async def category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['category'] = update.message.text
    await update.message.reply_text("Adicione uma descrição para a transação.")
    return DESCRIPTION

async def description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['description'] = update.message.text
    await update.message.reply_text("Qual é a data da transação? (Formato: DD/MM/AAAA)")
    return DATE

async def date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.effective_user.id)
    date_str = update.message.text
    try:
        date = datetime.strptime(date_str, "%d/%m/%Y")
        context.user_data['date'] = date_str

        if user_id not in user_data:
            user_data[user_id] = {
                "transactions": [],
                "categories": ["Alimentação", "Transporte", "Moradia", "Lazer", "Outros"],
                "goals": []
            }

        user_data[user_id]["transactions"].append({
            "amount": context.user_data['amount'],
            "category": context.user_data['category'],
            "description": context.user_data['description'],
            "date": context.user_data['date']
        })
        save_user_data()

        await update.message.reply_text(
            f"Transação adicionada: {format_currency(context.user_data['amount'])} - "
            f"{context.user_data['category']} - {context.user_data['description']} ({context.user_data['date']})"
        )
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Data inválida. Por favor, use o formato DD/MM/AAAA.")
        return DATE

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Operação cancelada.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def filter_transactions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Por favor, forneça uma data de referência no formato DD/MM/AAAA para calcular o saldo do dia.")
    return FILTER_DATE

async def filter_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.effective_user.id)
    date_str = update.message.text
    try:
        reference_date = datetime.strptime(date_str, "%d/%m/%Y")
        transactions = user_data.get(user_id, {}).get("transactions", [])
        filtered_transactions = [t for t in transactions if datetime.strptime(t['date'], "%d/%m/%Y") <= reference_date]
        
        if filtered_transactions:
            total = sum(t['amount'] for t in filtered_transactions)
            message = f"Saldo até {date_str}: {format_currency(total)}\nTransações:\n"
            for i, t in enumerate(filtered_transactions):
                message += f"{i+1}. {format_currency(t['amount'])} - {t['category']} - {t['description']} ({t['date']})\n"
            await update.message.reply_text(message)
        else:
            await update.message.reply_text(f"Não há transações registradas até {date_str}.")
    except ValueError:
        await update.message.reply_text("Data inválida. Por favor, use o formato DD/MM/AAAA.")
    return ConversationHandler.END

async def delete_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    try:
        index = int(context.args[0]) - 1
        deleted = user_data[user_id]["transactions"].pop(index)
        save_user_data()
        await update.message.reply_text(f"Transação removida: {format_currency(deleted['amount'])} - {deleted['category']} - {deleted['description']} ({deleted['date']})")
    except (IndexError, ValueError):
        await update.message.reply_text("Por favor, use o formato: /delete <número da transação>")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    transactions = user_data[user_id]["transactions"]
    today = datetime.now()

    # Filtrar transações futuras
    valid_transactions = [t for t in transactions if datetime.strptime(t['date'], "%d/%m/%Y") <= today]

    # Calcular o saldo total das transações válidas
    total = sum(t['amount'] for t in valid_transactions)
    await update.message.reply_text(f"Seu saldo atual é: {format_currency(total)}")

async def categories(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    if not context.args:
        categories = user_data[user_id]["categories"]
        await update.message.reply_text(f"Suas categorias: {', '.join(categories)}\n\nPara adicionar uma nova categoria, use: /categories add <nome da categoria>\nPara remover uma categoria, use: /categories remove <nome da categoria>")
    elif context.args[0] == "add":
        new_category = ' '.join(context.args[1:])
        if new_category not in user_data[user_id]["categories"]:
            user_data[user_id]["categories"].append(new_category)
            save_user_data()
            await update.message.reply_text(f"Categoria '{new_category}' adicionada com sucesso.")
        else:
            await update.message.reply_text(f"Categoria '{new_category}' já existe.")
    elif context.args[0] == "remove":
        category_to_remove = ' '.join(context.args[1:])
        if category_to_remove in user_data[user_id]["categories"]:
            user_data[user_id]["categories"].remove(category_to_remove)
            save_user_data()
            await update.message.reply_text(f"Categoria '{category_to_remove}' removida com sucesso.")
        else:
            await update.message.reply_text(f"Categoria '{category_to_remove}' não encontrada.")

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    transactions = user_data[user_id]["transactions"]
    
    today = datetime.now()
    last_month = today - timedelta(days=30)
    recent_transactions = [t for t in transactions if datetime.strptime(t['date'], "%d/%m/%Y") > last_month]
    
    if not recent_transactions:
        await update.message.reply_text("Não há transações registradas no último mês.")
        return
    
    category_totals = {}
    for t in recent_transactions:
        category = t['category']
        amount = t['amount']
        if category in category_totals:
            category_totals[category] += amount
        else:
            category_totals[category] = amount
    
    plt.figure(figsize=(10, 6))
    plt.pie(category_totals.values(), labels=category_totals.keys(), autopct='%1.1f%%')
    plt.title("Gastos por Categoria (Último Mês)")

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    report_text = "Relatório do último mês:\n\n"
    for category, total in category_totals.items():
        report_text += f"{category}: {format_currency(total)}\n"
    
    await update.message.reply_text(report_text)
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=buf)

async def goal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    if not context.args:
        goals = user_data[user_id].get("goals", [])
        if goals:
            message = "Suas metas de economia:\n"
            for i, g in enumerate(goals):
                message += f"{i+1}. {g['description']}: {format_currency(g['current'])} / {format_currency(g['target'])}\n"
            await update.message.reply_text(message)
        else:
            await update.message.reply_text("Você não tem metas de economia definidas. Use /goal add <descrição> <valor alvo> para adicionar uma.")
    elif context.args[0] == "add":
        try:
            description = ' '.join(context.args[1:-1])
            target = float(context.args[-1].replace(',', '.'))
            user_data[user_id].setdefault("goals", []).append({
                "description": description,
                "target": target,
                "current": 0
            })
            save_user_data()
            await update.message.reply_text(f"Meta adicionada: {description} - Alvo: {format_currency(target)}")
        except (IndexError, ValueError):
            await update.message.reply_text("Por favor, use o formato: /goal add <descrição> <valor alvo>")
    elif context.args[0] == "update":
        try:
            index = int(context.args[1]) - 1
            amount = float(context.args[2].replace(',', '.'))
            goals = user_data[user_id].get("goals", [])
            if 0 <= index < len(goals):
                goals[index]["current"] += amount
                save_user_data()
                await update.message.reply_text(f"Meta atualizada: {goals[index]['description']} - Progresso: {format_currency(goals[index]['current'])} / {format_currency(goals[index]['target'])}")
            else:
                await update.message.reply_text("Índice de meta inválido.")
        except (IndexError, ValueError):
            await update.message.reply_text("Por favor, use o formato: /goal update <número da meta> <valor a adicionar>")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "Aqui estão os comandos disponíveis:\n\n"
        "/add <valor> <categoria> <descrição> - Adicionar uma transação\n"
        "/filter - Filtrar transações por data\n"
        "/delete <número> - Excluir uma transação\n"
        "/balance - Verificar o saldo atual\n"
        "/categories - Gerenciar categorias\n"
        "/categories add <nome> - Adicionar uma nova categoria\n"
        "/categories remove <nome> - Remover uma categoria\n"
        "/report - Gerar relatório mensal\n"
        "/goal - Listar metas de economia\n"
        "/goal add <descrição> <valor alvo> - Adicionar uma meta de economia\n"
        "/goal update <número> <valor> - Atualizar progresso de uma meta\n"
        "/help - Mostrar esta mensagem de ajuda"
    )
    await update.message.reply_text(help_text)

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    if user_id in user_data:
        del user_data[user_id]
        save_user_data()
        await update.message.reply_text("Seus dados foram limpos. Você pode iniciar uma nova conversa usando o comando /start.")
    else:
        await update.message.reply_text("Não há dados para limpar. Você pode iniciar uma nova conversa usando o comando /start.")

def main() -> None:
    load_user_data()
    
    application = Application.builder().token("7864886909:AAE9NMeHk07rhpAfOE0LzXye9UxYZWEUWa8").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add', start_add_transaction)],
        states={
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, amount)],
            CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, category)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, description)],
            DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, date)],
            FILTER_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, filter_date)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("filter", filter_transactions))
    application.add_handler(CommandHandler("delete", delete_transaction))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("categories", categories))
    application.add_handler(CommandHandler("report", report))
    application.add_handler(CommandHandler("goal", goal))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("reset", reset))

    application.run_polling()

if __name__ == '__main__':
    main()
