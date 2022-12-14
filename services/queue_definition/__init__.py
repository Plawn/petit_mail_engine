import os
from typing import Type, Any

import yaml
from pika.adapters.blocking_connection import BlockingChannel

from .interface import ChannelInterface, QueueACK, QueueInterface
from .rabbit_mq import RabbitACK, RabbitChannel, RabbitMQConf, RabbitMQImplem

QUEUE_TYPE = dict
QUEUE_NAME = 'mail_queue'

default_implem = RabbitMQImplem

def get_implem()-> Type[QueueInterface[Any, QUEUE_TYPE]]:
    return default_implem

def get_channel(passive: bool) -> ChannelInterface[QUEUE_TYPE]:
    # TODO: not optimal but good enough for now
    with open(os.environ.get('CONF_FILE', "conf.yaml"), 'r') as f:
        conf = yaml.safe_load(f)['queue']
    implem = get_implem()
    queue_conf = implem.get_configurer()
    connection = implem(queue_conf(
        conf['host'],
        conf['user'],
        conf['password']
    ))
    channel = connection.declare_queue(QUEUE_NAME, passive=passive)
    return channel
