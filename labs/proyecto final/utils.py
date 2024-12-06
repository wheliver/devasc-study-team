import logging
import json
from netmiko import ConnectHandler
from stp_utils import normalize_interface_name

def setup_logging(log_file):
    """
    Configura el sistema de logging para registrar mensajes en un archivo.
    """
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s:%(levelname)s:%(message)s",
    )
    print(f"Logging configurado. Los eventos se registrarán en {log_file}")

def validate_bidirectional_connection(device, neighbor):
    """
    Valida que la conexión entre dos dispositivos sea consistente.
    """
    try:
        return any(
            n.get("device_id") == device["hostname"]
            and normalize_interface_name(n.get("local_interface")) == normalize_interface_name(neighbor.get("remote_port"))
            and normalize_interface_name(n.get("remote_interface")) == normalize_interface_name(neighbor.get("local_port"))
            for n in device.get("cdp_neighbors", [])
        )
    except Exception as e:
        logging.error(f"Error validando conexión bidireccional: {e}")
        return False


def final_export_topology_with_details(stp_network_map, output_file):
    """
    Exporta la topología STP con detalles completos, incluyendo Root ID, Bridge ID, roles,
    validación de conexiones bidireccionales y datos de los vecinos.
    """
    try:
        topology_tree = {"root": None, "switches": []}

        def validate_bidirectional_connection(device, neighbor):
            """
            Valida que la conexión entre dos dispositivos sea consistente.
            """
            return any(
                n.get("device_id") == device["hostname"]
                and n.get("local_interface") == neighbor.get("remote_port")
                and n.get("remote_interface") == neighbor.get("local_port")
                for n in device.get("cdp_neighbors", [])
            )

        for device, data in stp_network_map.items():
            stp_data = data.get("stp_data", {})
            vlans = stp_data.get("vlans", {})
            hostname = data.get("hostname", "unknown")
            ip = data.get("ip", "unknown")


            device_info = {
                "hostname": hostname,
                "ip": ip,
                "priority": stp_data["local_bridge"].get("priority", "unknown"),
                "mac": stp_data["local_bridge"].get("mac", "unknown"),
                "bridge_id": stp_data["local_bridge"],
                "root_id": stp_data["root_bridge"],
                "connections": [],
                "inter_switch_links": []
            }

            # Si el dispositivo es root, incluir toda su información
            if stp_data["local_bridge"].get("is_root", False):
                device_info["is_root"] = True
                topology_tree["root"] = device_info

            # Procesar conexiones y enlaces inter-switch
            for vlan, vlan_data in vlans.items():
                for port_info in vlan_data.get("ports", []):
                    connection = {
                        "connected_to": port_info.get("connected_to", "unknown"),
                        "via_port": port_info.get("port", "unknown"),
                        "remote_port": port_info.get("remote_port", "unknown"),
                        "vlan": vlan,
                        "role": port_info.get("role", "unknown"),
                        "state": port_info.get("state", "unknown"),
                        "platform": port_info.get("platform", "unknown"),
                        "capability": port_info.get("capability", "unknown")
                    }
                    device_info["connections"].append(connection)

            # Validar y agregar enlaces inter-switch
            cdp_neighbors = data.get("cdp_neighbors", [])
            for neighbor in cdp_neighbors:
                if validate_bidirectional_connection(data, neighbor):
                    inter_switch_link = {
                        "connected_to": neighbor.get("device_id", "unknown"),
                        "local_port": neighbor.get("local_interface", "unknown"),
                        "remote_port": neighbor.get("remote_interface", "unknown"),
                        "role": next(
                            (p.get("role", "unknown") for vlan_data in vlans.values()
                             for p in vlan_data.get("ports", [])
                             if p.get("port") == neighbor.get("local_interface")),
                            "unknown"
                        )
                    }
                    device_info["inter_switch_links"].append(inter_switch_link)

            topology_tree["switches"].append(device_info)

        # Exportar la topología final al archivo especificado
        with open(output_file, 'w') as f:
            json.dump(topology_tree, f, indent=4)
        print(f"Topología final exportada correctamente a {output_file}")
    except Exception as e:
        logging.error(f"Error al exportar la topología final: {e}")


def connect_to_device(host, port, device_config):
    """
    Conecta a un dispositivo de red y devuelve la conexión activa.
    """
    try:
        print(f"Intentando conectar al dispositivo {host}:{port}...")
        device_config.update({"host": host, "port": port})
        connection = ConnectHandler(**device_config)
        connection.enable()
        logging.info(f"Conectado al dispositivo {host}:{port}")
        return connection
    except Exception as e:
        logging.error(f"Error al conectar al dispositivo {host}:{port}: {e}")
        return None
