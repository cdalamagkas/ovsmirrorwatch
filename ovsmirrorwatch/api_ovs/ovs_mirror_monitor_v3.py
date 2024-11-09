import json
import time
import logging
from ovs_vsctl import VSCtl


def get_all_mirrors(vsctl):
    """
    Retrieves all mirror configurations.
    Returns a dictionary mapping mirror UUIDs to their configurations.
    """
    command = 'list Mirror'
    result = vsctl.run(
        command=command,
        table_format='json',
        data_format='json',
        parser=None
    )
    output = result.stdout.read()
    data = json.loads(output)

    mirrors = {}  # key: mirror UUID, value: mirror config

    if not data['data']:
        return mirrors

    # Iterate over the Mirror records
    for row in data['data']:
        mirror = {}
        for key, value in zip(data['headings'], row):
            mirror[key] = value
        mirror_uuid = mirror['_uuid'][1]  # ['uuid', '<uuid>']
        mirrors[mirror_uuid] = mirror

    return mirrors

def get_mirrors(vsctl):
    """
    Retrieves the current mirror configurations.
    Returns a dictionary mapping mirror names to their configurations,
    including the bridge each mirror belongs to.
    """
    # Get all mirrors
    mirrors_by_uuid = get_all_mirrors(vsctl)

    # Get list of bridges
    command = 'list Bridge'
    result = vsctl.run(
        command=command,
        table_format='json',
        data_format='json',
        parser=None
    )
    output = result.stdout.read()
    data = json.loads(output)

    mirrors = {}  # key: mirror name, value: mirror config including bridge

    if not data['data']:
        return mirrors

    # Iterate over the Bridge records
    for row in data['data']:
        bridge = {}
        for key, value in zip(data['headings'], row):
            bridge[key] = value
        bridge_name = bridge['name']
        bridge_mirrors = bridge.get('mirrors')

        if not bridge_mirrors or bridge_mirrors == ['set', []]:
            continue

        if bridge_mirrors[0] == 'set':
            mirror_refs = bridge_mirrors[1]
        else:
            mirror_refs = [bridge_mirrors]

        for mirror_ref in mirror_refs:
            if mirror_ref[0] == 'uuid':
                mirror_uuid = mirror_ref[1]
                # Get the mirror configuration from mirrors_by_uuid
                mirror = mirrors_by_uuid.get(mirror_uuid)
                if mirror:
                    mirror_name = mirror['name']
                    mirror['bridge'] = bridge_name
                    mirrors[mirror_name] = mirror

    return mirrors

def get_port_bridge_mapping(vsctl):
    """
    Builds a mapping from port UUIDs to bridge names.
    Returns a dictionary mapping port UUIDs to bridge names.
    """
    # Get list of bridges
    command = 'list Bridge'
    result = vsctl.run(
        command=command,
        table_format='json',
        data_format='json',
        parser=None
    )
    output = result.stdout.read()
    data = json.loads(output)
    
    port_bridge_map = {}  # key: port UUID, value: bridge name
    
    if not data['data']:
        return port_bridge_map

    # Iterate over the Bridge records
    for row in data['data']:
        bridge = {}
        for key, value in zip(data['headings'], row):
            bridge[key] = value
        bridge_name = bridge['name']
        bridge_ports = bridge.get('ports')
        if not bridge_ports or bridge_ports == ['set', []]:
            continue
        if bridge_ports[0] == 'set':
            port_refs = bridge_ports[1]
        else:
            port_refs = [bridge_ports]
        for port_ref in port_refs:
            if port_ref[0] == 'uuid':
                port_uuid = port_ref[1]
                port_bridge_map[port_uuid] = bridge_name
    return port_bridge_map

def check_and_repair_mirrors(vsctl, expected_mirrors, current_mirrors):
    """
    Compares expected mirrors with current mirrors.
    If any mirror is missing or misconfigured, re-establishes it.
    Logs when a mirror gets disabled and when it re-establishes it.
    """
    expected_mirror_names = set(expected_mirrors.keys())
    current_mirror_names = set(current_mirrors.keys())
    
    # Build port_bridge_map
    port_bridge_map = get_port_bridge_mapping(vsctl)
    
    # Check for missing mirrors
    missing_mirrors = expected_mirror_names - current_mirror_names
    for mirror_name in missing_mirrors:
        logging.warning(f"Mirror '{mirror_name}' is missing. Re-establishing.")
        reestablish_mirror(vsctl, expected_mirrors[mirror_name], port_bridge_map)
        logging.info(f"Mirror '{mirror_name}' re-established.")
    
    # Check for misconfigured mirrors
    # common_mirrors = expected_mirror_names & current_mirror_names
    # for mirror_name in common_mirrors:
    #     expected_mirror = expected_mirrors[mirror_name]
    #     current_mirror = current_mirrors[mirror_name]
    #     if not compare_mirror_configs(vsctl, expected_mirror, current_mirror):
    #         logging.warning(f"Mirror '{mirror_name}' is misconfigured. Re-establishing.")
    #         # Remove the existing mirror
    #         mirror_uuid = current_mirror['_uuid'][1]  # Get the UUID string
    #         bridge_name = current_mirror['bridge']
    #         remove_mirror(vsctl, bridge_name, mirror_uuid)
    #         # Re-establish the mirror
    #         reestablish_mirror(vsctl, expected_mirror, port_bridge_map)
    #         logging.info(f"Mirror '{mirror_name}' re-established.")

