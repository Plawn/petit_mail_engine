import os

import pika
import yaml
from pika.adapters.blocking_connection import BlockingChannel

QUEUE_NAME = 'mail_queue'

def get_channel() -> BlockingChannel:
    # TODO: not optimal but good enough
    with open(os.environ.get('CONF_FILE', "conf.yaml"), 'r') as f :
        conf = yaml.safe_load(f)['queue']
    
    rabbitHost = conf['address']
    rabbit_user = conf['user']
    rabbit_password = conf['password']
    
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=rabbitHost,
            credentials=pika.PlainCredentials(
                username=rabbit_user,
                password=rabbit_password,
            )
        )
    )

    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME)

    return channel
