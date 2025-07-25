from starlette_admin.contrib.mongoengine import Admin

from admin.auth import AdminAuthProvider
from admin.view import UserView, ChatStructureView, ProfileAdminView, get_templates, ChatLogAdminView
from models.models import ChatLog, ChatStructure, User

def create_admin(app):
    admin = Admin(
        title="BSOG Bot Administration",
        logo_url="/static/logo.png",
        login_logo_url="/static/logo.png",
        auth_provider=AdminAuthProvider(),
    )

    admin.add_view(UserView(User))
    admin.add_view(ProfileAdminView(label="Perfil"))
    admin.add_view(ChatStructureView(ChatStructure))
    admin.add_view(ChatLogAdminView(ChatLog))

    # Montar o admin primeiro para ter acesso às suas funções
    admin.mount_to(app)

    get_templates(admin)

    return admin
