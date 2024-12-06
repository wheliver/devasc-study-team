import logging


def parse_stp(output):
    """
    Analiza la salida del comando `show spanning-tree` y extrae información clave,
    incluyendo Root ID, Bridge ID y configuración general de STP.
    """
    stp_data = {
        "root_bridge": {"priority": None, "mac": None, "cost": None, "port": None},
        "local_bridge": {"priority": None, "mac": None, "is_root": False},
        "vlans": {},
        "hello_time": None,
        "max_age": None,
        "forward_delay": None,
        "aging_time": None
    }

    lines = output.splitlines()
    current_vlan = None

    for line in lines:
        line = line.strip()
        if not line:
            continue  # Ignorar líneas vacías

        try:
            # Extraer información del Root ID
            if "Root ID" in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "Priority":
                        stp_data["root_bridge"]["priority"] = parts[i + 1]
                    elif part == "Address":
                        stp_data["root_bridge"]["mac"] = parts[i + 1]
                    elif part == "Cost":
                        stp_data["root_bridge"]["cost"] = parts[i + 1]
                    elif part == "Port":
                        stp_data["root_bridge"]["port"] = parts[i + 1]

            # Extraer información del Bridge ID
          # Extraer información del Bridge ID
            if "Bridge ID" in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "Priority":
                        stp_data["local_bridge"]["priority"] = parts[i + 1]
                    elif part == "Address":
                        stp_data["local_bridge"]["mac"] = parts[i + 1]


            # Identificar si este bridge es root y agregar información completa
            elif "This bridge is the root" in line:
                stp_data["local_bridge"]["is_root"] = True

            # Extraer configuraciones de tiempos
            elif "Hello Time" in line:
                parts = line.split()
                stp_data["hello_time"] = parts[2]
                stp_data["max_age"] = parts[5]
                stp_data["forward_delay"] = parts[8]

            elif "Aging Time" in line:
                parts = line.split()
                stp_data["aging_time"] = parts[2]

            # Capturar información de la VLAN actual
            elif "VLAN" in line:
                current_vlan = line.split()[-1]
                stp_data["vlans"][current_vlan] = {"ports": []}

            # Procesar tabla de interfaces de la VLAN actual
            elif current_vlan and len(line.split()) >= 6:
                if "Interface" in line or "----" in line:
                    continue

                port_info = line.split()
                stp_data["vlans"][current_vlan]["ports"].append({
                    "port": normalize_interface_name(port_info[0]),
                    "role": port_info[1],
                    "state": port_info[2],
                    "cost": port_info[3],
                    "priority": port_info[4],
                    "type": port_info[5]
                })

        except Exception as e:
            logging.error(f"Error procesando línea: {line}, Error: {e}")

    return stp_data


def normalize_interface_name(interface):
    """
    Normaliza el nombre de una interfaz para que coincida en diferentes formatos.
    """
    try:
        # Eliminar espacios y normalizar prefijos comunes
        interface = interface.strip().replace(" ", "").replace("Ethernet", "Et").replace(
            "FastEthernet", "Fa").replace("GigabitEthernet", "Gi").replace("TenGigabitEthernet", "Te")
        return interface
    except Exception as e:
        logging.error(f"Error normalizando interfaz: {interface}, Error: {e}")
        return interface


def parse_cdp_neighbors(cdp_output):
    """
    Parsea la salida del comando `show cdp neighbors` y extrae información clave.
    """
    neighbors = []
    lines = cdp_output.splitlines()
    header_index = -1

    # Buscar la cabecera (Device ID, Local Intrfce, etc.)
    for i, line in enumerate(lines):
        if "Device ID" in line and "Local Intrfce" in line:
            header_index = i
            break

    if header_index == -1:
        logging.warning("No se encontraron cabeceras en la salida de CDP.")
        print("No se encontraron cabeceras en la salida de CDP.")
        return neighbors

    print(f"Cabeceras detectadas: {lines[header_index]}")

    # Procesar cada línea después de la cabecera
    for line in lines[header_index + 1:]:
        parts = line.split()
        print(f"Línea procesada: {line}")
        print(f"Partes extraídas: {parts}")

        if len(parts) < 6:
            print(f"Línea ignorada (no tiene suficientes columnas): {line}")
            continue

        try:
            neighbor_data = {
                "device_id": parts[0],
                "local_interface": parts[1]+normalize_interface_name(parts[2]),
                "holdtime": parts[3],
                "capability": " ".join(parts[4:-2]),
                "platform": parts[-2],
                "remote_interface": parts[-2]+normalize_interface_name(parts[-1])
            }
            print(f"Vecino procesado: {neighbor_data}")
            neighbors.append(neighbor_data)
        except Exception as e:
            logging.error(f"Error procesando vecino CDP: {line}, Error: {e}")
            print(f"Error procesando vecino CDP: {line}, Error: {e}")

    return neighbors


logging.info("STP utilities updated successfully.")
def normalize_interface_name(interface):
    """
    Normaliza el nombre de una interfaz para que coincida en diferentes formatos.
    """
    try:
        return (
            interface.strip()
            .replace(" ", "")
            .replace("Eth", "Et")
            .replace("Ethernet", "Et")
            .replace("FastEthernet", "Fa")
            .replace("GigabitEthernet", "Gi")
            .replace("TenGigabitEthernet", "Te")
        )
    except Exception as e:
        logging.error(f"Error normalizando interfaz: {interface}, Error: {e}")
        return interface
