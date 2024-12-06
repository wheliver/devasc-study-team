from ncclient import manager
import xml.dom.minidom
with manager.connect(

        host="devnetsandboxiosxe.cisco.com",
        port=830,
        username="admin",
        password="C1sco12345",
        hostkey_verify=False

) as m:
#Para modificar la configuración del dispositivo (ejemplo: cambiar la descripcion de la GigabitEthernet1):
    netconf_interface = """

    <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">

        <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">

            <interface>

                <GigabitEthernet>

                    <name>1</name>

                    <description>Configurado por wheliver - Configurado via NETCONF</description>

                </GigabitEthernet>

            </interface>

        </native>

    </config>

    """

    # Enviamos la configuración al dispositivo (directamente al running)

    try:

        netconf_reply = m.edit_config(target="running", config=netconf_interface)
        # Imprimimos la respuesta de la configuración aplicada en formato XML legible
        print(xml.dom.minidom.parseString(netconf_reply.xml).toprettyxml())
    except Exception as e:
        # Imprimimos cualquier error que se produzca

        print(f"Error: {e}")
