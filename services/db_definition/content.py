from typing import TYPE_CHECKING
from pony.orm.core import Optional, PrimaryKey, Set
from pony.orm.ormtypes import Json

from .base import database


class Content(database.Entity):
    """The content of an email

    If this entity contains a non-null content, it will be considered as a plain email
    otherwise the worker will attempt to render the email using the data contained in the data field and the base_content entity
    """
    id = PrimaryKey(int, auto=True)
    # if the content is rendered
    base_content = Optional('CommonContent', nullable=True)
    data = Optional(Json, nullable=True)

    # if the content is not rendered
    content = Optional(str, nullable=True)
    subject = Optional(str, nullable=True)

    emails = Set('Email', reverse="content")
