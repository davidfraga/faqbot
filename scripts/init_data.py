import asyncio
from mongoengine import connect
from decouple import config

from models.models import User, pwd_context, Role

connect(db=config("MONGO_DB_NAME"), host=config("MONGO_URL"))


async def insert_data():
    # Criação de um admin padrão
    if (config("ADMIN_INITIAL_USERNAME") and config("ADMIN_INITIAL_PASSWORD") and
            not User.objects(username=config("ADMIN_INITIAL_USERNAME")).first()):
        User(username=config("ADMIN_INITIAL_USERNAME"), password=pwd_context.hash(config("ADMIN_INITIAL_PASSWORD")),
             name="Admin", email="email@email.com", roles=[Role.ADMIN]).save()
        print("usuário ADMIN criado com sucesso.")
    else:
        print("NADA ALTERADO para o usuário ADMIN.")

if __name__ == "__main__":
    asyncio.run(insert_data())