from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from data_manager import DataManager

async def categories(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    dm = DataManager()
    user_data = dm.get_user_data(user_id)
    
    if not context.args:
        categories = user_data.get("categories", [])
        await update.message.reply_text(
            f"Suas categorias: {', '.join(categories)}\n\n"
            "Para adicionar uma nova categoria, use: /categories add <nome da categoria>\n"
            "Para remover uma categoria, use: /categories remove <nome da categoria>"
        )
    elif context.args[0] == "add":
        new_category = ' '.join(context.args[1:])
        if "categories" not in user_data:
            user_data["categories"] = []
        if new_category not in user_data["categories"]:
            user_data["categories"].append(new_category)
            dm.set_user_data(user_id, user_data)
            await update.message.reply_text(f"Categoria '{new_category}' adicionada com sucesso.")
        else:
            await update.message.reply_text(f"Categoria '{new_category}' já existe.")
    elif context.args[0] == "remove":
        category_to_remove = ' '.join(context.args[1:])
        if "categories" in user_data and category_to_remove in user_data["categories"]:
            user_data["categories"].remove(category_to_remove)
            dm.set_user_data(user_id, user_data)
            await update.message.reply_text(f"Categoria '{category_to_remove}' removida com sucesso.")
        else:
            await update.message.reply_text(f"Categoria '{category_to_remove}' não encontrada.")
    else:
        await update.message.reply_text("Comando inválido. Use /categories para ver as opções disponíveis.")

categories_handler = CommandHandler("categories", categories)
