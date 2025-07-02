from starlette_admin.contrib.mongoengine import Admin, ModelView

from admin.auth import AdminAuthProvider
from admin.view import UserView, ProfileView, ChatStructureView
from models.models import ChatLog, ChatStructure, User

admin = Admin(title="StarsChatAI Administration", auth_provider=AdminAuthProvider())
admin.add_view(UserView(ChatLog ))
admin.add_view(ChatStructureView(ChatStructure))
admin.add_view(ProfileView(User))