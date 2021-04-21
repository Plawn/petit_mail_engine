

import json
from typing import List, Tuple, Union

import pika
from fastapi import FastAPI
from fastapi.responses import Response
from pony.orm.core import select
import itertools
from ...db_definition import (CommonContent, Content, Email, Identity,
                              Recipient, Sender, credentials, database,
                              db_session, init_db)
from .dto import SendPlainMailBody, SendTemplateMailBody
from ...queue_definition import QUEUE_NAME, channel

app = FastAPI()

drop_database = False


@app.on_event('startup')
def init():
    init_db(credentials, drop_database)


def get_recipients_from_emails(emails: List[List[str]]) -> List[Recipient]:
    # check if exists in db
    # create recipient entity for each not existing
    # TODO: optimize
    res = [
        [
            Recipient.get(email=email) or Recipient(email=email)
            for email in email_list
        ]
        for email_list in emails
    ]
    return res


def push_mails_to_queue(emails: List[Email]) -> None:
    for email in emails:
        channel.basic_publish(
            exchange='', routing_key=QUEUE_NAME,
            body=json.dumps({
                'id': email.id
            })
        )


def get_identities_for_emails(identity: Identity, addresses: List[List[str]]) -> List[Sender]:
    number = 0
    for a in addresses:
        number += len(a)
    identity_id = identity.id
    # TODO: use plain pony orm ?
    available_senders: List[Tuple[int, int]] = list(database.select(
        """select
                i.id,
                i.remaning
            from
                (
                    SELECT
                        s.*,
                        s.quota - s.pending - (
                            select
                                count(r.*)
                            from
                                email e
                                join sender s on s.id = e.sender
                                join email_recipient er on er.email = e.id
                                join recipient r on er.recipient = r.id
                            where
                                age(e.sent_at) < '24h'
                        ) as remaning
                    FROM
                        sender s
                        JOIN identity i on i.id = s.identity
                    where
                        i.id = $identity_id
                    group by
                        s.id
                ) as i
            where
                remaning > 0;
    """))
    # todo: clean
    # todo: handle case where not enough quota is available now
    remaining = number
    res = []
    for sender_id, available in available_senders:
        sender = Sender[sender_id]
        if remaining <= available:
            res.extend([sender for _ in range(remaining)])
            sender.pending += remaining
        else:
            res.extend([sender for _ in range(available)])
            sender.pending += available
    return res


def _send_mail(identity: str, content: List[Content], from_: str, adresses: List[List[str]]) -> Content:
    ident = Identity.get(name=identity)
    recipients = get_recipients_from_emails(adresses)
    senders = get_identities_for_emails(ident, adresses)
    emails = [
        Email(
            identity=ident,
            from_=from_,
            content=c,
            recipient=recipient,
            sender=sender,
        ) for recipient, sender, c in zip(recipients, senders, itertools.cycle(content))
    ]
    database.commit()
    # save
    # push ids to queue
    push_mails_to_queue(emails)


@app.post('/send/{identity}/html')
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
    _send_mail(identity, content, body.from_, body.addresses)


@app.post('/send/{identity}/plain')
@db_session
def send_mail_plain(identity: str, body: SendPlainMailBody):
    content = Content(
        content=body.content,
        subject=body.subject
    )
    _send_mail(identity, [content], body.from_, body.addresses)


@app.get('/live')
def live():
    return Response('OK')


@app.get('/templates')
def list_templates():
    pass
