from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.security import HTTPBearer
from starlette.requests import Request
from starlette.responses import RedirectResponse

from admin.utils import get_current_user
from models.models import User
from mongoengine.errors import ValidationError

admin_router = APIRouter(prefix="/admin", tags=["admin"])
security = HTTPBearer()

@admin_router.post("/change-password/{user_id}", name="change_password_form")
async def change_password_form(
        request: Request,
        user_id: str,
        current_password: str = Form(...),
        new_password: str = Form(...),
        confirm_password: str = Form(...),
        current_user: User = Depends(get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/admin/login", status_code=302)
    # Verificar se é o próprio usuário ou admin
    if str(current_user.id) != user_id and not "admin" in current_user.roles:
        raise HTTPException(status_code=403, detail="Acesso negado")

    user = User.get_user_by_id(user_id)

    # Validar senha atual (apenas se não for admin alterando senha de outro usuário)
    if str(current_user.id) == user_id:
        if not user.validate_password(current_password):
            request.session["error_message"] = "Senha atual incorreta"
            return RedirectResponse(
                url=f"/admin/change-password/{user_id}",
                status_code=302
            )

    # Validar confirmação de senha
    if new_password != confirm_password:
        request.session["error_message"] = "As senhas não coincidem"
        return RedirectResponse(
            url=f"/admin/change-password/{user_id}",
            status_code=302
        )

    # Validar tamanho mínimo da senha
    if len(new_password) < 8:
        request.session["error_message"] = "A senha deve ter pelo menos 8 caracteres"
        return RedirectResponse(
            url=f"/admin/change-password/{user_id}",
            status_code=302
        )

    try:
        # Alterar senha
        user.set_password(new_password)
        user.save()

        request.session["success_message"] = "Senha alterada com sucesso!"

        # Se for o próprio usuário, redirecionar para perfil
        if str(current_user.id) == user_id:
            return RedirectResponse(
                url="/admin/profile",
                status_code=302
            )
        else:
            # Se for admin alterando outro usuário, voltar para lista
            return RedirectResponse(
                url="/admin/user/list",
                status_code=302
            )

    except ValidationError as e:
        request.session["error_message"] = f"Erro de validação: {str(e)}"
        return RedirectResponse(
            url=f"/admin/change-password/{user_id}",
            status_code=302
        )
    except Exception as e:
        request.session["error_message"] = f"Erro interno: {str(e)}"
        return RedirectResponse(
            url=f"/admin/change-password/{user_id}",
            status_code=302
        )


@admin_router.get("/change-password/{user_id}", name="change_password_page")
async def change_password_page(
        request: Request,
        user_id: str,
        current_user: User = Depends(get_current_user)
):
    from admin.view import templates_global as templates
    from admin.forms import ChangePasswordForm
    if not current_user:
        return RedirectResponse(url=f"/admin/login?next={request.url}", status_code=302)
    # Verificar permissões
    if str(current_user.id) != user_id and not "admin" in current_user.roles:
        raise HTTPException(status_code=403, detail="Acesso negado")

    user = User.get_user_by_id(user_id)
    form = ChangePasswordForm()

    # Determinar se é o próprio usuário ou admin alterando outro
    is_own_password = str(current_user.id) == user_id

    return templates.TemplateResponse(
        "change_password.html",
        {
            "request": request,
            "form": form,
            "user": user,
            "user_id": user_id,
            "is_own_password": is_own_password,
            "page_title": f"Alterar Senha - {user.username}",
            "error_message": request.session.pop("error_message", None),
            "success_message": request.session.pop("success_message", None),
            "admin_title": "Painel Administrativo",
            "current_user": current_user,
        }
    )


@admin_router.get("/profile/change-password", name="profile_change_password")
async def change_own_password(
        request: Request,
        current_user: User = Depends(get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/admin/login", status_code=302)
    return RedirectResponse(
        url=f"/admin/change-password/{str(current_user.id)}",
        status_code=302
    )


@admin_router.get("/profile", name="profile")
async def user_profile(
        request: Request,
        current_user: User = Depends(get_current_user)
):
    from admin.view import templates_global as templates
    if not current_user:
        return RedirectResponse(url="/admin/login", status_code=302)
    return templates.TemplateResponse(
        "admin/profile.html",
        {
            "request": request,
            "user": current_user,
            "page_title": "Meu Perfil",
            "admin_title": "Painel Administrativo",
            "current_user": current_user,
        }
    )


@admin_router.post("/logout", name="admin:logout_post")
async def admin_logout_post(request: Request):
    request.session.clear()
    return RedirectResponse(url="/admin/login", status_code=302)

@admin_router.get("/logout", name="admin:logout")
async def admin_logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/admin/login", status_code=302)