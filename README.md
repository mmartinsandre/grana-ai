# Pataco - Assistente Financeiro Telegram Bot

Pataco é um bot do Telegram projetado para ajudar os usuários a gerenciar suas finanças pessoais. Ele oferece uma variedade de funcionalidades, incluindo rastreamento de transações, orçamentos, metas financeiras e relatórios.

## Funcionalidades

- Adicionar transações
- Filtrar transações por data
- Excluir transações
- Verificar saldo atual
- Gerenciar categorias de gastos
- Gerar relatórios mensais
- Definir metas de economia
- Adicionar transações recorrentes
- Definir orçamentos
- Adicionar investimentos
- Definir moeda preferida
- Análise de gastos

## Requisitos

- Python 3.9+
- Bibliotecas Python listadas em `requirements.txt`

## Configuração

1. Clone este repositório:
   ```
   git clone https://github.com/seu-usuario/pataco-bot.git
   cd pataco-bot
   ```

2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

3. Crie um arquivo `.env` na raiz do projeto e adicione seu token do bot do Telegram:
   ```
   TELEGRAM_TOKEN=seu_token_aqui
   ```

4. Execute o bot:
   ```
   python src/main.py
   ```

## Uso

Inicie uma conversa com o bot no Telegram e use o comando `/ajuda` para ver a lista completa de comandos disponíveis.

## Implantação

Este bot pode ser implantado em várias plataformas. Instruções detalhadas para implantação no Heroku estão incluídas nos comentários do código.

## Contribuindo

Contribuições são bem-vindas! Por favor, sinta-se à vontade para submeter um Pull Request.

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.
