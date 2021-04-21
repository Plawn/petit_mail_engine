from typing import List

from pony.orm.core import PrimaryKey, Required, Set

from .base import database


class Identity(database.Entity):
    id = PrimaryKey(int, auto=True)
    
    emails = Set('Email', reverse="identity")
    
    """All the email accounts used in order to send more than the maximum per account
    """
    senders = Set('Sender', reverse="identity")
    
    """Name used in order to differentiate all identities

    - business
        - business01@example.com
        - business02@example.com
    - legal
        - legal01@example.com
        - legal02@example.com
    """
    name = Required(str)




    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'senders': [s.to_json() for s in self.senders],
        }