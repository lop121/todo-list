import pika
import json
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class RabbitClient:
    def __init__(self, host: str = 'rabbitmq'):
        self.host = host
        self.exchange_name = 'user_events'
        self.queue_name = 'notifications_queue'
        self.routing_key = 'user.registered'

    def _send_message(self, body: dict):
        """
        Приватный метод для подключения и отправки сообщения.
        """
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host))
            channel = connection.channel()

            channel.exchange_declare(exchange=self.exchange_name, exchange_type='direct')
            channel.queue_declare(queue=self.queue_name, durable=True)
            channel.queue_bind(
                exchange=self.exchange_name,
                queue=self.queue_name,
                routing_key=self.routing_key
            )

            channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=self.routing_key,
                body=json.dumps(body)
            )

            logger.info(f" [x] Отправлено сообщение с ключом '{self.routing_key}': {body}")
            connection.close()

        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f" [!] Не удалось подключиться к RabbitMQ: {e}")

    def send_user_registered_notification(self, username: str):
        """
        Публичный метод для отправки уведомления о регистрации.
        """
        message_body = {
            "username": username,
            "time_create": datetime.now(timezone.utc).isoformat()
        }
        self._send_message(message_body)
