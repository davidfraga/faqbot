from typing import Optional

from pydantic import BaseModel

class UserMessage(BaseModel):
    question: str

class ChatLogOut(BaseModel):
    user_message: str
    response: Optional[str]
    out_of_context: bool