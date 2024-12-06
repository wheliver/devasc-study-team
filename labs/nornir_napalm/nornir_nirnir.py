from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_utils.plugins.functions import print_result
from nornir_napalm.plugins.tasks import napalm_get



# Función para enviar un comando a través de NAPALM
def send_command(task: Task) -> Result:
    # Recuperar información usando NAPALM
    result = task.run(task=napalm_get, getters=["facts", "interfaces"])
    return Result(host=task.host, result=result)

# Inicializar Nornir
nr = InitNornir(config_file="config.yaml")

# Ejecutar la tarea en todos los hosts
result = nr.run(task=send_command)

# Mostrar los resultados
print_result(result)