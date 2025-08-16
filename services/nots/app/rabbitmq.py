import pika
from pydantic import ValidationError

from . import schemas, services
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logging.getLogger("pika").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

ROUTING_MAP = {
    'user.registered': (schemas.NotificationNewUser, services.handle_user_registration),
    # 'task.created': (schemas.TaskCreatedEvent, services.handle_task_creation), # для будущего
}


def callback(ch, method, properties, body):
    routing_key = method.routing_key
    logger.info(f"Получено сообщение с ключом маршрутизации: {routing_key}")

    handler_tuple = ROUTING_MAP.get(routing_key)
    if not handler_tuple:
        logger.warning(f"Нет обработчика для ключа: {routing_key}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        return

    schema, handler_function = handler_tuple

    try:
        message = schema.model_validate_json(body)
        handler_function(message)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except ValidationError as e:
        logger.error(f"Ошибка валидации Pydantic для ключа {routing_key}: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    except Exception as e:
        logger.error(f"Неизвестная ошибка при обработке сообщения: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def start_consuming():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    exchange_name = 'user_events'
    channel.exchange_declare(exchange=exchange_name, exchange_type='direct')

    queue_name = 'notifications_queue'
    channel.queue_declare(queue=queue_name, durable=True)

    for routing_key in ROUTING_MAP.keys():
        channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)
        logger.info(f"Очередь '{queue_name}' привязана к ключу '{routing_key}'")

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=callback)

    logger.info('[*] Ожидание сообщений. Для выхода нажмите CTRL+C')
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("Остановка консьюмера")
        channel.stop_consuming()
    finally:
        connection.close()
        logger.info("Соединение с RabbitMQ закрыто")
