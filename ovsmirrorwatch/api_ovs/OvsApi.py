import json
from ovs_vsctl import VSCtl, exception


class OVSAPI:
    def __init__(self, protocol='tcp', addr='192.168.86.254', port=6640):
        self.vsctl = VSCtl(protocol=protocol, addr=addr, port=port)

    def list_bridges(self):
        """
        List all available bridge interfaces.
        Returns a list of bridge names.
        """
        command = 'list-br'
        try:
            result = self.vsctl.run(command=command, parser=None)
            output = result.stdout.read()
            bridge_names = output.strip().split('\n')
            return [bridge for bridge in bridge_names if bridge]
        except exception.VSCtlError as e:
            print(f"Error listing bridges: {e}")
            return []

    def list_ports(self, bridge_name):
        """
        List available ports for a given bridge interface.
        Returns a list of port names.
        """
        command = f'list-ports {bridge_name}'
        try:
            result = self.vsctl.run(command=command, parser=None)
            output = result.stdout.read()
            port_names = output.strip().split('\n')
            return [port for port in port_names if port]
        except exception.VSCtlError as e:
            print(f"Error listing ports on bridge '{bridge_name}': {e}")
            return []

    def create_mirror(self, mirror_name, bridge_name, select_src_ports, select_dst_ports, output_port):
        """
        Create a port mirror.
        Parameters:
            mirror_name (str): Name of the mirror.
            bridge_name (str): Name of the bridge to add the mirror to.
            select_src_ports (list): List of source port names to mirror.
            select_dst_ports (list): List of destination port names to mirror.
            output_port (str): Name of the output port.
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Build command components
            commands = []
            # Create Mirror
            commands.append(f'-- --id=@m create Mirror name={mirror_name}')

            # Add select_src_ports
            for idx, port_name in enumerate(select_src_ports):
                commands.append(f'-- --id=@p{idx} get Port {port_name}')
            if select_src_ports:
                port_refs = ','.join([f'@p{idx}' for idx in range(len(select_src_ports))])
                commands.append(f'select_src_port=[{port_refs}]')

            # Add select_dst_ports
            for idx, port_name in enumerate(select_dst_ports):
                commands.append(f'-- --id=@d{idx} get Port {port_name}')
            if select_dst_ports:
                port_refs = ','.join([f'@d{idx}' for idx in range(len(select_dst_ports))])
                commands.append(f'select_dst_port=[{port_refs}]')

            # Output port
            if output_port:
                commands.append(f'-- --id=@out get Port {output_port}')
                commands.append(f'output_port=@out')

            # Add the Mirror to the Bridge
            commands.append(f'-- add Bridge {bridge_name} mirrors @m')

            # Build the full command
            command = ' '.join(commands)

            self.vsctl.run(command=command, parser=None)
            print(f"Mirror '{mirror_name}' created successfully on bridge '{bridge_name}'.")
            return True
        except Exception as e:
            print(f"Error creating mirror '{mirror_name}': {e}")
            return False

    def destroy_mirror(self, mirror_name, bridge_name):
        """
        Destroy a port mirror.
        Parameters:
            mirror_name (str): Name of the mirror to destroy.
            bridge_name (str): Name of the bridge containing the mirror.
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Get the UUID of the mirror
            command = f'get Bridge {bridge_name} mirrors'
            result = self.vsctl.run(command=command, parser=None)
            output = result.stdout.read()
            mirror_uuids = self.extract_uuids_from_output(output)

            # Find the mirror with the specified name
            for mirror_uuid in mirror_uuids:
                command = f'get Mirror {mirror_uuid} name'
                result = self.vsctl.run(command=command, parser=None)
                name = result.stdout.read().strip().strip('"')
                if name == mirror_name:
                    # Remove the mirror from the bridge
                    command = f'remove Bridge {bridge_name} mirrors {mirror_uuid}'
                    self.vsctl.run(command=command, parser=None)
                    # Destroy the mirror
                    command = f'destroy Mirror {mirror_uuid}'
                    self.vsctl.run(command=command, parser=None)
                    print(f"Mirror '{mirror_name}' destroyed successfully.")
                    return True
            print(f"Mirror '{mirror_name}' not found on bridge '{bridge_name}'.")
            return False
        except Exception as e:
            print(f"Error destroying mirror '{mirror_name}': {e}")
            return False

    def alter_mirror(self, mirror_name, bridge_name, select_src_ports=None, select_dst_ports=None, output_port=None):
        """
        Alter an existing port mirror.
        Parameters:
            mirror_name (str): Name of the mirror to alter.
            bridge_name (str): Name of the bridge containing the mirror.
            select_src_ports (list): New list of source port names to mirror.
            select_dst_ports (list): New list of destination port names to mirror.
            output_port (str): New name of the output port.
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Get the UUID of the mirror
            command = f'get Bridge {bridge_name} mirrors'
            result = self.vsctl.run(command=command, parser=None)
            output = result.stdout.read()
            mirror_uuids = self.extract_uuids_from_output(output)

            mirror_uuid = None
            for uuid in mirror_uuids:
                command = f'get Mirror {uuid} name'
                result = self.vsctl.run(command=command, parser=None)
                name = result.stdout.read().strip().strip('"')
                if name == mirror_name:
                    mirror_uuid = uuid
                    break

            if not mirror_uuid:
                print(f"Mirror '{mirror_name}' not found on bridge '{bridge_name}'.")
                return False

            # Build command components
            commands = []

            # Update select_src_ports
            if select_src_ports is not None:
                port_refs = []
                for idx, port_name in enumerate(select_src_ports):
                    self.vsctl.run(command=f'--id=@p{idx} get Port {port_name}', parser=None)
                    port_refs.append(f'@p{idx}')
                if port_refs:
                    commands.append(f'set Mirror {mirror_uuid} select_src_port=[{",".join(port_refs)}]')
                else:
                    commands.append(f'clear Mirror {mirror_uuid} select_src_port')

            # Update select_dst_ports
            if select_dst_ports is not None:
                port_refs = []
                for idx, port_name in enumerate(select_dst_ports):
                    self.vsctl.run(command=f'--id=@d{idx} get Port {port_name}', parser=None)
                    port_refs.append(f'@d{idx}')
                if port_refs:
                    commands.append(f'set Mirror {mirror_uuid} select_dst_port=[{",".join(port_refs)}]')
                else:
                    commands.append(f'clear Mirror {mirror_uuid} select_dst_port')

            # Update output_port
            if output_port is not None:
                if output_port:
                    self.vsctl.run(command=f'--id=@out get Port {output_port}', parser=None)
                    commands.append(f'set Mirror {mirror_uuid} output_port=@out')
                else:
                    commands.append(f'clear Mirror {mirror_uuid} output_port')

            # Execute commands
            for cmd in commands:
                self.vsctl.run(command=cmd, parser=None)

            print(f"Mirror '{mirror_name}' altered successfully.")
            return True
        except Exception as e:
            print(f"Error altering mirror '{mirror_name}': {e}")
            return False

    def get_mirrors_overview(self):
        """
        Provides an overview of established port mirrors.
        Returns a list of dictionaries containing mirror information.
        """
        try:
            command = 'list Mirror'
            result = self.vsctl.run(command=command, parser=None)
            output = result.stdout.read()
            mirrors = self.parse_mirror_output(output)
            return mirrors
        except Exception as e:
            print(f"Error retrieving mirrors overview: {e}")
            return []

    # Helper functions
    def extract_uuids_from_output(self, output):
        """
        Extracts UUIDs from ovs-vsctl output.
        """
        uuids = []
        # The output might look like [uuid1, uuid2, ...]
        output = output.strip().strip('[]')
        if output:
            uuids = [uuid.strip() for uuid in output.split(',')]
        return uuids

    def parse_mirror_output(self, output):
        """
        Parses the output of 'list Mirror' command into a list of dictionaries.
        """
        # For simplicity, we can use the JSON output
        result = self.vsctl.run(
            command='list Mirror',
            table_format='json',
            data_format='json',
            parser=None
        )
        output = result.stdout.read()
        data = json.loads(output)
        mirrors = []

        if not data['data']:
            return mirrors

        for row in data['data']:
            mirror = {}
            for key, value in zip(data['headings'], row):
                mirror[key] = value
            # Resolve port UUIDs to names
            mirror['select_src_port'] = self.resolve_ports(mirror.get('select_src_port'))
            mirror['select_dst_port'] = self.resolve_ports(mirror.get('select_dst_port'))
            mirror['output_port'] = self.resolve_port(mirror.get('output_port'))
            mirrors.append(mirror)
        return mirrors

    def resolve_ports(self, port_set):
        """
        Given a port set, returns a list of port names.
        """
        port_names = []
        if not port_set or port_set == ['set', []]:
            return port_names
        if port_set[0] == 'set':
            ports = port_set[1]
        else:
            ports = [port_set]

        for port in ports:
            if port[0] == 'uuid':
                port_uuid = port[1]
                port_name = self.get_port_name(port_uuid)
                port_names.append(port_name)
        return port_names

    def resolve_port(self, port_ref):
        """
        Given a port reference, returns the port name.
        """
        if not port_ref or port_ref == ['uuid', '00000000-0000-0000-0000-000000000000']:
            return None
        if port_ref[0] == 'uuid':
            port_uuid = port_ref[1]
            return self.get_port_name(port_uuid)
        return None

    def get_port_name(self, port_uuid):
        """
        Retrieves the port name given its UUID.
        """
        command = f'get Port {port_uuid} name'
        try:
            result = self.vsctl.run(command=command, parser=None)
            port_name = result.stdout.read().strip().strip('"')
            return port_name
        except Exception as e:
            print(f"Error fetching port name for UUID {port_uuid}: {e}")
            return port_uuid
