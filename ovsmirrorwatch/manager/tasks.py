from celery import shared_task
from celery.utils.log import get_task_logger
from api_ovs.OvsApi import OVSAPI
from manager.models import OVSManager


logger = get_task_logger(__name__)


@shared_task
def check_ovsdb_manager(server_name):
    logger.info("The sample task just ran for " + server_name)
