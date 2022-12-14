from dataclasses import dataclass
from typing import Generic, TypeVar, Optional
import threading
import logging
import pika
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection
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


class Monitor(threading.Thread):
    def __init__(self, channel: BlockingConnection, logger: Optional[logging.Logger] = None):
        self.channel = channel
        self.stopped = False
        self.running = False
        self.logger = logger or logging.getLogger()
    
    def run(self):
        self.running = True
        self.logger.info("Monitor started")
        while not self.stopped:
            self.logger.info("Monitor ensure events begin processed")
            self.channel.process_data_events() # prevent timeout
            time.sleep(10)
        self.running =  False

    def stop(self):
        self.stopped = True
        self.join()


class RabbitChannel(ChannelInterface[T]):
    def __init__(self, connection: RabbitMQImplem, channel: BlockingChannel) -> None:
        self.channel = channel
        self.connection = connection


    def add_consumer(self, name: str, consumer: CallbackType[T]) -> None:
        def wrapped_callback(ch: BlockingChannel, method: Basic.Deliver, properties: pika.BasicProperties, body: bytes): # TODO: body type should be generic
            consumer(body, RabbitACK(ch, method))

        self.channel.basic_consume(
            name, on_message_callback=wrapped_callback, auto_ack=False)

    def start(self):
        self.connection._ensure_started()
        self.channel.start_consuming()

    def stop(self):
        self.channel.stop_consuming()

    def publish(self, name: str, data: T):
        self.channel.basic_publish(exchange='', routing_key=name, body=data)


class RabbitMQImplem(Generic[T], QueueInterface[RabbitMQConf, T]):
    def __init__(self, conf: RabbitMQConf) -> None:
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=conf.host,
                heartbeat=30,
                credentials=pika.PlainCredentials(
                    username=conf.user,
                    password=conf.password,
                )
            )
        )
        self.monitor = Monitor(self.connection)

    def _ensure_started(self):
        if not self.monitor.running:
            self.monitor.start()

    def stop(self):
        self.monitor.stop()

    @staticmethod
    def get_configurer():
        return RabbitMQConf

    def declare_queue(self, name: str, passive: bool) -> RabbitChannel[T]:
        channel = self.connection.channel()
        channel.queue_declare(queue=name, passive=passive)
        return RabbitChannel(self, channel=channel)
