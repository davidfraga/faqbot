import asyncio

import main
from db.vectorstore import build_vectorstore
from core.settings import ChatSettings

update_queue = asyncio.Queue()

async def schedule_vectorstore_update():
    await update_queue.put(1)
    await asyncio.sleep(1)
    while not update_queue.empty():
        _ = await update_queue.get()
    settings = ChatSettings()
    main.CHAT_SETTINGS = settings
    print("[INFO] Vetorstore atualizado.")