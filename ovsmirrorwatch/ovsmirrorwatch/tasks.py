from celery import shared_task
from celery.utils.log import get_task_logger
from api_ovs.OvsApi import OVSAPI


logger = get_task_logger(__name__)


@shared_task
def check_server_updates():
    logger.info("The sample task just ran.")
