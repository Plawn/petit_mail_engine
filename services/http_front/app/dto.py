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


class SendTemplateMailBody(BaseSendMailBody):
    template_name: str
    data: Optional[Dict[str, Any]]
    base_data: Dict[str, Any]


class CreateIdentityBody(BaseModel):
    name: str


class CreateSenderBody(BaseModel):
    email: str
    quota: int