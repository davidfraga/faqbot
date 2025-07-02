import datetime

from mongoengine import Document, StringField, BooleanField, DateTimeField, ListField, EnumField

from admin.utils import Role

from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
    username = StringField(required=True)
    password = StringField(required=True)
    name = StringField(required=True)
    email = StringField(required=False)
    roles = ListField(EnumField(Role), default=[Role.VIEWER])
    active = BooleanField(default=True)
    registered_on = DateTimeField(default=datetime.datetime.now)

    meta = {
        'db_alias': 'default'
    }

    def verify_password(self, plain_password: str) -> bool:
        return pwd_context.verify(plain_password, self.password)


    def __str__(self):
        return self.name



