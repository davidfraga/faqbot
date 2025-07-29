from typing import Any

from starlette.templating import Jinja2Templates
from starlette_admin import CustomView, action
from starlette_admin.contrib.mongoengine import ModelView
from starlette.requests import Request
from starlette.responses import RedirectResponse

import starlette_admin.fields as sa

from rag_pipeline.vectorstore_manager import schedule_vectorstore_update

from models.models import User, ChatStructure

templates_global = None


def get_templates(admin):
    templates_jinja = Jinja2Templates(env=admin.templates.env)
    global templates_global
    templates_global = templates_jinja


class UserView(ModelView):
    model = User
    identity = "user"
    name = "Usuários"
    label = "Usuários"
    icon = "fa fa-users"

    fields = ["id", "username", "email", "active", "roles", "registered_on"]
    fields_default_sort = ["-registered_on"]
    exclude_fields_from_list = ["password"]
    exclude_fields_from_detail = ["password"]
    exclude_fields_from_create = ["password", "registered_on"]
    exclude_fields_from_edit = ["password", "registered_on"]


    # Adicionar ações personalizadas
    @action(
        name="change_password",
        text="Alterar Senha",
        confirmation="Deseja alterar a senha deste usuário?",
        submit_btn_text="Sim, alterar",
        submit_btn_class="btn btn-success",
        icon_class="fas fa-key",
        custom_response=True
    )
    async def change_password_action(self, request: Request, pks: list[str]):
        """Ação para alterar senha do usuário"""
        if len(pks) != 1:
            request.session["error"] = "Selecione apenas um usuário"
            return RedirectResponse(url=request.url_for("admin:list", identity=self.identity))

        user_id = pks[0]
        return RedirectResponse(
            url=f"/admin/change-password/{user_id}",
            status_code=302
        )

    def can_create(self, request: Request) -> bool:
        return False

    def can_edit(self, request: Request) -> bool:
        return False

    def can_delete(self, request: Request) -> bool:
        return False

class ProfileAdminView(CustomView):
    identity = "profile"
    name = "Meu Perfil"
    label = "Perfil"
    icon = "fa fa-user"
    template = "profile.html"

    async def render(self, request: Request, templates):
        user = request.state.user

        return templates.TemplateResponse(
            self.template,
            {
                "request": request,
                "user": user,
                "page_title": "Meu Perfil",
                "admin_title": "Painel Administrativo",
                "current_user": user,
            }
        )


class ChatStructureView(ModelView):
    fields = [
        "id",
        "title",
        sa.TextAreaField("description", maxlength=1000,rows=4)
    ]
    model=ChatStructure
    async def after_create(self, request: Request, obj: Any) -> None:
        await schedule_vectorstore_update()
        await super().after_create(request, obj)

    async def after_edit(self, request: Request, obj: Any) -> None:
        await schedule_vectorstore_update()
        await super().after_edit(request, obj)

    async def after_delete(self, request: Request, obj: Any) -> None:
        await schedule_vectorstore_update()
        await super().after_delete(request, obj)



class ChatLogAdminView(ModelView):
    fields = ['id','user_message','response','out_of_context','timestamp']

    def can_create(self, request: Request) -> bool:
        return False

    def can_edit(self, request: Request) -> bool:
        return False

    def can_delete(self, request: Request) -> bool:
        return False