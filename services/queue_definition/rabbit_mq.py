from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar, Optional
import threading
import logging
import pika
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection
from pika.spec import Basic
import time
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
        threading.Thread.__init__(self)
        self.channel = channel
        self.stopped = False
        self.running = False
        self.logger = logger or logging.getLogger()
        self.daemon = True

    def run(self):
        self.running = True
        self.logger.info("Monitor started")
        while not self.stopped:
            self.logger.info("Monitor ensure events being processed")
            self.channel.process_data_events()  # prevent timeout
            time.sleep(10)
        self.running = False

    def is_running(self):
        return self.running

    def stop(self):
        self.stopped = True
        self.join()


class RabbitChannel(ChannelInterface[T]):
    def __init__(self, connection: RabbitMQImplem, channel: BlockingChannel) -> None:
        self.channel = channel
        self.connection = connection

    def add_consumer(self, name: str, consumer: CallbackType[T]) -> None:
        # TODO: body type should be generic
        def wrapped_callback(ch: BlockingChannel, method: Basic.Deliver, properties: pika.BasicProperties, body: T):
            consumer(body, RabbitACK(ch, method))

        self.channel.basic_consume(
            name, on_message_callback=wrapped_callback, auto_ack=False)

    def start(self):
        self.ensure_ready()
        self.channel.start_consuming()

    def stop(self):
        self.channel.stop_consuming()

    def ensure_ready(self) -> None:
        if not self.connection.is_opened():
            raise Exception(
                'Not opened, call init() on the connection or open() on the channel before use')

    def publish(self, name: str, data: T):
        self.ensure_ready()
        self.channel.basic_publish(exchange='', routing_key=name, body=data)

    def open(self):
        self.connection.init()
        return self


class RabbitMQImplem(Generic[T], QueueInterface[RabbitMQConf, T]):
    def __init__(self, conf: RabbitMQConf) -> None:
        super().__init__(conf)
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

    def init(self):
        self._ensure_started()
        self.did_init = True
        return self

    def _ensure_started(self):
        if not self.monitor.is_running():
            self.monitor.start()

    def is_opened(self):
        return self.did_init

    def stop(self):
        self.monitor.stop()

    @staticmethod
    def get_configurer():
        return RabbitMQConf

    def declare_queue(self, name: str, passive: bool) -> RabbitChannel[T]:
        channel = self.connection.channel()
        channel.queue_declare(queue=name, passive=passive)
        return RabbitChannel(self, channel=channel)
