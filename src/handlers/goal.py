from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from data_manager import DataManager

async def goal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    dm = DataManager()
    user_data = dm.get_user_data(user_id)
    if not context.args:
        goals = user_data.get("goals", [])
        if goals:
            message = "Suas metas de economia:\n"
            for i, g in enumerate(goals):
                message += f"{i+1}. {g['description']}: {g['current']:.2f} / {g['target']:.2f}\n"
            await update.message.reply_text(message)
        else:
            await update.message.reply_text("Você não tem metas de economia definidas. Use /goal add <descrição> <valor alvo> para adicionar uma.")
    elif context.args[0] == "add":
        try:
            description = ' '.join(context.args[1:-1])
            target = float(context.args[-1].replace(',', '.'))
            if "goals" not in user_data:
                user_data["goals"] = []
            user_data["goals"].append({
                "description": description,
                "target": target,
                "current": 0
            })
            dm.set_user_data(user_id, user_data)
            await update.message.reply_text(f"Meta adicionada: {description} - Alvo: {target:.2f}")
        except (IndexError, ValueError):
            await update.message.reply_text("Por favor, use o formato: /goal add <descrição> <valor alvo>")
    elif context.args[0] == "update":
        try:
            index = int(context.args[1]) - 1
            amount = float(context.args[2].replace(',', '.'))
            goals = user_data.get("goals", [])
            if 0 <= index < len(goals):
                goals[index]["current"] += amount
                dm.set_user_data(user_id, user_data)
                await update.message.reply_text(f"Meta atualizada: {goals[index]['description']} - Progresso: {goals[index]['current']:.2f} / {goals[index]['target']:.2f}")
            else:
                await update.message.reply_text("Índice de meta inválido.")
        except (IndexError, ValueError):
            await update.message.reply_text("Por favor, use o formato: /goal update <número da meta> <valor a adicionar>")

goal_handler = CommandHandler("goal", goal)
