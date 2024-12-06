from nornir import InitNornir
from nornir_netmiko import netmiko_send_config
import csv
from jinja2 import Template
from nornir_utils.plugins.functions import print_result, print_title

# Inicializar Nornir usando la configuración del archivo config.yaml
nr = InitNornir(config_file="/home/wheliver/labs/jinja2/config.yaml")

# Archivo CSV con los datos de las interfaces
source_file = "/home/wheliver/labs/jinja2/router_interfaces.csv"

# Archivo de plantilla Jinja2
interface_template_file = "/home/wheliver/labs/jinja2/interface_config_template.j2"

# String que contendrá la configuración final de todas las interfaces
interface_configs = ""

# Leer la plantilla Jinja2 y crear un objeto Template
with open(interface_template_file) as f:
    interface_template = Template(f.read(), keep_trailing_newline=True)

# Leer el archivo CSV con los datos de las interfaces
with open(source_file) as f:
    reader = csv.DictReader(f)
    for row in reader:
        interface_config = interface_template.render(
            interface=row["Interface"],
            IP_Address=row["IP_Address"],
            Subnet_Mask=row["Subnet_Mask"],
            Description=row["Description"],
            Static_Route=row.get("Static_Route"),
            Routing_Protocol=row.get("Routing_Protocol")
        )
        interface_configs += interface_config

# Guardar la configuración final en un archivo de salida
with open("generated_interface_configs.txt", "w") as f:
    f.write(interface_configs)

print("Archivo de configuraciones generado con éxito")

# Función de Nornir para aplicar configuraciones
def apply_config(task):
    config = interface_configs  # Usar la configuración generada
    try:
        # Enviar la configuración al dispositivo
        result = task.run(task=netmiko_send_config, config_commands=config.split('\n'))
        print(f"Configuración aplicada a {task.host.name}: {result.result}")
    except Exception as e:
        print(f"Error al aplicar la configuración a {task.host.name}: {e}")

# Ejecutar la tarea de aplicar configuraciones en los routers
print_title("Aplicando configuraciones a los routers")
results = nr.run(task=apply_config)
print_result(results)