from fastapi import APIRouter, Response

from ...db_definition import CommonContent, Content, db_session
from . import utils
from .dto import SendPlainMailBody, SendTemplateMailBody

router = APIRouter()


@router.post('/send/{identity}/html')
@db_session
def send_mail_html(identity: str, body: SendTemplateMailBody):
    # todo, fix
    # content has the "all" key where the data can be used for each mail rendering
    base_content = CommonContent(
        template_name=body.template_name,
        data=body.base_data
    )
    if body.data is not None and len(body.data) > 0:
        if len(body.data) == len(body.addresses):
            # means that we have the same amount of data as email to render
            content = [
                Content(base_content=base_content, data=d,) for d in body.data
            ]
        else:
            raise Exception(
                'Invalid body, should have the same number '
                f'of data items as addresses item, got {len(body.data)} and {body.addresses}'
            )
    else:
        content = [Content(base_content=base_content)]
    utils.send_mail(identity, content, body.from_, body.addresses)


@router.post('/send/{identity}/plain')
@db_session
def send_mail_plain(identity: str, body: SendPlainMailBody):
    content = Content(
        content=body.content,
        subject=body.subject
    )
    utils.send_mail(identity, [content], body.from_, body.addresses)


@router.get('/live')
def live():
    return Response('OK')


@router.get('/templates')
def list_templates():
    # TODO
    pass
