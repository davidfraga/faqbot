import datetime
import enum

from bson.errors import InvalidId
from fastapi import HTTPException

from mongoengine import Document, StringField, BooleanField, DateTimeField, ListField, EnumField, DoesNotExist
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Role(str, enum.Enum):
    VIEWER = "viewer"
    ADMIN = "admin"



class ChatLog(Document):
    user_message = StringField(required=True)
    response = StringField()
    out_of_context = BooleanField(default=False)
    timestamp = DateTimeField()

    meta = {
        'collection': 'chat_logs',
        'db_alias': 'default'
    }

class ChatStructure(Document):
    title = StringField(required=True)
    description = StringField(required=True)

    meta = {
        'db_alias': 'default'
    }

class User(Document):
    username = StringField(required=True, unique=True)
    password = StringField(required=True)
    name = StringField(required=True)
    email = StringField(required=False)
    roles = ListField(EnumField(Role), default=[Role.VIEWER])
    active = BooleanField(default=True)
    registered_on = DateTimeField(default=datetime.datetime.now)

    meta = {
        'db_alias': 'default',
        'collection': 'users',
        'indexes': ['username', 'email']
    }

    def validate_password(self, plain_password: str) -> bool:
        return pwd_context.verify(plain_password, self.password)

    def set_password(self, password: str):
        self.password = pwd_context.hash(password)


    def __str__(self):
        return self.name

    @classmethod
    def get_user_by_id(cls, user_id: str):
        """Obter usuário por ID"""
        try:
            user = User.objects(id=user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="Usuário não encontrado")
            return user
        except (DoesNotExist, InvalidId):
            raise HTTPException(status_code=404, detail="Usuário não encontrado")


class Role(str, enum.Enum):
    VIEWER = "viewer"
    ADMIN = "admin"



