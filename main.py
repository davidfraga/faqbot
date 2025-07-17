import os
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, Request, Query
from mongoengine import connect, Q, ConnectionFailure
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import JSONResponse
from telegram import Update

from core.settings import ChatSettings
from models.models import ChatLog
from serializers.serializers import UserMessage, ChatLogOut
from admin.admin import admin
from starlette.middleware.base import BaseHTTPMiddleware

class HTTPSRedirectMiddlewareCustom(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Rewrite the scheme to https (forcing URLs to be HTTPS)
        request.scope["scheme"] = "https"
        response = await call_next(request)
        return response

CHAT_SETTINGS: Optional[ChatSettings] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Função de lifespan que torna a conexão com o banco de dados opcional,
    permitindo um build limpo e genérico da imagem Docker.
    """
    global CHAT_SETTINGS
    
    mongo_url = os.getenv("MONGO_URL")
    
    # Apenas tenta conectar e inicializar se a MONGO_URL foi fornecida.
    if mongo_url:
        print(f"INFO: MONGO_URL encontrada. Tentando conectar ao banco de dados...")
        try:
            # Usa as variáveis de ambiente para a conexão.
            db_name = os.getenv("MONGO_DB_NAME", "chat_dbbo")
            connect(db=db_name, host=mongo_url, alias="default")
            
            # Se a conexão for bem-sucedida, inicializa os componentes da aplicação.
            CHAT_SETTINGS = ChatSettings()
            
            from messenger.telegram_bot import application
            await application.initialize()
            app.state.bot_app = application

            print("INFO:     Conexão com o banco e inicialização da aplicação concluídas com sucesso.")

        except ConnectionFailure as e:
            print(f"ERRO CRÍTICO: Falha ao conectar ao MongoDB. A aplicação pode não funcionar corretamente. Erro: {e}")
        except Exception as e:
            print(f"ERRO CRÍTICO: Falha inesperada durante a inicialização. Erro: {e}")
    
    else:
        # Se MONGO_URL não for encontrada, a aplicação inicia sem conexão com o banco.
        print("AVISO: MONGO_URL não definida. Aplicação iniciando sem conexão com o banco de dados (ideal para ambiente de build).")

    yield
    
    # Lógica de finalização (shutdown)
    if hasattr(app.state, 'bot_app'):
        print("INFO: Finalizando aplicação do bot do Telegram...")
        await app.state.bot_app.stop()
        await app.state.bot_app.shutdown()
    
    print("INFO: Aplicação finalizada.")

app = FastAPI(lifespan=lifespan)

# app.add_middleware(HTTPSRedirectMiddlewareCustom)
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY", "sua_chave_super_secreta_padrao"))
admin.mount_to(app)

@app.post("/webhook/telegram")
async def telegram_webhook(req: Request):
    from messenger.telegram_bot import application
    data = await req.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return JSONResponse(content={"ok": True})

@app.get("/", response_model=List[ChatLogOut])
def get_history(limit: int = Query(20, ge=1, le=100), search: Optional[str] = None):
    query = ChatLog.objects
    if search:
        query = query.filter(Q(user_message__icontains=search) | Q(response__icontains=search))
    return [
        {"user_message": log.user_message, "response": log.response}
        for log in query.order_by('-id')[:limit]
    ]

@app.post("/chat")
async def chat(message: UserMessage):
    global CHAT_SETTINGS
    if not CHAT_SETTINGS:
        raise HTTPException(status_code=503, detail="Serviço indisponível. Falha na inicialização com a base de dados.")
    from rag_pipeline.rag_pipeline import run_rag_pipeline
    response, out_of_context = run_rag_pipeline(message.question, CHAT_SETTINGS.qa_chain, CHAT_SETTINGS.parser)
    return {"response": response, "out_of_context": out_of_context}

# OLD VERSION
"""
from contextlib import asynccontextmanager
from typing import Optional, List

from fastapi import FastAPI, Request, Query


from core import ChatSettings
from db.db import save_conversation
from models import ChatLog
from serializers import UserMessage, ChatLogOut
from fastapi.responses import JSONResponse
from telegram import Update

from decouple import config

from mongoengine import connect, Q
from starlette.middleware.sessions import SessionMiddleware

CHAT_SETTINGS = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    connect(db=config("MONGO_DB_NAME"), host=config("MONGO_URL"), alias="default")
    global CHAT_SETTINGS
    CHAT_SETTINGS = ChatSettings()
    from messenger.telegram_bot import application
    await application.initialize()
    await application.start()
    # Armazena o bot na instância do app (ou global, se preferir)
    app.state.bot_app = application

    yield

    # Encerra ao desligar
    await application.stop()
    await application.shutdown()

app = FastAPI(lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key="c36e6b10e20846ce8856dde2b13ef3642231878d48230c784241e4741305a4c1")
from admin.admin import admin
admin.mount_to(app)


@app.post("/webhook/telegram")
async def telegram_webhook(req: Request):
    from messenger.telegram_bot import application
    data = await req.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return JSONResponse(content={"ok": True})

@app.get("/", response_model=List[ChatLogOut])
def get_history(
    limit: int = Query(20, ge=1, le=100),
    out_of_context: Optional[bool] = None,
    search: Optional[str] = None
):
    query = ChatLog.objects

    if out_of_context is not None:
        query = query.filter(out_of_context=out_of_context)
    if search:
        query = query.filter(
            Q(user_message__icontains=search) | Q(response__icontains=search)
        )

    query = query.order_by('-id').limit(limit)

    return [
        {
            "user_message": log.user_message,
            "response": log.response,
            "out_of_context": log.out_of_context
        }
        for log in query
    ]

@app.post("/chat")
async def chat(message: UserMessage):
    from rag_pipeline import run_rag_pipeline
    global CHAT_SETTINGS
    question = message.question

    intention = CHAT_SETTINGS.intent_router.run(question)
    print(intention)
    if intention == "agradecimento":
        result = "Eu é que agradeço, tenha uma ótima semana!"
        is_out_of_context = True
    else:
        result, is_out_of_context = run_rag_pipeline(question=question, retriever=CHAT_SETTINGS.qa_chain,
                                                     parser=CHAT_SETTINGS.parser)

    save_conversation(question, result, is_out_of_context)

    return {"response": result, "out_of_context": is_out_of_context}

@app.post("/remake_db")
async def remake_db():
    global CHAT_SETTINGS
    CHAT_SETTINGS = ChatSettings()
    return {}


"""