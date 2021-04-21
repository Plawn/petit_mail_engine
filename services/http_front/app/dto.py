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
    data: Optional[List[Dict[str, Any]]]
    base_data: Dict[str, Any]