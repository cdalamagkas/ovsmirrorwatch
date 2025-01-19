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
        Create a port mirror in a single ovs-vsctl transaction.

        Parameters:
            mirror_name (str): Name of the mirror.
            bridge_name (str): Name of the bridge to attach the mirror to.
            select_src_ports (list): List of source port names to mirror.
            select_dst_ports (list): List of destination port names to mirror.
            output_port (str): Name of the output port.

        Returns:
            True if successful, False otherwise.
        """
        try:
            # Set Bridge
            cmd_parts = [f"-- set Bridge {bridge_name} mirrors=@m"]
            
            for idx, port_name in enumerate(select_src_ports or []):
                cmd_parts.append(f"-- --id=@src{idx} get Port {port_name}")

            
            for idx, port_name in enumerate(select_dst_ports or []):
                cmd_parts.append(f"-- --id=@dst{idx} get Port {port_name}")
            
            if output_port:
                cmd_parts.append(f"-- --id=@out get Port {output_port}")

            # Create Mirror
            mirror_create = [f"-- --id=@m create Mirror name={mirror_name}"]

            # Attach source ports
            if select_src_ports:
                src_refs = ",".join(f"@src{idx}" for idx in range(len(select_src_ports)))
                mirror_create.append(f"select-src-port=[{src_refs}]")

            # Attach destination ports
            if select_dst_ports:
                dst_refs = ",".join(f"@dst{idx}" for idx in range(len(select_dst_ports)))
                mirror_create.append(f"select-dst-port=[{dst_refs}]")

            # Attach output port
            if output_port:
                mirror_create.append("output-port=@out")

            # Combine all Mirror fields into one
            cmd_parts.append(" ".join(mirror_create))

            # Build the full command (single transaction)
            full_command = " ".join(cmd_parts)
            # Example final command structure:
            # ovs-vsctl -- set Bridge vmbr5 mirrors=@m
            #            -- --id=@src0 get Port ens4f1
            #            -- --id=@out get Port tap111i1
            #            -- --id=@m create Mirror name=kali_mirror select-src-port=[@src0] output-port=@out

            print("Running single transaction:", full_command)
            self.vsctl.run(command=full_command, parser=None)

            print(f"Mirror '{mirror_name}' created successfully on bridge '{bridge_name}'.")
            return True

        except Exception as e:
            print(f"Error creating mirror '{mirror_name}': {e}")
            return False



    def destroy_mirror(self, mirror_name, bridge_name):
        """
        Destroy a port mirror by name on a given bridge.

        Parameters:
            mirror_name (str): Name of the mirror to destroy.
            bridge_name (str): Name of the bridge containing the mirror.
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Get all mirror UUIDs referenced by the Bridge
            command = f"get Bridge {bridge_name} mirrors"
            result = self.vsctl.run(command=command, parser=None)
            output = result.stdout.read()
            mirror_uuids = self.extract_uuids_from_output(output)

            if not mirror_uuids:
                print(f"No mirrors found on bridge '{bridge_name}'.")
                return False

            # Find the mirror whose 'name' matches mirror_name
            mirror_uuid_to_destroy = None
            for mirror_uuid in mirror_uuids:
                # For each Mirror UUID, get its 'name' column
                command = f"get Mirror {mirror_uuid} name"
                result = self.vsctl.run(command=command, parser=None)
                name = result.stdout.read().strip().strip('"')
                if name == mirror_name:
                    mirror_uuid_to_destroy = mirror_uuid
                    break

            if not mirror_uuid_to_destroy:
                print(f"Mirror '{mirror_name}' not found on bridge '{bridge_name}'.")
                return False

        # Remove the Mirror from the Bridge and destroy it in one transaction.
        # Using a single transaction ensures both actions happen together:
        #      remove Bridge <bridge_name> mirrors <mirror_uuid>
        #      destroy Mirror <mirror_uuid>
        # OVS ephemeral references are not needed here because we are 
        # referencing the actual UUID directly.
            combined_command = (
                f"-- remove Bridge {bridge_name} mirrors {mirror_uuid_to_destroy} "
                f"-- destroy Mirror {mirror_uuid_to_destroy}"
            )
            self.vsctl.run(command=combined_command, parser=None)

            print(f"Mirror '{mirror_name}' destroyed successfully.")
            return True

        except Exception as e:
            print(f"Error destroying mirror '{mirror_name}': {e}")
            return False


    def alter_mirror(self, mirror_name, bridge_name, select_src_ports=None, select_dst_ports=None, output_port=None):
        """
        Alter an existing port mirror in a single ovs-vsctl transaction.

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
            get_mirrors_cmd = f"get Bridge {bridge_name} mirrors"
            result = self.vsctl.run(command=get_mirrors_cmd, parser=None)
            output = result.stdout.read()
            mirror_uuids = self.extract_uuids_from_output(output)

            mirror_uuid = None
            for uuid in mirror_uuids:
                get_name_cmd = f"get Mirror {uuid} name"
                result = self.vsctl.run(command=get_name_cmd, parser=None)
                name = result.stdout.read().strip().strip('"')
                if name == mirror_name:
                    mirror_uuid = uuid
                    break

            if not mirror_uuid:
                print(f"Mirror '{mirror_name}' not found on bridge '{bridge_name}'.")
                return False

            # Build a single transaction (a single ovs-vsctl command)
            # that creates ephemeral references for the Port rows,
            # and then sets/clears the relevant columns on the Mirror.
            transaction_parts = []

            # Collect ephemeral references for select_src_ports
            # Example:   -- --id=@p0 get Port ens4f1
            src_refs = []
            if select_src_ports is not None:
                for idx, port_name in enumerate(select_src_ports):
                    transaction_parts.append(f"-- --id=@src{idx} get Port {port_name}")
                    src_refs.append(f"@src{idx}")

            # Collect ephemeral references for select_dst_ports
            dst_refs = []
            if select_dst_ports is not None:
                for idx, port_name in enumerate(select_dst_ports):
                    transaction_parts.append(f"-- --id=@dst{idx} get Port {port_name}")
                    dst_refs.append(f"@dst{idx}")

            # Collect ephemeral reference for output_port 
            has_output_port = (output_port is not None)  # i.e. user wants to set or clear
            if has_output_port and output_port:
                transaction_parts.append(f"-- --id=@out get Port {output_port}")

            # Now we’ll build "set Mirror <mirror_uuid> ..." or "clear Mirror <mirror_uuid> ..."
            # for each field the user wants to update (SRC, DST, OUTPUT)
            # We'll gather them in one or more "set/clear" lines.  
            # You can do them in multiple lines or combine them, but they must be in
            # the same transaction.

            # Update select_src_port in the same transaction
            if select_src_ports is not None:
                if src_refs:
                    # set Mirror <uuid> select_src_port=[@src0,@src1,...]
                    transaction_parts.append(
                        f"-- set Mirror {mirror_uuid} select_src_port=[{','.join(src_refs)}]"
                    )
                else:
                    # clear Mirror <uuid> select_src_port
                    transaction_parts.append(f"-- clear Mirror {mirror_uuid} select_src_port")

            # Update select_dst_port
            if select_dst_ports is not None:
                if dst_refs:
                    transaction_parts.append(
                        f"-- set Mirror {mirror_uuid} select_dst_port=[{','.join(dst_refs)}]"
                    )
                else:
                    transaction_parts.append(f"-- clear Mirror {mirror_uuid} select_dst_port")

            # Update output_port
            if has_output_port:
                if output_port:
                    # set Mirror <uuid> output_port=@out
                    transaction_parts.append(f"-- set Mirror {mirror_uuid} output_port=@out")
                else:
                    # clear Mirror <uuid> output_port
                    transaction_parts.append(f"-- clear Mirror {mirror_uuid} output_port")

            # Combine all into a single ovs-vsctl command
            full_command = " ".join(transaction_parts)
            # Example final structure:
            #   ovs-vsctl
            #     -- --id=@src0 get Port ens4f1
            #     -- --id=@dst0 get Port ens4f2
            #     -- --id=@out get Port tap111i1
            #     -- set Mirror <mirror_uuid> select_src_port=[@src0] select_dst_port=[@dst0] output_port=@out

            print("Running single-transaction command:", full_command)
            self.vsctl.run(command=full_command, parser=None)

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

