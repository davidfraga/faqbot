# 🤖 FAQBot: API Inteligente de Perguntas Frequentes com FastAPI, MongoDB e Groq

[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.14-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-green)](#license)

## 📝 Sobre o Projeto

O **FAQBot** é uma API inteligente desenvolvida com **FastAPI**, **MongoDB** e **Groq**. Ela automatiza respostas relacionadas a perguntas frequentes (FAQs) utilizando o conceito de RAG (**Retriever-Augmented Generation**), tornando as respostas mais precisas ao consultar uma base de conhecimento dinâmica.

Principais funcionalidades:
- **Integração com MongoDB**: Salve e gerencie documentos na base de conhecimento.
- **Starlette-Admin**: Um painel administrativo interativo permite criar, alterar ou excluir documentos diretamente na base de conhecimento, com **impacto instantâneo no RAG**, sem necessidade de reiniciar o serviço.
- **Integração com Telegram**: Um bot conectado via webhook, que responde perguntas diretamente no Telegram.
- **Alta modularidade e configuração simples**: Pronto para ser implantado em produção com Docker e Docker Compose.

---

## ✨ Funcionalidades

- **FastAPI com MongoDB**:
  - Endpoints REST para interação direta.
  - Gerenciamento dinâmico da base de conhecimento.

- **Starlette-Admin**:
  - Interface administrativa simples e poderosa.
  - Permite criar, editar e excluir documentos no **ChatStructure**.
  - Impacto **em tempo real** no pipeline RAG, refletindo mudanças instantaneamente nas respostas.

- **Integração com Telegram**:
  - Webhook configurável para receber perguntas e enviar respostas do FAQBot via bot no Telegram.

- **Suporte a Groq**:
  - Conectividade com a API **Groq** para melhorar a precisão e a geração de respostas inteligentes.

---

## 🚀 Tecnologias Utilizadas

- **[Python 3.13](https://python.org)**: Linguagem principal do projeto.
- **[FastAPI 0.115.14](https://fastapi.tiangolo.com)**: Framework assíncrono para APIs.
- **[MongoDB](https://www.mongodb.com/)**: Banco de dados NoSQL para armazenar documentos da base de conhecimento.
- **[Groq](https://groq.com/)**: API para processamento e geração de linguagem natural.
- **[Starlette-Admin](https://github.com/fastapi-admin/starlette-admin)**: Painel administrativo integrado com suporte ao MongoDB.
- **[Docker & Docker Compose](https://www.docker.com/)**: Containerização para rápida implantação e escalabilidade.

---

## ⚙️ Configuração e Instalação

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/faqbot.git
cd faqbot
```

### 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz projeto e configure as seguintes variáveis:

```env
# Token do seu bot Telegram (obtenha pelo BotFather no Telegram)
TELEGRAM_TOKEN=<INSIRA_SEU_TOKEN_DO_TELEGRAM>

# Chave da API Groq (obtenha em https://groq.com/)
GROQ_API_KEY=<INSIRA_SUA_CHAVE_GROQ>

# Configuração de Conexão com MongoDB (baseado no docker-compose.yml)
MONGO_URL=mongodb://mongodb:27017/faqbot
MONGO_DB_NAME=chat_db
```

### 3. Executar com Docker Compose

Certifique-se de ter o **Docker** e **Docker Compose** instalados no seu sistema. Para iniciar o FAQBot e o MongoDB:

```bash
docker-compose up --build
```

Isso iniciará os seguintes serviços:
- **FastAPI** disponível em: [http://localhost:8000](http://localhost:8000)
- **Starlette-Admin** disponível em: [http://localhost:8000/admin](http://localhost:8000/admin)

---

## 📖 Configurando o Webhook do Telegram

Antes de usar o bot no Telegram, é necessário registrar o webhook para que o Telegram envie as mensagens ao FAQBot.

### Passo 1: Criação do Bot pelo BotFather

1. No Telegram, inicie uma conversa com o [BotFather](https://t.me/BotFather).
2. Use o comando `/newbot` e siga as instruções para criar um novo bot.
3. Você receberá um **TOKEN**, que deve ser configurado no arquivo `.env` como `TELEGRAM_TOKEN`.

### Passo 2: Definindo um DNS para o Webhook

Para testes locais, utilize o **ngrok** para criar um DNS público:
```bash
ngrok http --url=SUA_URL_COM_DNS_AQUI 8000
```

Copie a URL HTTPS fornecida (ex: `https://abc123.ngrok-free.app`) e registre o webhook no Telegram:

```bash
curl -X POST https://api.telegram.org/bot<SEU_TELEGRAM_BOT_TOKEN>/setWebhook \
     -d "url=https://<URL_NGROK>/webhook/telegram"
```

👉 *Substitua `<SEU_TELEGRAM_BOT_TOKEN>` pelo token do BotFather e `<URL_NGROK>` pela URL gerada pelo ngrok.*

---

## 📂 Estrutura do Projeto

```plaintext
faqbot/
├── main.py                      # Ponto de entrada do FastAPI
├── admin/                       # Pacote com arquivos usados pelo Starlette-admin
│   └── admin.py                 
│   └── auth.py
│   └── utils.py
│   └── views.py
├── models/           
│   └── models.py                # Definições dos modelos de dados (Pydantic)
├── core/           
│   └── settings.py              # Instancia das ferramentas da IA (LLM, vector store, chain, prompt)
├── db/           
│   └── db.py                    # Funções para salvar dados no MongoDB
│   └── utils.py                 # Funções para processamento de dados
│   └── vectorstore.py           # Criação e estruturação do vector store
├── messenger/           
│   └── telegram_bot.py          # Handler para tratar mensagens do telegram
├── rag_pipeline/           
│   └── rag_pipeline.py          # Processasmento da RAG
├── serializers/              
│   └── serializers.py           # Lógica de negócio para tratar requests dos endpoints
├── utils/              
│   └── vectorstore_manager.py   # Lógica de Atualização do vector store
├── docker-compose.yml           # Configuração para Docker Compose (FastAPI e MongoDB)
├── .env                         # Variáveis de ambiente
├── requirements.txt             # Dependências do projeto
└── README.md                    # Documentação do projeto
```

---

## 🌐 Endpoints Principais

| Método | Endpoint               | Descrição                                                                 |
|--------|------------------------|---------------------------------------------------------------------------|
| POST   | `/chat`                | Endpoint principal para enviar perguntas e receber respostas.            |
| GET    | `/`                    | Retorna o histórico de conversas armazenado.                            |
| POST   | `/webhook/telegram`    | Webhook para integração com o bot do Telegram.                          |
| GET    | `/admin`               | Interface de administração através do Starlette-Admin.                  |

---

## 🎛️ Starlette-Admin: Gerencie sua Base de Conhecimento

Acesse o painel do **Starlette-Admin** em [http://localhost:8000/admin](http://localhost:8000/admin).

- O painel está configurado para fazer login. Se não tiver uma credencial, Você deve criar um documento 'User' no mongodb
```python
# Exemplo de como pode ser feito

# Executar: docker exec -it <NOME_DA_IMAGEM> python e incluir esse script lá
from models.models import User
from models.models import pwd_context
from mongoengine import connect

connect("default", host="mongodb://mongodb:27017", alias="default")

password = pwd_context.hash("SUA_SENHA_AQUI")
User(username="admin",name="Admin",password=password,roles=['admin']).save()
```
- O painel exibe uma interface para gerenciar os **documentos da base de conhecimento**.
- Atualizações no **ChatStructure** são refletidas **imediatamente** no pipeline de RAG, **sem necessidade de reiniciar o serviço**.
- Funcionalidades de CRUD completas:
  - **Criar documentos:** Adicione novos itens à base de resposta.
  - **Editar documentos existentes:** Atualize informações rapidamente.
  - **Excluir documentos antigos:** Remova itens desatualizados.

---
