import json
import requests
requests.packages.urllib3.disable_warnings()

api_url = "https://devnetsandboxiosxe.cisco.com/restconf/data/ietf-interfaces:interfaces/interface=Loopback230"
headers = { "Accept": "application/yang-data+json", 
            "Content-type":"application/yang-data+json"
           }
basicauth = ("admin", "C1sco12345")
yangConfig = {
    "ietf-interfaces:interface": {
        "name": "Loopback230",
        "description": "My second RESTCONF loopback wheliver",
        "type": "iana-if-type:softwareLoopback",
        "enabled": True,
        "ietf-ip:ipv4": {
            "address": [
                {
                    "ip": "10.230.1.1",
                    "netmask": "255.255.255.0"
                }
            ]
        },
        "ietf-ip:ipv6": {}
    }
}   
resp = requests.put(api_url, data=json.dumps(yangConfig), auth=basicauth, headers=headers, verify=False)
if(resp.status_code >= 200 and resp.status_code <= 299):
    print("STATUS OK: {}".format(resp.status_code))
else:
    print('Error. Status Code: {} \nError message: {}'.format(resp.status_code,resp.json()))