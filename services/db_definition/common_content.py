from pony.orm.core import Optional, PrimaryKey, Required, Set
from pony.orm.ormtypes import Json

from .base import database


class CommonContent(database.Entity):
    """The content which can be shared between emails

    This is always connected to a given `Content`
    """
    id = PrimaryKey(int, auto=True)
    data = Optional(Json, nullable=True)
    linked_contents = Set('Content', reverse="base_content")
    template_name= Required(str)