def compare_mirror_configs(vsctl, expected_mirror, current_mirror):
    """
    Compares the relevant fields of two mirror configurations.
    Returns True if they are the same, False otherwise.
    """
    # For set fields
    set_fields = ['select_src_port', 'select_dst_port']
    for field in set_fields:
        expected_value = expected_mirror.get(field)
        current_value = current_mirror.get(field)
        
        # Resolve port names for comparison
        expected_ports = extract_port_names(vsctl, expected_value)
        current_ports = extract_port_names(vsctl, current_value)
        
        if expected_ports != current_ports:
            return False
    
    # For single port fields
    single_fields = ['output_port']
    for field in single_fields:
        expected_value = expected_mirror.get(field)
        current_value = current_mirror.get(field)
        
        # Resolve port names for comparison
        expected_port = extract_port_name(vsctl, expected_value)
        current_port = extract_port_name(vsctl, current_value)
        
        if expected_port != current_port:
            return False

    # Compare bridge names
    if expected_mirror.get('bridge') != current_mirror.get('bridge'):
        return False
    
    return True

def get_port_refs(port_set):
    """
    Extracts port UUIDs from a port set.
    """
    port_uuids = []
    if not port_set or port_set == ['set', []]:
        return port_uuids
    if port_set[0] == 'set':
        ports = port_set[1]
    else:
        ports = [port_set]
    
    for port in ports:
        if port[0] == 'uuid':
            port_uuid = port[1]
            port_uuids.append(port_uuid)
    return port_uuids

def reestablish_mirror(vsctl, mirror_config, port_bridge_map):
    """
    Re-establishes the mirror with the given configuration.
    Verifies that the ports used in the mirror belong to the same bridge as the mirror.
    """
    mirror_name = mirror_config['name']
    bridge_name = mirror_config['bridge']
    # Use port UUIDs instead of names
    select_src_port_refs = mirror_config.get('select_src_port')
    select_dst_port_refs = mirror_config.get('select_dst_port')
    output_port_ref = mirror_config.get('output_port')
    
    # Initialize command components
    commands = []
    # Create Mirror
    commands.append(f'-- --id=@m create Mirror name={mirror_name}')
    
    # Prepare select_src_port
    src_ports = get_port_refs(select_src_port_refs)
    # Verify that src_ports belong to the mirror's bridge
    valid_src_ports = []
    for port_uuid in src_ports:
        port_bridge = port_bridge_map.get(port_uuid)
        if port_bridge == bridge_name:
            valid_src_ports.append(port_uuid)
        else:
            port_name = get_port_name(vsctl, port_uuid)
            logging.error(f"Port '{port_name}' does not belong to bridge '{bridge_name}' and cannot be used in mirror '{mirror_name}'.")

    # Add select_src_port
    for idx, port_uuid in enumerate(valid_src_ports):
        commands.append(f'-- --id=@p{idx} get Port {port_uuid}')
    if valid_src_ports:
        port_refs = ','.join([f'@p{idx}' for idx in range(len(valid_src_ports))])
        commands.append(f'select_src_port=[{port_refs}]')
    else:
        # No valid src ports
        logging.error(f"No valid source ports for mirror '{mirror_name}'. Mirror cannot be re-established.")
        return  # Exit the function

    # Prepare select_dst_port
    dst_ports = get_port_refs(select_dst_port_refs)
    # Verify that dst_ports belong to the mirror's bridge
    valid_dst_ports = []
    for port_uuid in dst_ports:
        port_bridge = port_bridge_map.get(port_uuid)
        if port_bridge == bridge_name:
            valid_dst_ports.append(port_uuid)
        else:
            port_name = get_port_name(vsctl, port_uuid)
            logging.error(f"Port '{port_name}' does not belong to bridge '{bridge_name}' and cannot be used in mirror '{mirror_name}'.")

    # Add select_dst_port
    for idx, port_uuid in enumerate(valid_dst_ports):
        commands.append(f'-- --id=@d{idx} get Port {port_uuid}')
    if valid_dst_ports:
        port_refs = ','.join([f'@d{idx}' for idx in range(len(valid_dst_ports))])
        commands.append(f'select_dst_port=[{port_refs}]')
    # It's acceptable for select_dst_port to be empty

    # Output port
    if output_port_ref and output_port_ref[0] == 'uuid':
        output_port_uuid = output_port_ref[1]
        port_bridge = port_bridge_map.get(output_port_uuid)
        if port_bridge == bridge_name:
            commands.append(f'-- --id=@out get Port {output_port_uuid}')
            commands.append(f'output_port=@out')
        else:
            port_name = get_port_name(vsctl, output_port_uuid)
            logging.error(f"Output port '{port_name}' does not belong to bridge '{bridge_name}' and cannot be used in mirror '{mirror_name}'. Mirror cannot be re-established.")
            return  # Exit the function
    else:
        # No output port
        logging.error(f"No valid output port for mirror '{mirror_name}'. Mirror cannot be re-established.")
        return  # Exit the function

    # Add the Mirror to the Bridge
    commands.append(f'-- add Bridge {bridge_name} mirrors @m')
    
    # Build the full command
    command = ' '.join(commands)
    
    try:
        vsctl.run(command=command, parser=None)
    except Exception as e:
        logging.error(f"Error re-establishing mirror '{mirror_name}' on bridge '{bridge_name}': {e}")

