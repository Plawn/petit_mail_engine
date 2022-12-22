from __future__ import annotations

from pulsar import Client, MessageId, Consumer, Message
import pulsar
from dataclasses import dataclass
from typing import Generic, TypeVar, Optional
import logging

import time
from .interface import CallbackType, ChannelInterface, QueueACK, QueueInterface

T = TypeVar('T')


@dataclass
class PulsarConf:
    host: str
    port: str


"""
client = pulsar.Client('pulsar://localhost:6650')

consumer = client.subscribe(
    topic='my-topic',
    subscription_name='my-subscription',
    schema=AvroSchema(Example))


while True:
    msg = consumer.receive()
    ex = msg.value()
    try:
        print("Received message a={} b={} c={}".format(ex.a, ex.b, ex.c))
        # Acknowledge successful processing of the message
        consumer.acknowledge(msg)
    except Exception:
        # Message failed to be processed
        consumer.negative_acknowledge(msg)
"""


@dataclass
class RabbitMQConf:
    host: str
    user: str
    password: str

# OK


class PulsarACK(Generic[T], QueueACK[T]):

    def __init__(self, consumer: Consumer, message: Message) -> None:
        self.consumer = consumer
        self.message = message

    def success(self) -> None:
        self.consumer.acknowledge(self.message)

    def failed(self, reason: str) -> None:
        """reason is ignored for now"""
        self.consumer.negative_acknowledge(message)


class PulsarChannel(ChannelInterface[T]):
    def __init__(self, connection: PulsarImplem, name: str) -> None:
        self.connection = connection
        self.consumer = self.connection.get_consumer(topic, 'worker')
        self.producer = self.connection.get_producer(topic)
        self.running = False
        self.consumers = []

    def add_consumer(self, name: str, consumer: CallbackType[T]) -> None:
        self.consumers.append(wrapped)

    def start(self):
        self.running = True
        while self.running:
            try:
                msg = self.consumer.receive(timeout_millis=1000)
                body = msg.value()
                for consumer in self.consumers:
                    try:
                        consumer(body, PulsarACK(self.consumer, msg))
                    except Exception:
                        # Message failed to be processed
                        self.consumer.negative_acknowledge(msg)
            except:
                continue


    def stop(self):
        self.running = False

    def publish(self, name: str, data: T):
        self.producer.send(data)

    def open(self):
        self.connection.init()
        return self


class PulsarImplem(Generic[T], QueueInterface[PulsarConf, T]):
    def __init__(self, conf: PulsarConf) -> None:
        super().__init__(conf)
        self.connection = pulsar.Client(f'pulsar://{conf.host}:{conf.port}')

    def init(self):
        self.did_init = True
        return self

    def is_opened(self):
        return self.did_init

    def stop(self):
        pass

    @staticmethod
    def get_configurer():
        return PulsarConf

    def get_consumer(self, topic: str, subscription_name: str):
        return self.connection.subscribe(topic, subscription_name)

    def get_producer(self, topic: str):
        return self.connection.create_producer(topic)

    def declare_queue(self, name: str, passive: bool) -> RabbitChannel[T]:
        return PulsarChannel(self, name)
