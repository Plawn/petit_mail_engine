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
    def __init__(self, connection: PulsarImplem, channel: Consumer) -> None:
        self.connection = connection
        self.channel = channel
        
    def add_consumer(self, name: str, consumer: CallbackType[T]) -> None:
        # TODO: body type should be generic
        def wrapped_callback(ch: Consumer, method: Basic.Deliver, properties: pika.BasicProperties, body: T):
            consumer(body, PulsarACK(ch, method))

        self.channel.basic_consume(
            name, on_message_callback=wrapped_callback, auto_ack=False)

    def start(self):
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

    def stop(self):
        self.channel.stop_consuming()

    def publish(self, name: str, data: T):
        self.ensure_ready()
        self.channel.basic_publish(exchange='', routing_key=name, body=data)

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

    def declare_queue(self, name: str, passive: bool) -> RabbitChannel[T]:
        channel = self.connection.channel()
        channel.queue_declare(queue=name, passive=passive)
        return PulsarChannel(self, channel=channel)
