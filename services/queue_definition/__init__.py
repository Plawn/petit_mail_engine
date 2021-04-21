import pika

rabbitHost = 'localhost'
rabbit_user = "rabbitUser"
rabbit_password = "rabbitPass"

QUEUE_NAME = 'mail_queue'


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