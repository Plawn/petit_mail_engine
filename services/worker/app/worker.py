import json
import logging
from datetime import datetime

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic
from services.db_definition.common_content import CommonContent
from services.db_definition.sender import Sender
from services.worker.app.utils import load_context

from ...db_definition import (Content, Email, Recipient, credentials, database,
                              db_session, init_db)
from ...queue_definition import QUEUE_NAME, channel
from .render_functions import RenderFunctions
from .senders.interface import Email as EmailObj


def make_template_filename(template_name: str):
    return template_name + '.html'


class BasicRenderFunctions(RenderFunctions):
    def ternary(self, _input, a, b):
        return a if _input else b

    def get_functions(self):
        return {
            'ternary': self.ternary,
        }


def merge_data(content: Content) -> dict:
    b = content.base_content.data or {}
    s = content.data or {}
    # merge data
    for k, v in s.items():
        b[k] = v
    return b


def main(conf_file: str):
    init_db(credentials)

    context = load_context(conf_file, 'local')

    template_db = context.template_db
    context.template_db.bind_render_functions(BasicRenderFunctions())
    template_db.init()
    senders_db = context.senders_db

    @db_session
    def callback(ch: BlockingChannel, method: Basic.Deliver, properties: pika.BasicProperties, body: bytes):
        logging.debug("[x] Received %r" % body)
        body = json.loads(body)
        try:
            email = Email[body['id']]
            content_entity: Content = email.content
            sender: Sender = email.sender
            sender_ = senders_db[sender.email]
            if content_entity.content is not None:
                sender_.send_raw_mail(
                    EmailObj(
                        email.from_,
                        content_entity.subject,
                        content_entity.content,
                        [r.email for r in email.recipient]
                    )
                )
            else:
                template_name = make_template_filename(
                    content_entity.base_content.template_name
                )
                data = merge_data(content_entity)
                subject, content = template_db.render(
                    template_name, data
                )
                sender_.send_html_mail(
                    EmailObj(
                        email.from_,
                        subject,
                        content,
                        [r.email for r in email.recipient]
                    )
                )

            email.sent_at = datetime.now()
            sender.pending -= len(email.recipient)

            ch.basic_ack(delivery_tag=method.delivery_tag)
        except:
            import traceback
            traceback.print_exc()

    channel.basic_consume(
        queue=QUEUE_NAME, on_message_callback=callback, auto_ack=False
    )
    logging.info('started worker')
    channel.start_consuming()
