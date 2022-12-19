import os
from typing import Type, Any

import yaml
from pika.adapters.blocking_connection import BlockingChannel

from .interface import ChannelInterface, QueueACK, QueueInterface
from .rabbit_mq import RabbitACK, RabbitChannel, RabbitMQConf, RabbitMQImplem
from ..configurer import Configurer, YamlConfigurer
from pydantic import BaseModel

QUEUE_TYPE = dict
QUEUE_NAME = 'mail_queue'

default_implem = RabbitMQImplem


def get_implem() -> Type[QueueInterface[Any, QUEUE_TYPE]]:
    return default_implem

class QueueConf(BaseModel):
    host: str
    user: str
    password: str

class Conf(BaseModel):
    queue: QueueConf


configurer = YamlConfigurer[Conf](os.environ.get('CONF_FILE', "conf.yaml"))

def get_channel(configurer: Configurer[Conf], passive: bool) -> ChannelInterface[QUEUE_TYPE]:
    conf = configurer.content().queue
    implem = get_implem()
    queue_conf = implem.get_configurer()
    connection = implem(queue_conf(conf.host, conf.user, conf.password))
    channel = connection.declare_queue(QUEUE_NAME, passive=passive)
    return channel
