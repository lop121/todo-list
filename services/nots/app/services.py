import logging
from . import schemas

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


def handle_user_registration(event: schemas.NotificationNewUser):
    logger.info(
        "Уведомление! Зарегистрировался новый пользователь: %s (создан: %s)",
        event.username,
        event.time_create.strftime('%Y-%m-%d %H:%M:%S')
    )
    # В будущем здесь будет:
    # send_email_to_admin(f"Новый пользователь: {event.username}")
