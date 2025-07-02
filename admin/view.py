from typing import Any, Dict, Optional, Sequence

from starlette_admin.contrib.mongoengine import ModelView
from starlette.requests import Request

import main
from admin.utils import Role
import mongoengine as me
import starlette_admin.fields as sa
from mongoengine.base import BaseDocument

from utils.vectorstore_manager import schedule_vectorstore_update

from models.models import pwd_context
from bson import ObjectId

class UserView(ModelView):

    def can_create(self, request: Request) -> bool:
        return False

    def can_edit(self, request: Request) -> bool:
        return False

    def can_delete(self, request: Request) -> bool:
        return False

class ProfileView(ModelView):
    def is_accessible(self, request: Request) -> bool:
        return Role.ADMIN in request.state.user.roles

    async def _populate_obj(  # noqa: C901
            self,
            request: Request,
            obj: me.Document,
            data: Dict[str, Any],
            is_edit: bool = False,
            document: Optional[BaseDocument] = None,
            fields: Optional[Sequence[sa.BaseField]] = None,
    ) -> me.Document:
        if not is_edit or not obj.password == data.get("password"):
            data['password'] = pwd_context.hash(data['password'])
        return await super()._populate_obj(request,obj, data,is_edit,document, fields)

class ChatStructureView(ModelView):
    fields = [
        "id",
        "title",
        sa.TextAreaField("description", maxlength=1000,rows=4)
    ]
    async def after_create(self, request: Request, obj: Any) -> None:
        await schedule_vectorstore_update()
        await super().after_create(request, obj)

    async def after_edit(self, request: Request, obj: Any) -> None:
        await schedule_vectorstore_update()
        await super().after_edit(request, obj)

    async def after_delete(self, request: Request, obj: Any) -> None:
        await schedule_vectorstore_update()
        await super().after_delete(request, obj)

    def serialize_field_value(self, value, field_name: str):
        if isinstance(value, ObjectId):
            return str(value)
        return value