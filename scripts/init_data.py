import asyncio
from mongoengine import connect
from decouple import config

from models.models import ChatLog

connect(db=config("MONGO_DB_NAME"), host=config("MONGO_URL"))
collection = ChatLog.objects

async def insert_data():
    docs = [
        {
            "title": "O que é a BSOG?",
            "content": "A BSOG (Brazilian Series of Games) é uma plataforma..."
        },
        {
            "title": "Como faço para participar?",
            "content": "Você deve se cadastrar no site oficial..."
        }
    ]
    await collection.delete_many({})
    await collection.insert_many(docs)
    print("Dados inseridos com sucesso.")

if __name__ == "__main__":
    asyncio.run(insert_data())