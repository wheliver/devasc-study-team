from ncclient import manager
import xml.dom.minidom

# Parámetros de conexión al dispositivo
with manager.connect(
        host="sandbox-iosxr-1.cisco.com",
        port=830,
        username="admin",
        password="C1sco12345",
        hostkey_verify=False
) as m:
    # Configuración de Loopback10
    netconf_loopback10 = """
    <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <interface-configurations xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg">
            <interface-configuration>
                <active>act</active>
                <interface-name>Loopback100</interface-name>
                <description>Wheliver NETCONF Loopback100</description>
                <ipv4-network xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ipv4-io-cfg">
                    <addresses>
                        <primary>
                            <address>172.16.100.1</address>
                            <netmask>255.255.255.0</netmask>
                        </primary>
                    </addresses>
                </ipv4-network>
            </interface-configuration>
        </interface-configurations>
    </config>
    """
    try:
        # Enviamos la configuración de Loopback10 al dispositivo
        netconf_reply = m.edit_config(target="candidate", config=netconf_loopback10)
        # Realizamos el commit de la configuración
        m.commit()
        # Imprimir la respuesta de la configuración aplicada en formato XML legible
        print(xml.dom.minidom.parseString(netconf_reply.xml).toprettyxml())
    except Exception as e:
        # Imprimir el error si ocurre alguno
        print(f"Error: {e}")
