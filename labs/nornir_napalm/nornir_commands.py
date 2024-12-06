from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir_netmiko import netmiko_send_command

# Inicializa Nornir con el archivo de configuración
nr = InitNornir(config_file="config.yaml")

# Ejecuta el comando en todos los dispositivos
result = nr.run(
    task=netmiko_send_command,
    command_string="show ip int br"
)

# Muestra el resultado
print_result(result)