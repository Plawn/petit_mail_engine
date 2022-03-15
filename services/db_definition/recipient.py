from pony.orm.core import PrimaryKey, Required, Set
from .base import database



class Recipient(database.Entity):
    """The point of this entity is to store efficiently the recipient of all 
    emails and reuse the entities when sending another email to a given recipient
    
    This will make the tracking of analytics easier in the future
    """
    id = PrimaryKey(int, auto=True)
    
    """The email of the recipient
    """
    email: str = Required(str)
    emails = Set('Email', reverse="recipient")