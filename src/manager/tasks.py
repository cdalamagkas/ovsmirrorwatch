from celery import shared_task
from celery.utils.log import get_task_logger
from api_ovs.OvsApi import OVSAPI
from manager.models import OVSManager
from mirror.models import OVSMirror


logger = get_task_logger(__name__)


@shared_task(ignore_result=True)
def check_ovsdb_manager(server_name):
    manager = OVSManager.objects.get(name=server_name)
    OVSDBManager = OVSAPI(addr=manager.ip_address, port=manager.port)

    # Get all mirrors from the live system
    live_mirrors = OVSDBManager.get_mirrors_overview()
    live_named_mirrors = {live_mirror.get('name'):live_mirror for live_mirror in live_mirrors} #helper dict

    db_mirrors = OVSMirror.objects.all()

    # For each mirror of the Django DB
    for db_mirror in db_mirrors:

        mirror_name = db_mirror.name
        bridge_name = db_mirror.out_port.bridge.ovs_name
        select_src_ports = [f_name["ovs_name"] for f_name in db_mirror.src_ports.values('ovs_name')]
        select_dst_ports = [f_name["ovs_name"] for f_name in db_mirror.dst_ports.values('ovs_name')]
        output_port = db_mirror.out_port.ovs_name

        if mirror_name in live_named_mirrors.keys():
            live_mirror = live_named_mirrors[mirror_name]
            # Update health status
            db_mirror.health = True
            logger.info(f"Mirror {db_mirror.name} is live.")

            # Check for misconfiguration. If yes change the mirror config to the desired on based on the db mirror.
            # Check config of live and db mirror setups
            if not any([select_src_ports == live_mirror["select_src_port"],
                        select_dst_ports == live_mirror["select_dst_port"],
                        output_port == live_mirror["output_port"]]):
                
                db_mirror.health = False
                logger.info(f"Mirror {db_mirror.name} is live but misconfigured.")

                # Destroy old mirror and set up a new one based on the db mirror
                if OVSDBManager.destroy_mirror(mirror_name, bridge_name):
                    logger.info(f"Destroyed mirror {db_mirror.name}.")
                    
                    # Reset the mirror on OVS Manager
                    if OVSDBManager.create_mirror(mirror_name, bridge_name, select_src_ports, select_dst_ports, output_port):
                        logger.info(f"Reseted mirror {db_mirror.name} successfully.")
                        # Update health status
                        db_mirror.health = True
                    else:
                        # Update health status
                        db_mirror.health = False
                        logger.info(f"Failed to reset mirror {db_mirror.name}")
                        
                else:
                    logger.info(f'Failed to destroy mirror {db_mirror.name}')
        

        # Check if mirror does not exist. If not recreate the mirror
        else:
            # Update health status
            db_mirror.health = False
            OVSDBManager.create_mirror(mirror_name, bridge_name, select_src_ports, select_dst_ports, output_port)

                
    logger.info("The sample task just ran for " + server_name)
