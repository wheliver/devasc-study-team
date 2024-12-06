#! /usr/bin/env python
"""
Demo script showing how to create network configurations by combining data from CSV files with Jinja templates. 
"""

import csv
from jinja2 import Template
from nornir import InitNornir
from nornir_netmiko import netmiko_send_config, netmiko_send_command
from nornir.core.filter import F
from nornir_utils.plugins.functions import print_result, print_title

source_file = "switchport.csv"
interface_template_file = "switchport-interface-template.j2"

# String that will hold final full configuration of all interfaces
interface_configs = ""

# Open up the Jinja template file (as text) and then create a Jinja Template Object 
with open(interface_template_file) as f:
    interface_template = Template(f.read(), keep_trailing_newline=True)

# Open up the CSV file containing the data 
with open(source_file) as f:
    # Use DictReader to access data from CSV 
    reader = csv.DictReader(f)
    # For each row in the CSV, generate an interface configuration using the jinja template 
    for row in reader:
        interface_config = interface_template.render(
            interface = row["Interface"],
            vlan = row["VLAN"],
            server = row["Server"],
            link = row["Link"],
            purpose = row["Purpose"]
        )

        # Append this interface configuration to the full configuration 
        interface_configs += interface_config

# Save the final configuraiton to a file 
with open("interface_configs.txt", "w") as f:
    f.write(interface_configs)
print("Archivo de configuracion Generado")

nr = InitNornir(config_file="config.yaml")


def config(task):
    
    # Ejecuta la tarea de enviar configuración desde un archivo
    task.run(task=netmiko_send_config, config_file="interface_configs.txt")
    
    # Ejecuta la tarea de enviar un comando específico
    #task.run(task=netmiko_send_command, command_string="show run | begin line")
    
    # Ejecuta la tarea de guardar la configuración en memoria
    #task.run(task=netmiko_send_command, command_string="write memory")

# Filtra los dispositivos en función del grupo "Juan"
devices = nr.filter(F(groups__contains="Juan") and F(groups__contains="Switches"))

# Ejecuta la función "config" en los dispositivos filtrados
results = devices.run(task=config)

# Imprime un título para indicar el despliegue de la configuración
print_title("Realizando la configuracion")

# Imprime los resultados de las tareas en los dispositivos
print_result(results)
