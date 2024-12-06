# Script para practicar configuraciones NETCONF y verificaciones con ncclient

from ncclient import manager, xml_
import xml.dom.minidom

# Información del dispositivo
HOST = "sandbox-iosxr-1.cisco.com"
PORT = 830
USERNAME = "admin"
PASSWORD = "C1sco12345"

# 1. Mostrar capacidades YANG del dispositivo
def show_capabilities():
    """
    Esta función se conecta al dispositivo y lista todas las capacidades YANG
    soportadas, que indican los modelos disponibles para configurar.
    """
    with manager.connect(
        host=HOST,
        port=PORT,
        username=USERNAME,
        password=PASSWORD,
        hostkey_verify=False
    ) as m:
        print("# Modelos YANG soportados por el dispositivo:")
        for capability in m.server_capabilities:
            print(capability)

# 2. Configurar una interfaz Loopback con NETCONF
def configure_loopback(loopback_id, address, netmask, description):
    """
    Configura una interfaz Loopback en el dispositivo.
    Parámetros:
        loopback_id: ID de la interfaz Loopback (por ejemplo, 10).
        address: Dirección IP a asignar a la interfaz.
        netmask: Máscara de red de la interfaz.
        description: Descripción para la interfaz.
    """
    loopback_config = f"""
    <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <interface-configurations xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg">
            <interface-configuration>
                <active>act</active>
                <interface-name>Loopback{loopback_id}</interface-name>
                <description>{description}</description>
                <ipv4-network xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ipv4-io-cfg">
                    <addresses>
                        <primary>
                            <address>{address}</address>
                            <netmask>{netmask}</netmask>
                        </primary>
                    </addresses>
                </ipv4-network>
            </interface-configuration>
        </interface-configurations>
    </config>
    """

    with manager.connect(
        host=HOST,
        port=PORT,
        username=USERNAME,
        password=PASSWORD,
        hostkey_verify=False
    ) as m:
        try:
            print(f"# Configurando Loopback{loopback_id}...")
            netconf_reply = m.edit_config(target="candidate", config=loopback_config)
            m.commit()
            print(xml.dom.minidom.parseString(netconf_reply.xml).toprettyxml())
        except Exception as e:
            print(f"Error al configurar Loopback{loopback_id}: {e}")

# 3. Verificar la configuración de una Loopback
def verify_loopback(loopback_id):
    """
    Verifica la configuración de una interfaz Loopback específica.
    Parámetros:
        loopback_id: ID de la interfaz Loopback a verificar.
    """
    filter_config = f"""
    <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <interface-configurations xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg">
            <interface-configuration>
                <interface-name>Loopback{loopback_id}</interface-name>
            </interface-configuration>
        </interface-configurations>
    </filter>
    """

    with manager.connect(
        host=HOST,
        port=PORT,
        username=USERNAME,
        password=PASSWORD,
        hostkey_verify=False
    ) as m:
        try:
            print(f"# Verificando configuración de Loopback{loopback_id}...")
            netconf_reply = m.get_config(source="running", filter=filter_config)
            print(xml.dom.minidom.parseString(netconf_reply.xml).toprettyxml())
        except Exception as e:
            print(f"Error al verificar Loopback{loopback_id}: {e}")

# 4. Guardar la configuración del dispositivo (alternativa)
def save_config_alternative():
    """
    Realiza un commit en IOS XR para asegurar que los cambios sean persistentes.
    """
    with manager.connect(
        host=HOST,
        port=PORT,
        username=USERNAME,
        password=PASSWORD,
        hostkey_verify=False
    ) as m:
        try:
            print("# Guardando configuración (commit)...")
            m.commit()
            print("Configuración guardada exitosamente.")
        except Exception as e:
            print(f"Error al guardar configuración (commit): {e}")

# 5. Ejecución del script
def main():
    """
    Punto de entrada principal del script. Ejecuta las funciones en secuencia.
    """
    print("\n### Listando capacidades del dispositivo ###")
    show_capabilities()

    print("\n### Configurando una nueva interfaz Loopback ###")
    configure_loopback(10, "10.10.10.10", "255.255.255.0", "Wheliver Loopback10")

    print("\n### Verificando la configuración de la interfaz Loopback ###")
    verify_loopback(10)

    print("\n### Guardando la configuración ###")
    save_config_alternative()

if __name__ == "__main__":
    main()
