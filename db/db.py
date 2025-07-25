# fastapi_app/db.py
from datetime import datetime, UTC
from typing import List, Optional
from models.models import ChatLog, ChatStructure


def save_conversation(user_message: str, response: str, out_of_context: bool = False) -> None:
    """
    Salva um registro da conversa no banco de dados (ChatLog).

    Args:
        user_message (str): A mensagem enviada pelo usuário.
        response (str): A resposta gerada pelo sistema.
        out_of_context (bool, optional): Indica se a mensagem está fora de contexto. Default é False.
    """
    ChatLog(
        user_message=user_message,
        response=response,
        out_of_context=out_of_context,
        timestamp=datetime.now(UTC),
    ).save()


def get_conversations(limit: int = 10, out_of_context: Optional[bool] = None) -> List[ChatLog]:
    """
    Retorna as conversas mais recentes com base nos parâmetros fornecidos.

    Args:
        limit (int, optional): Número máximo de registros a retornar. Default é 10.
        out_of_context (bool, optional): Filtro por mensagens fora de contexto.

    Returns:
        List[ChatLog]: Lista de objetos ChatLog.
    """
    query = ChatLog.objects.order_by('-timestamp')
    if out_of_context is not None:
        query = query.filter(out_of_context=out_of_context)
    return query[:limit]