def extract_port_names(vsctl, port_set):
    """
    Given a port set from the mirror configuration, return a set of port names.
    """
    port_names = set()
    if not port_set or port_set == ['set', []]:
        return port_names
    if port_set[0] == 'set':
        ports = port_set[1]
    else:
        ports = [port_set]
    
    for port in ports:
        if port[0] == 'uuid':
            port_uuid = port[1]
            port_name = get_port_name(vsctl, port_uuid)
            port_names.add(port_name)
    return port_names

def extract_port_name(vsctl, port_ref):
    """
    Given a port reference from the mirror configuration, returns the port name.
    """
    if not port_ref or port_ref == ['uuid', '00000000-0000-0000-0000-000000000000']:
        return None
    if port_ref[0] == 'uuid':
        port_uuid = port_ref[1]
        port_name = get_port_name(vsctl, port_uuid)
        return port_name
    return None

def get_port_name(vsctl, port_uuid):
    """
    Given a port UUID, return its name.
    """
    command = f'get Port {port_uuid} name'
    try:
        result = vsctl.run(command=command, parser=None)
        port_name = result.stdout.read().strip().strip('"')
        return port_name
    except Exception as e:
        logging.error(f"Error fetching port name for UUID {port_uuid}: {e}")
        return port_uuid

def remove_mirror(vsctl, bridge_name, mirror_uuid):
    """
    Removes the mirror with the given UUID from the specified bridge.
    """
    command = f'remove Bridge {bridge_name} mirrors {mirror_uuid}'
    try:
        vsctl.run(command=command, parser=None)
    except Exception as e:
        logging.error(f"Error removing mirror {mirror_uuid} from bridge {bridge_name}: {e}")

def print_mirrors(vsctl, mirrors):
    """
    Prints all current mirror configurations.
    """
    print("\nCurrent Port Mirroring Configurations:")
    if not mirrors:
        print("No port mirroring configurations found.")
        return
    for mirror_name, mirror in mirrors.items():
        print(f"Mirror Name: {mirror_name}")
        print(f"    UUID: {mirror['_uuid']}")
        print(f"    Bridge: {mirror.get('bridge')}")
        select_src_ports = extract_port_names(vsctl, mirror.get('select_src_port'))
        select_dst_ports = extract_port_names(vsctl, mirror.get('select_dst_port'))
        output_port = extract_port_name(vsctl, mirror.get('output_port'))
        print(f"    Select Src Ports: {list(select_src_ports)}")
        print(f"    Select Dst Ports: {list(select_dst_ports)}")
        print(f"    Output Port: {output_port}")
        print(f"    Statistics: {mirror.get('statistics')}")
        print(f"    External IDs: {mirror.get('external_ids')}")
        print()
    print("-" * 50)

def main():
    # Initialize VSCtl instance
    vsctl = VSCtl('tcp','192.168.86.254', 6640)
    
    # Get initial expected mirror configurations
    expected_mirrors = get_mirrors(vsctl)
    if not expected_mirrors:
        print("No port mirroring configurations found.")
        return
    
    print("Starting port mirroring monitor...")
    logging.info("Started port mirroring monitor.")
    
    # Start monitoring loop
    while True:
        # Wait for 5 seconds
        time.sleep(5)
        
        # Get current mirror configurations
        current_mirrors = get_mirrors(vsctl)
        
        # Compare current mirrors with expected mirrors
        check_and_repair_mirrors(vsctl, expected_mirrors, current_mirrors)
        
        # Get updated mirrors after any repairs
        current_mirrors = get_mirrors(vsctl)
        
        # Print all current mirror configurations
        print_mirrors(vsctl, current_mirrors)


if __name__ == "__main__":
    main()




