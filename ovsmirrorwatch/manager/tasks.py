from celery import shared_task
from celery.utils.log import get_task_logger
from api_ovs.OvsApi import OVSAPI
from manager.models import OVSManager
from mirror.models import OVSMirror
from api_ovs.ovs_mirror_monitor_v3 import check_and_repair_mirrors


logger = get_task_logger(__name__)


@shared_task
def check_ovsdb_manager(server_name):
    manager = OVSManager.objects.get(name=server_name)
    OVSDBManager = OVSAPI(addr=manager.ip_address, port=manager.port)

    # Get all mirrors from the live system
    live_mirrors = OVSDBManager.get_mirrors_overview()
    
    # check_and_repair_mirrors(OVSDBManager, OVSManager.objects.all(), live_mirrors)

    # For each mirror of the Django DB
    for db_mirror in OVSMirror.objects.all():

        # Check if the mirror exists in the real system
        live_mirror = [item for item in live_mirrors if item.get('name')==db_mirror.name]
        if len(live_mirror) > 0:

            live_mirror = live_mirror[0]

            # If exists, check if the components of the live mirror correspond to the db_mirror components
            # live_src_ports = live_mirror["select_src_port"]
            # live_dst_ports = live_mirror["select_dst_port"]
            # live_output_port = live_mirror["output_port"]
            # if not, destroy and create again the mirror, based on the db_mirror components

        else:
            # if the mirror does not exist, create it, based on the db_mirror components
            logger.info("The mirror " + db_mirror.name + " does not exist.")

                
    logger.info("The sample task just ran for " + server_name)
