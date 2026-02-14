import json
import pika
from .config import RABBITMQ_HOST, RABBITMQ_USER, RABBITMQ_PASSWORD, QUEUE_NAME


def publish_event(event_data: dict):
    credentials = pika.PlainCredentials(
        RABBITMQ_USER,
        RABBITMQ_PASSWORD
    )

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            credentials=credentials
        )
    )

    channel = connection.channel()

    # Durable queue
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    # Persistent message
    channel.basic_publish(
        exchange="",
        routing_key=QUEUE_NAME,
        body=json.dumps(event_data),
        properties=pika.BasicProperties(
            delivery_mode=2  # Makes message persistent
        ),
    )

    connection.close()
