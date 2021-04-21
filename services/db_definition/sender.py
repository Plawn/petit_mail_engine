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

    def to_json(self):
        return {
            'id': self.id,
            'email': self.email,
            'pending': self.pending,
            'quota': self.quota,
        }

    def deactivate(self):
        """Deactivates a sender by updating it's quota to 0
        """
        self.quota = 0