import os
from typing import Type, Any, Union

import yaml
from pika.adapters.blocking_connection import BlockingChannel

from .interface import ChannelInterface, QueueACK, QueueInterface
from .rabbit_mq import RabbitACK, RabbitChannel, RabbitMQConf, RabbitMQImplem
from ..configurer import Configurer, YamlConfigurer
from pydantic import BaseModel
from .pulsar_queue import PulsarConf, PulsarImplem

QUEUE_TYPE = dict
QUEUE_NAME = 'mail_queue'

default_implem = RabbitMQImplem

implems = {
    "rabbit": RabbitMQImplem,
    "pulsar": PulsarImplem
}

def get_implem(implem_name: str) -> Type[QueueInterface[Any, QUEUE_TYPE]]:
    return implems[implem_name]

class Conf(BaseModel):
    queue: Union[RabbitMQConf, PulsarConf]


configurer = YamlConfigurer[Conf](os.environ.get('CONF_FILE', "conf.yaml"))

def get_channel(configurer: Configurer[Conf], passive: bool) -> ChannelInterface[QUEUE_TYPE]:
    conf = configurer.content().queue
    implem = get_implem(conf.implem)
    queue_configurer = implem.get_configurer()
    connection = implem(queue_configurer(**conf.dict()))
    channel = connection.declare_queue(QUEUE_NAME, passive=passive)
    return channel
