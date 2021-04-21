from typing import List

from pony.orm.core import PrimaryKey, Required, Set

from .base import database


class Identity(database.Entity):
    id = PrimaryKey(int, auto=True)
    emails = Set('Email', reverse="identity")
    senders = Set('Sender', reverse="identity")
    name = Required(str)




    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'senders': [s.to_json() for s in self.senders],
        }