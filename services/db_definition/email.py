import datetime
import uuid

from pony.orm.core import Optional, PrimaryKey, Required, Set
from pony.orm import Set
from .base import database


class Email(database.Entity):
    """Represents a given email sent to a set a recipient

    It contains all the required data to send a valid email
    """
    id = PrimaryKey(int, auto=True)
    callback_uid = Required(uuid.UUID, default=uuid.uuid4)
    created_at = Required(datetime.datetime, sql_default='CURRENT_TIMESTAMP')
    
    """For monitoring purposes, we can measure how much time elapsed between the schedule and the send event
    """
    sent_at = Optional(datetime.datetime)


    """From field of the mail
    """
    from_ = Required(str)
    """Identity sending the email, an identity will most likely use multiple senders
    """
    identity = Required('Identity', reverse="emails")
    """
    The actual sender used to send this email, the schedule is done on 
    the front end directly to avoid complications on the worker
    """
    sender = Required('Sender', reverse="emails")
    
    """Set of recipient, whom'll receive the email
    """
    recipient = Set('Recipient', reverse="emails")
    
    """The actual content of the email
    """
    content = Required('Content', reverse="emails")
