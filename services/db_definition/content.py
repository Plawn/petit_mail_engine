from typing import TYPE_CHECKING
from pony.orm.core import Optional, PrimaryKey, Set
from pony.orm.ormtypes import Json

from .base import database


class Content(database.Entity):
    id = PrimaryKey(int, auto=True)
    # if the content is rendered
    base_content = Optional('CommonContent', nullable=True)
    data = Optional(Json, nullable=True)

    # if the content is not rendered
    content = Optional(str, nullable=True)
    subject = Optional(str, nullable=True)

    emails = Set('Email', reverse="content")
