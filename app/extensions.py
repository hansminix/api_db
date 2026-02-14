from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_migrate import Migrate
from wtforms.validators import ValidationError
from ipaddress import IPv4Network, IPv6Network, NetmaskValueError
import re

db = SQLAlchemy()
admin=Admin()
migrate=Migrate()

def validateIBObject(form, field):
    if field.data:
        #test if ipv4 network
        try:
            ipv4net=IPv4Network(field.data)
            ipv4=True
        except Exception:
            #Not network, set ipv4 flase
            ipv4=False
        try:
            ipv6net=IPv6Network(field.data)
            ipv6=True
        except Exception:
            #Not network, set ipv6 flase
            ipv6=False
        dnsdomain=re.match(r'^(((?!-))(xn--|_)?[a-z0-9-]{0,61}[a-z0-9]{1,1}\.)*(xn--)?([a-z0-9][a-z0-9\-]{0,60}|[a-z0-9-]{1,30}\.[a-z]{2,})$', field.data)
        if not (ipv4 or ipv6 or dnsdomain):
            raise ValidationError('Geen valide object')
