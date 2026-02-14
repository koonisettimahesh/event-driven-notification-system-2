import pika
import json
import logging
from datetime import datetime
from db import get_connection
from config import (
    RABBITMQ_HOST,
    RABBITMQ_USER,
    RABBITMQ_PASSWORD,
    QUEUE_NAME
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def process_event(ch, method, properties, body):
    try:
        event = json.loads(body)

        logger.info(f"Processing event: {event}")

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO processed_events
                    (user_id, event_type, message, payload, processed_at)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (user_id, event_type, message) DO NOTHING
                    """,
                    (
                        event["user_id"],
                        event["event_type"],
                        event["message"],
                        json.dumps(event.get("payload")),
                        datetime.utcnow()
                    )
                )
            conn.commit()

        logger.info("Event stored successfully")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except json.JSONDecodeError:
        logger.error("Invalid JSON format")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def start_consumer():
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

    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    channel.basic_consume(
        queue=QUEUE_NAME,
        on_message_callback=process_event
    )

    logger.info("Consumer waiting for messages...")
    channel.start_consuming()


if __name__ == "__main__":
    start_consumer()
