from decouple import config
from starlette.requests import Request
from starlette.responses import Response
from starlette_admin.exceptions import FormValidationError, LoginFailed
from starlette_admin.auth import AdminConfig, AdminUser, AuthProvider
import jwt
from admin.utils import create_access_token
from models.models import User

class AdminAuthProvider(AuthProvider):

    async def login(
            self,
            username: str,
            password: str,
            remember_me: bool,
            request: Request,
            response: Response,
    ) -> Response:
        if len(username) < 3:
            # Form data validation
            raise FormValidationError(
                {"username": "Ensure username has at least 03 characters"}
            )
        user = User.objects(username=username).first()
        if user and user.validate_password(password):
            # Cria o token JWT
            user_roles = [role.value for role in user.roles]
            access_token = create_access_token(data={"sub": user.username, "roles": user_roles})
            # Save username in session
            request.session.update({"username": username, "access_token": access_token})
            request.state.user = user

            return response

        raise LoginFailed("Invalid username or password")


    async def logout(self, request: Request, response: Response) -> Response:
        """
        Limpa o cookie de autenticação.
        """
        request.session.clear()
        return response

    async def is_authenticated(self, request: Request) -> bool:
        """
        Verifica a cada requisição se o usuário está autenticado.
        """
        token = request.session.get("access_token")
        if not token:
            return False

        try:
            # Remove o prefixo "Bearer "
            #token = token.split(" ")[1]
            payload = jwt.decode(token, config("JWT_SECRET_KEY"), algorithms=[ALGORITHM])
            # Armazena o payload no estado da requisição para uso posterior (ex: autorização)
            request.state.user_payload = payload
            request.state.user = User.objects(username=payload["sub"]).first()
            return True
        except jwt.PyJWTError:
            return False

    async def get_display_name(self, request: Request) -> str:
        """
        Exibe o nome do usuário no topo da página do admin.
        """
        try:
            if hasattr(request.state, "user_payload"):
                return request.state.user_payload.get("sub", "")
            return "Usuário"
        except AttributeError as e:
            if await self.is_authenticated(request):
                return await self.get_display_name(request)
            raise e

    async def get_admin_config(self, request: Request) -> AdminConfig:
        try:
            user = request.state.user  # Retrieve current user
            # Update app title according to current_user
            custom_app_title = "Hello, " + user.name + "!"
            # Update logo url according to current_user
            custom_logo_url = None
            return AdminConfig(
                app_title=custom_app_title,
            )
        except AttributeError as e:
            if await self.is_authenticated(request):
                return await self.get_admin_config(request)
            raise e

    async def get_admin_user(self, request: Request) -> AdminUser:
        try:
            user = request.state.user  # Retrieve current user
            return AdminUser(username=user.name)
        except AttributeError as e:
            if await self.is_authenticated(request):
                return await self.get_admin_user(request)
            raise e

