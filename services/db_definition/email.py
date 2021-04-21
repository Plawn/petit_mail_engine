import datetime
import uuid

from pony.orm.core import Optional, PrimaryKey, Required, Set
from pony.orm import Set
from .base import database


class Email(database.Entity):
    id = PrimaryKey(int, auto=True)
    callback_uid = Required(uuid.UUID, default=uuid.uuid4)
    created_at = Required(datetime.datetime, sql_default='CURRENT_TIMESTAMP')
    sent_at = Optional(datetime.datetime)

    from_ = Required(str)
    identity = Required('Identity', reverse="emails")
    sender = Required('Sender', reverse="emails")
    
    recipient = Set('Recipient', reverse="emails")
    content = Required('Content', reverse="emails")
