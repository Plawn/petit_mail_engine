import itertools
from fastapi import APIRouter, Response

from ...db_definition import CommonContent, Content, db_session
from . import utils
from .dto import SendPlainMailBody, SendTemplateMailBody

router = APIRouter()


@router.post('/{identity}/html')
@db_session
def send_mail_html(identity: str, body: SendTemplateMailBody):
    # todo, fix
    # content has the "all" key where the data can be used for each mail rendering
    base_content = CommonContent(
        template_name=body.template_name,
        data=body.base_data
    )
    if body.data is not None and len(body.data) > 0:    
        # means that we have the same amount of data as email to render
        content = []
        default_content = Content(base_content=base_content)
        used_default = False
        for key in range(len(body.addresses)):
            # we have a json object here so even number keys are strings
            d = body.data.get(str(key))
            if d is not None:
                content.append(Content(base_content=base_content, data=d))
            else:
                used_default = True
                # we reuse the exact same entity to avoid data duplication
                content.append(default_content)
        if not used_default:
            # avoid creating a useless entity
            del default_content
    else:
        # reuse the exact same data for every render
        content = itertools.cycle([Content(base_content=base_content)])
    utils.send_mail(identity, content, body.from_, body.addresses)


@router.post('/{identity}/plain')
@db_session
def send_mail_plain(identity: str, body: SendPlainMailBody):
    content = [Content(
        content=body.content,
        subject=body.subject
    )]
    utils.send_mail(identity, itertools.cycle(content), body.from_, body.addresses)


