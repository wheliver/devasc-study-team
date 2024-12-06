from config import LOG_FILE, OUTPUT_FILE, DEFAULT_DEVICE
from utils import setup_logging, final_export_topology_with_details
from discovery import map_stp_network, stp_network_map
import json


def load_devices_from_file(file_path):
    """
    Carga la lista de dispositivos desde un archivo JSON.
    """
    try:
        with open(file_path, 'r') as f:
            devices = json.load(f)
        print(f"Dispositivos cargados desde {file_path}: {len(devices)} dispositivos encontrados.")
        return devices
    except Exception as e:
        print(f"Error al cargar dispositivos desde {file_path}: {e}")
        return []


def main():
    """
    Programa principal para mapear y exportar la red STP.
    """
    try:
        # Configurar logging
        setup_logging(LOG_FILE)

        # Ruta fija para el archivo JSON de dispositivos
        devices_file = "/home/wheliver/labs/proyecto final/devices.json"
        devices = load_devices_from_file(devices_file)

        if not devices:
            print("No hay dispositivos válidos para mapear.")
            return

        # Iniciar el mapeo de la red STP
        print("Iniciando el mapeo de la red STP...")
        map_stp_network(devices)

        # Exportar la topología final a un archivo JSON detallado
        print(f"Exportando topología a {OUTPUT_FILE}...")
        final_export_topology_with_details(stp_network_map, OUTPUT_FILE)

        print("Proceso completado. Revisa el archivo exportado para más detalles.")

    except Exception as e:
        print(f"Error en el proceso principal: {e}")


if __name__ == "__main__":
    main()
