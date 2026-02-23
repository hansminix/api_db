from ipaddress import IPv4Address, IPv6Address, IPv4Network, IPv6Network
from pydantic import BaseModel, Field, ValidationError, model_validator
from typing import Any, Annotated
import re
import json

gritNetworks=[IPv4Network('10.1.1.0/24'), IPv4Network('10.10.1.0/24')]
gritZones=['intra.mindef.nl']
regexZone=r"(^.*?)\.(.*)"

def isGritAddress(ipaddress, version):
    if version=='ipv4':
        ipadd=IPv4Address(ipaddress)
        for net in gritNetworks:
            if ipadd in net:
                return True
    return False

class Host(BaseModel):
    name: str = ''
    zone: str =''
    iptxt: str = ''
    comment: str = ''
    ipv4addr:  str = ''
    ipv6addr: str = ''

    @model_validator(mode='before')
    @classmethod
    def set_ip_net(cls, data: Any) -> Any:
        if isinstance(data, dict):
            iptxt = data.get('iptxt')
            if iptxt:
                try:
                    ipv4=IPv4Address(iptxt)
                    data['ipv4addr'] = str(ipv4)
                except:
                    pass
                try:
                    ipv6=IPv6Address(iptxt)
                    data['ipv6addr'] = str(ipv6)
                except:
                    pass
            else:
                raise ValueError('Geen ipadres opgegeven')
            name=data.get('name')
            match = re.search(regexZone, name)
            if match:
                data['zone']=match.group(2)
        return data

    @model_validator(mode='after')
    def chkNetZone(self):
        if self.ipv4addr:
            #print(isGritAddress(self.ipv4addr,'ipv4'))
            #print(self.zone in gritZones)
            if isGritAddress(self.ipv4addr,'ipv4') and not self.zone in gritZones:
                raise ValueError("GRIT address niet in GRIT Zone")
        return self

# Gegevens van buitenaf (bijv. API-response)
external_data = {
    "name": "hans.mod.nl",
    "iptxt": "",
    "comment": "Test"
}

# Validatie en conversie automatisch
try:
    host = Host(**external_data)
except ValidationError as exc:
    print(print(repr(json.loads(exc.json())[0]['msg'])))