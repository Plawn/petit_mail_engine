import json
import logging
import traceback
from datetime import datetime

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic
from services.db_definition.sender import Sender
from services.worker.app.utils import load_context

from ...db_definition import Content, Email, credentials, init_db, db_session
from ...queue_definition import QUEUE_NAME, get_channel
from . import utils
from .basic_render_functions import BasicRenderFunctions
from .data_structure import Context
from .senders.interface import Email as EmailObj


def make_callback(context: Context):
    """Creates a callback from the given context
    """
    senders_db = context.senders_db
    template_db = context.template_db

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
                template_name = utils.make_template_filename(
                    content_entity.base_content.template_name
                )
                data = utils.merge_data(content_entity)
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
            logging.error(traceback.format_exc())

    return callback


def start_worker(conf_file: str, profile: str):
    """Starts a worker with the given configuration
    """
    init_db(credentials)
    channel = get_channel()
    context = load_context(conf_file, profile)

    context.template_db.bind_render_functions(BasicRenderFunctions())
    context.template_db.init()
    callback = make_callback(context)
    channel.basic_consume(
        queue=QUEUE_NAME, on_message_callback=callback, auto_ack=False
    )
    logging.info('started worker')
    print('started worker')
    channel.start_consuming()
