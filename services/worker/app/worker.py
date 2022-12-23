import json
import logging
import traceback
from datetime import datetime

import pika
from retry import retry

from services.db_definition.sender import Sender
from services.worker.app.utils import load_context

from ...db_definition import (Content, Email, credentials, db_session, init_db,
                              minimal_settings)
from ...queue_definition import QUEUE_NAME, QueueACK, get_channel, configurer
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
    def callback(raw_body: str, ack: QueueACK[str]):
        logging.debug(f"[x] Received {raw_body}")
        body = json.loads(raw_body)
        try:
            email = Email[body['id']]
            content_entity: Content = email.content
            sender: Sender = email.sender

            sender_ = senders_db[sender.email]
            emails = [r.email for r in email.recipient]
            logging.info(f"Sending to {emails}")
            if content_entity.content is not None:
                sender_.send_raw_mail(
                    EmailObj(
                        email.from_,
                        content_entity.subject,
                        content_entity.content,
                        emails
                    )
                )
            else:
                template_name = utils.make_template_filename(
                    content_entity.base_content.template_name
                )
                data = utils.merge_data(content_entity)
                try:
                    subject, content = template_db.render(
                        template_name, data
                    )
                except KeyError:
                    logging.error(f"Template was not found: {template_name}")
                    return
                sender_.send_html_mail(
                    EmailObj(
                        email.from_,
                        subject,
                        content,
                        emails
                    )
                )

            email.sent_at = datetime.now()
            sender.pending -= len(email.recipient) # error here -> should better handle concurrent update

            ack.success()
        except:
            logging.error(traceback.format_exc())
            ack.failed(traceback.format_exc())
    return callback

@retry(pika.exceptions.AMQPConnectionError, delay=5, jitter=(1, 3))
def start_worker(conf_file: str, profile: str):
    """Starts a worker with the given configuration
    """
    
    context = load_context(conf_file, profile)
    context.template_db.bind_render_functions(BasicRenderFunctions())
    context.template_db.init()
    logging.info("Loaded context")
    init_db(credentials, minimal_settings)
    channel = get_channel(configurer, passive=False).open()

    callback = make_callback(context)
    channel.add_consumer(callback)
    logging.info('started worker')
    print('started worker')
    channel.start()
