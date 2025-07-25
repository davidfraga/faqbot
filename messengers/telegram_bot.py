from fastapi import APIRouter, Request
from starlette.responses import JSONResponse
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

from rag_pipeline.rag_pipeline import run_rag_pipeline  # Seu pipeline RAG
from decouple import config

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from main import CHAT_SETTINGS
    if not CHAT_SETTINGS:
        from core.settings import ChatSettings
        CHAT_SETTINGS = ChatSettings()
    question = update.message.text
    intention = CHAT_SETTINGS.intent_router.run(question)
    print(intention)
    if intention == "agradecimento":
        result = "Eu é que agradeço, tenha uma ótima semana!"
    else:
        result, is_out_of_context = run_rag_pipeline(question=question, qa_chain=CHAT_SETTINGS.qa_chain,
                                                     parser=CHAT_SETTINGS.parser)

    # response, is_out_of_context = run_rag_pipeline(user_message)
    await update.message.reply_text(result)

# Inicializa o bot
application = ApplicationBuilder().token(config("TELEGRAM_TOKEN")).build()
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

telegram_router = APIRouter()

@telegram_router.post("/webhook/telegram")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return JSONResponse(content={"ok": True})

