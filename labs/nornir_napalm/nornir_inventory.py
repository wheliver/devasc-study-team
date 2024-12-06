from nornir import InitNornir
from nornir_utils.plugins.functions import print_result

# Inicializa Nornir con el archivo de configuración
nr = InitNornir(config_file="config.yaml")

# Muestra el inventario de dispositivos
print(nr.inventory.hosts)