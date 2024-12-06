from netmiko import ConnectHandler
from getpass import getpass

router = {
    "device_type": "cisco_ios_telnet",
    "host": "192.168.100.121",
    "port": 33310,
    "username": "wheliver",
    "password": "class",#getpass(),
    "timeout": 100,  # Incrementa el tiempo de espera
    "fast_cli": False, # Evita que Netmiko intente ser muy rápido al ejecutar comandos
    "secret":"pucmm1",# getpass("Ingrese el enable password: ")
}


config_commands = [
    'interface loopback 0',
    'ip address 10.0.0.1 255.255.255.0',
    'description Creado por Wheliver '
]

with ConnectHandler(**router) as net_connect:
    net_connect.enable()  # Entra en modo privilegiado
    output = net_connect.send_config_set(config_commands)


print(output)
