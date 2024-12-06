from netmiko import ConnectHandler
from jinja2 import Environment, FileSystemLoader
from getpass import getpass
import logging
import json

# Configuración de logging
logging.basicConfig(filename='port_security.log', level=logging.INFO, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Parámetros del dispositivo predeterminados
default_router = {
    "device_type": "cisco_ios_telnet",
    "host": "192.168.100.121",
    "port": 33286,
    "username": "wheliver",
    "password":"class",  # Se llenará más adelante si se elige usar por defecto
    "timeout": 100,  # Incrementa el tiempo de espera
    "fast_cli": False,  # Evita que Netmiko intente ser muy rápido al ejecutar comandos
    "secret": "pucmm1",  # Se llenará más adelante si se elige usar por defecto
    "global_delay_factor": 2  # Aumenta el tiempo de espera para procesos más lentos
}

# Solicitar la información del dispositivo al usuario
def get_device_info():
    use_default = input("¿Deseas usar la configuración por defecto? (s/n): ").lower()
    
    if use_default == 's':

       # default_router['password'] = getpass()
        #default_router['secret'] = getpass("Ingrese el enable password predeterminado: ")
        return default_router
    else:
        # Solicitar los datos al usuario
        device_info = {
            "device_type": "cisco_ios_telnet",
            "host": input("Ingrese el host: "),
            "port": int(input("Ingrese el puerto (default: 23): ") or 23),  # Usa el puerto 23 si no se ingresa ninguno
            "username": input("Ingrese el nombre de usuario: "),
            "password": getpass("Ingrese la contraseña: "),
            "timeout": 100,
            "fast_cli": False,  # Evita que Netmiko intente ser muy rápido
            "secret": getpass("Ingrese el enable password: ")
        }
        return device_info

# Conectar al dispositivo de red con validación de errores
def connect_to_device(device_params):
    try:
        net_connect = ConnectHandler(**device_params)
        net_connect.enable()  # Modo enable si es necesario
        print(f"Conectado al dispositivo {device_params['host']} con éxito.")
        logging.info(f"Conectado al dispositivo {device_params['host']} con éxito.")
        return net_connect
    except Exception as e:
        print(f"Error al conectar al dispositivo: {e}")
        logging.error(f"Error al conectar al dispositivo: {e}")
        raise e

# Obtener una lista de los puertos del dispositivo
def get_device_ports(connection):
    try:
        output = connection.send_command("show ip interface brief")
        logging.info(f"Puertos disponibles:\n{output}")
        print("Puertos disponibles:\n", output)
        
        # Extraer los nombres de las interfaces
        ports = []
        for line in output.splitlines()[1:]:  # Omitir la primera línea de encabezado
            if line:
                port = line.split()[0]
                ports.append(port)
        return ports
    except Exception as e:
        print(f"Error al obtener la lista de puertos: {e}")
        logging.error(f"Error al obtener la lista de puertos: {e}")
        raise e

# Cargar configuración de puertos desde archivo JSON
def load_port_config():
    try:
        with open('ports_config.json', 'r') as file:
            config = json.load(file)
        logging.info("Configuración de puertos cargada exitosamente.")
        print("Configuración de puertos cargada exitosamente.")
        return config
    except Exception as e:
        print(f"Error al cargar la configuración de puertos: {e}")
        logging.error(f"Error al cargar la configuración de puertos: {e}")
        raise e

# Cargar la plantilla con Jinja2
def load_template(port, allowed_mac_list, denied_mac_list, permit_all, deny_all):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('port_security_template.j2')
    return template.render(port=port, 
                           allowed_mac_list=allowed_mac_list, 
                           denied_mac_list=denied_mac_list,
                           permit_all=permit_all,
                           deny_all=deny_all)

# Configurar seguridad en puerto basado en las reglas
def configure_port_security(connection, port, allowed_mac, denied_mac, permit_all, deny_all):
    try:
        config_commands = load_template(port, allowed_mac, denied_mac, permit_all, deny_all)
        connection.send_config_set(config_commands.split('\n') ,read_timeout=100)
        print(f"Configuración aplicada al puerto {port}.")
        logging.info(f"Configuración aplicada al puerto {port}.")
    except Exception as e:
        print(f"Error al aplicar configuración en {port}: {e}")
        logging.error(f"Error al aplicar configuración en {port}: {e}")
        raise e



# Verificación de configuración aplicada correctamente (con show running-config)
def verify_port_security(connection, port):
    try:
        # Verifica la configuración de la interfaz con show running-config
        output = connection.send_command(f"show running-config interface {port}")
        print(f"Configuración actual de {port}:\n{output}")
        logging.info(f"Configuración actual de {port}:\n{output}")
        return output
    except Exception as e:
        print(f"Error al verificar la configuración del puerto {port}: {e}")
        logging.error(f"Error al verificar la configuración del puerto {port}: {e}")
        raise e




# Función principal
def main():
    try:
        # Obtener la información del dispositivo
        device = get_device_info()
        print(device)
    
        # Conectar al dispositivo
        net_connect = connect_to_device(device)

        # Obtener los puertos disponibles en el dispositivo
        device_ports = get_device_ports(net_connect)
        print(f"Puertos en el dispositivo: {device_ports}")

        # Cargar la configuración de puertos desde archivo JSON
        port_config = load_port_config()

        # Verificar si los puertos en la lista JSON están en el dispositivo
        for port in port_config.keys():
            if port not in device_ports:
                print(f"Advertencia: El puerto {port} no está en el dispositivo.")
            else:
                print(f"Puerto {port} encontrado en el dispositivo, aplicando configuración.")
                settings = port_config[port]
                configure_port_security(
                    net_connect, 
                    port, 
                    settings['allowed_mac'], 
                    settings['denied_mac'], 
                    settings['permit_all'], 
                    settings['deny_all']
                )
                verify_port_security(net_connect, port)

        net_connect.disconnect()
        print("Proceso completado exitosamente.")
        logging.info("Proceso completado exitosamente.")
    except Exception as e:
        print(f"Error durante el proceso principal: {e}")
        logging.error(f"Error durante el proceso principal: {e}")

if __name__ == '__main__':
    main()
