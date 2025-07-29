import os
from contextlib import asynccontextmanager
from typing import List, Optional

import starlette_admin
from fastapi import FastAPI, Query, HTTPException
from mongoengine import connect, Q, ConnectionFailure
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles

from admin.routes import admin_router
from core.settings import ChatSettings
from messengers.telegram_bot import telegram_router
from models.models import ChatLog
from serializers.serializers import UserMessage, ChatLogOut
from admin.admin import create_admin
from starlette.middleware.base import BaseHTTPMiddleware

from dotenv import load_dotenv
load_dotenv()

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

            from messengers.telegram_bot import application
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

app.add_middleware(SessionMiddleware, secret_key="sua_chave_super_secreta")
app.add_middleware(SessionMiddleware, secret_key="sua_chave_super_secreta")
app.mount("/static", StaticFiles(directory="static"), name="static")
starlette_admin_static_dir = os.path.join(os.path.dirname(starlette_admin.__file__), "statics")
app.mount("/admin/statics", StaticFiles(directory=starlette_admin_static_dir), name="admin:statics")

# Rotas da API
app.include_router(admin_router)
app.include_router(telegram_router)
admin = create_admin(app)



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

