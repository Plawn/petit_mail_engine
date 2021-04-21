from typing import Dict

from .senders.sender_identity import EmailSender
from .template_db import TemplateDB


class Context():
    senders_db: Dict[str, EmailSender]
    template_db: TemplateDB
