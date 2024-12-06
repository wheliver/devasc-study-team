from config import LOG_FILE, OUTPUT_FILE, DEFAULT_DEVICE
from utils import connect_to_device
from stp_utils import parse_cdp_neighbors, parse_stp, normalize_interface_name
import logging

# Variable global para almacenar la red STP
stp_network_map = {}
visited_devices = set()


def collect_device_data(connection, host, port):
    """
    Recoge datos de STP y CDP de un dispositivo sin procesar las conexiones.
    """
    try:
        logging.info(f"Recogiendo datos de STP y CDP de {host}:{port}...")

        # Recoger datos de STP
        stp_output = connection.send_command("show spanning-tree")
        stp_data = parse_stp(stp_output)

        # Recoger datos de CDP
        cdp_output = connection.send_command("show cdp neighbors")
        neighbors_data = parse_cdp_neighbors(cdp_output)
    # Recoger dirección MAC
        mac_output = connection.send_command("show version | include Base Ethernet MAC Address")
        mac_address = "unknown"
        for line in mac_output.splitlines():
            if "Base Ethernet MAC Address" in line:
                mac_address = line.split(":")[-1].strip()
                break

        # Recoger IP real
        ip_output = connection.send_command("show ip interface brief")
        ip_address = "unknown"
        for line in ip_output.splitlines():
            if "up" in line.lower() and "protocol" in line.lower():  # Filtrar interfaces activas
                parts = line.split()
                if len(parts) > 1:
                    ip_address = parts[1]  # Asumimos que la IP está en la segunda columna
                    break
        return {
            "stp_data": stp_data,
            "cdp_neighbors": neighbors_data,
            "hostname": connection.find_prompt().strip("#"),
            "ip": ip_address,
            "mac": mac_address,
        }
    except Exception as e:
        logging.error(f"Error al recoger datos de {host}:{port}: {e}")
        return None

def clean_up_connections():
    """
    Limpia conexiones redundantes, no válidas o no reconocibles.
    """
    global stp_network_map

    for device_id, device_data in stp_network_map.items():
        hostname = device_data.get("hostname", "unknown")
        valid_connections = []

        for connection in device_data.get("connections", []):
            connected_to = connection.get("connected_to", "unknown")
            remote_port = connection.get("remote_port", "unknown")

            # Validar si la conexión es válida
            if connected_to != "unknown" and remote_port != "unknown" and connected_to != hostname:
                valid_connections.append(connection)
            else:
                print(f"[Debug] Eliminando conexión no válida o redundante: {connection}")

        # Reemplazar conexiones con la lista filtrada
        device_data["connections"] = valid_connections

    print("\n=== Limpieza de conexiones completada ===\n")


def process_connections():
    """
    Procesa las conexiones entre dispositivos utilizando los datos recogidos.
    """
    print("\n=== Iniciando el procesamiento de conexiones ===\n")

    for device_id, device_data in stp_network_map.items():
        hostname = device_data.get("hostname", "unknown")
        stp_data = device_data.get("stp_data", {})
        vlans = stp_data.get("vlans", {})

        print(f"Procesando dispositivo: {hostname} ({device_id})")

        for vlan, vlan_data in vlans.items():
            print(f"\n--- VLAN: {vlan} ---")
            for port_info in vlan_data.get("ports", []):
                local_port = normalize_interface_name(port_info["port"])
                print(f"Puerto local normalizado: {local_port}")

                for other_device_id, other_device_data in stp_network_map.items():
                    if device_id == other_device_id:
                        continue

                    for neighbor in other_device_data.get("cdp_neighbors", []):
                        neighbor_device_id = neighbor["device_id"]
                        neighbor_remote_port = normalize_interface_name(neighbor["remote_interface"])
                        neighbor_local_port = normalize_interface_name(neighbor["local_interface"])

                        # Validar conexión bidireccional
                        if (
                            neighbor_device_id == hostname and
                            neighbor_remote_port == local_port and
                            other_device_data["hostname"] != hostname
                        ):
                            print(f"¡Conexión detectada entre {hostname} y {other_device_data['hostname']}!")

                            # Actualizar la conexión del dispositivo actual
                            port_info.update({
                                "connected_to": other_device_data["hostname"],
                                "via_port": local_port,
                                "remote_port": neighbor_local_port,
                                "holdtime": neighbor.get("holdtime"),
                                "capability": neighbor.get("capability"),
                                "platform": neighbor.get("platform"),
                            })

                            # Añadir conexión a inter-switch links si corresponde
                            if "inter_switch_links" in device_data:
                                device_data["inter_switch_links"].append({
                                    "connected_to": other_device_data["hostname"],
                                    "local_port": local_port,
                                    "remote_port": neighbor_local_port,
                                })
                            break

    print("\n=== Procesamiento de conexiones finalizado ===\n")

    # Realizar limpieza de conexiones al final
    clean_up_connections()
    print("\n=== Limpieza de conexiones completada ===\n")


def map_stp_network(devices):
    """
    Mapea la configuración STP para todos los dispositivos en la lista.
    """
    global stp_network_map, visited_devices

    # Paso 1: Recoger datos de todos los dispositivos
    for device in devices:
        host = device["host"]
        port = device.get("port", 23)
        unique_id = f"{host}:{port}"

        if unique_id in visited_devices:
            logging.info(f"{unique_id} ya fue visitado. Saltando...")
            continue
        visited_devices.add(unique_id)

        logging.info(f"Conectando a {host}:{port}...")

        # Configuración del dispositivo y aplicar configuraciones predeterminadas
        device_config = {**DEFAULT_DEVICE, **device}
        device_config["port"] = port

        try:
            connection = connect_to_device(host, port, device_config)

            if connection:
                device_data = collect_device_data(connection, host, port)
                if device_data:
                    stp_network_map[unique_id] = device_data
                connection.disconnect()
                logging.info(f"Desconexión exitosa de {unique_id}")
            else:
                logging.error(f"No se pudo conectar a {unique_id}")

        except Exception as e:
            logging.error(f"Error durante la conexión con {unique_id}: {e}")

    # Paso 2: Procesar conexiones después de recoger todos los datos
    process_connections()
