from dataclasses import dataclass
from typing import Generic, TypeVar

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic

from .interface import CallbackType, ChannelInterface, QueueACK, QueueInterface

T = TypeVar('T')


@dataclass
class RabbitMQConf:
    host: str
    user: str
    password: str
    
class RabbitACK(Generic[T], QueueACK[T]):
    
    def __init__(self, channel: BlockingChannel, method: Basic.Deliver) -> None:
        self.channel = channel
        self.method = method
    
    def success(self) -> None:
        self.channel.basic_ack(delivery_tag=self.method.delivery_tag)
    
    def failed(self, reason: str) -> None:
        """reason is ignored for now"""
        self.channel.basic_nack(delivery_tag=self.method.delivery_tag)

class RabbitChannel(ChannelInterface[T]):
    def __init__(self, channel: BlockingChannel) -> None:
        self.channel = channel
    
    def add_consumer(self, name: str, consumer: CallbackType[T]) -> None:
        def wrapped_callback(ch: BlockingChannel, method: Basic.Deliver, properties: pika.BasicProperties, body: bytes):
            consumer(body, RabbitACK(ch, method))
        
        self.channel.basic_consume(name, on_message_callback=wrapped_callback, auto_ack=False)

    def start(self):
        self.channel.start_consuming()
        
    def stop(self):
        self.channel.stop_consuming()

class RabbitMQImplem(Generic[T], QueueInterface[RabbitMQConf, T]):
    def __init__(self, conf: RabbitMQConf) -> None:
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=conf.host,
                credentials=pika.PlainCredentials(
                    username=conf.user,
                    password=conf.password,
                )
            )
        )
        
    def declare_queue(self, name: str, passive: bool) -> RabbitChannel[T]: 
        channel = self.connection.channel()
        channel.queue_declare(queue=name, passive=passive)
        return RabbitChannel(channel=channel)
