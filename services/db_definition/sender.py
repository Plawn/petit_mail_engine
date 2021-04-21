from pony.orm.core import PrimaryKey, Required, Set
from pony.orm.ormtypes import Json
from .base import database



class Sender(database.Entity):
    id = PrimaryKey(int, auto=True)
    email = Required(str)
    pending = Required(int, default=0)
    identity = Required('Identity', reverse="senders")
    emails = Set('Email', reverse="sender")
    credentials = Required(Json)
    quota = Required(int)