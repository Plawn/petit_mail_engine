from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class BaseSendMailBody(BaseModel):
    addresses: List[List[str]]
    from_: str

    class Config:
        fields = {
            'from_': 'from'
        }


class SendPlainMailBody(BaseSendMailBody):
    content: str
    subject: str


class NotificationFragment(BaseModel):
    body: Optional[Dict[str, Any]]
    type: str
    to: List[str]

class SendTemplateMailBody(BaseModel):
    from_: str

    class Config:
        fields = {
            'from_': 'from'
        }

    template_name: str
    fragments: List[NotificationFragment]
    base_data: Dict[str, Any]


class CreateIdentityBody(BaseModel):
    name: str


class CreateSenderBody(BaseModel):
    email: str
    quota: int