import pika
from pika.adapters.blocking_connection import BlockingChannel


# todo, load from conf


QUEUE_NAME = 'mail_queue'


def get_channel() -> BlockingChannel:
    rabbitHost = 'localhost'
    rabbit_user = "rabbitUser"
    rabbit_password = "rabbitPass"
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
