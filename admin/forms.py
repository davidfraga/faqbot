from wtforms import Form, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo


class ChangePasswordForm(Form):
    current_password = PasswordField(
        'Senha Atual',
        validators=[DataRequired(message="Campo obrigatório")]
    )
    new_password = PasswordField(
        'Nova Senha',
        validators=[
            DataRequired(message="Campo obrigatório"),
            Length(min=8, message="A senha deve ter pelo menos 8 caracteres")
        ]
    )
    confirm_password = PasswordField(
        'Confirmar Nova Senha',
        validators=[
            DataRequired(message="Campo obrigatório"),
            EqualTo('new_password', message="As senhas não coincidem")
        ]
    )
