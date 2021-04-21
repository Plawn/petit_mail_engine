from pony.orm.core import Optional, PrimaryKey, Required, Set
from pony.orm.ormtypes import Json

from .base import database


class CommonContent(database.Entity):
    id = PrimaryKey(int, auto=True)
    data = Optional(Json, nullable=True)
    linked_contents = Set('Content', reverse="base_content")
    template_name= Required(str)