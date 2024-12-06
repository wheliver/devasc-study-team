from ncclient import manager

with manager.connect(

        host="devnetsandboxiosxe.cisco.com",

        port=830,

        username="admin",

        password="C1sco12345",

        hostkey_verify=False

) as m:

    print("# Capabilities supported (modelos YANG):")

    for capability in m.server_capabilities:

        print(capability)
