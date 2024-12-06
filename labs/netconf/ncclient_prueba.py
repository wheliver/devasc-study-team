from ncclient import manager
import xml.dom.minidom
with manager.connect(

        host="devnetsandboxiosxe.cisco.com",
        port=830,
        username="admin",
        password="C1sco12345",
        hostkey_verify=False

) as m:

    netconf_reply = m.get_config(source="running")

    print(xml.dom.minidom.parseString(netconf_reply.xml).toprettyxml())

 #Cree un filtro para recuperar solo una parte específica de la configuración (ejemplo: configuración de interfaces):
    # Filtro NETCONF para recuperar solo la configuración de interfaces

    netconf_filter = """

    <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">

        <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">

            <interface/>

        </native>

    </filter>

    """
    # Solicitar la configuración filtrada al dispositivo

    netconf_reply = m.get_config(source="running", filter=netconf_filter)
    # Imprimir la configuración filtrada de las interfaces en formato XML legible

    print(xml.dom.minidom.parseString(netconf_reply.xml).toprettyxml())


