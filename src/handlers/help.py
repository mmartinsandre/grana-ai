from telegram import Update
from telegram.ext import ContextTypes

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "Aqui estão os comandos disponíveis:\n\n"
        "/adicionar - Adicionar uma transação\n"
        "/filtrar - Filtrar transações por data\n"
        "/excluir - Excluir uma transação\n"
        "/saldo - Verificar o saldo atual\n"
        "/categorias - Gerenciar categorias\n"
        "/relatorio - Gerar relatório mensal\n"
        "/meta - Definir uma meta de economia\n"
        "/recorrente - Adicionar transação recorrente\n"
        "/orcamento - Definir orçamento\n"
        "/investir - Adicionar investimento\n"
        "/moeda - Definir moeda preferida\n"
        "/analise - Ver análise de gastos\n"
        "/ajuda - Mostrar esta mensagem de ajuda\n"
        "/resetar - Resetar todos os seus dados"
    )
    await update.message.reply_text(help_text)
