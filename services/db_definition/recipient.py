from pony.orm.core import PrimaryKey, Required, Set
from .base import database



class Recipient(database.Entity):
    id = PrimaryKey(int, auto=True)
    email = Required(str)
    emails = Set('Email', reverse="recipient")