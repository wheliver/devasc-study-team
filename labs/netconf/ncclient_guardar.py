from ncclient import manager, xml_
import xml.dom.minidom
#import xmltodict

save_body = """
<cisco-ia:save-config xmlns:cisco-ia="http://cisco.com/yang/cisco-ia"/>
"""

# Parámetros de conexión al dispositivo
with manager.connect(
        host="devnetsandboxiosxe.cisco.com",
        port=830,
        username="admin",
        password="C1sco12345",
        hostkey_verify=False
) as m:
    netconf_reply = m.dispatch(xml_.to_ele(save_body))
    print(xml.dom.minidom.parseString(netconf_reply.xml).toprettyxml())