from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from ldap3 import Server, Connection, ALL, ALL_ATTRIBUTES
from ldap3.core.exceptions import LDAPBindError
from .config import Config
from logging import getLogger
import json

logger=getLogger(__name__)

class ldapLogin():

    def __init__(self):
        self.ldapconn=None
        self.userdn=None
        self.cn=None

    def authenticate(self, userid, password):
        try:
            server = Server(Config.LDAP_HOST, get_info=ALL)
            self.cn=userid
            self.userdn=f"{Config.LDAP_USER_RDN_ATTR}={userid},{Config.LDAP_USER_DN},{Config.LDAP_BASE_DN}"
            conn = Connection(server, self.userdn, password, auto_bind=True)
        except LDAPBindError as e:
            print("Authentication failed.")
            return False
        except Exception as e:
            logger.error(f"Onbekende fout bij inloggen: {e}")
            return False
        self.ldapconn = conn    
        return True
    
    def getUserAttributes(self):
        if self.ldapconn.search(Config.LDAP_BASE_DN,f'({Config.LDAP_USER_RDN_ATTR}={self.cn})',attributes=ALL_ATTRIBUTES):
            return json.loads(self.ldapconn.entries[0].entry_to_json())
        return None

    
    def getGroups(self):
        groups=[]
        try:
            if Config.LDAP_SEARCH_GROUPS=='groupattribute':
                if self.ldapconn.search(Config.LDAP_BASE_DN,f'({Config.LDAP_GROUP_ATTRIBUTE}={self.userdn})',attributes=['objectclass']):
                    for entry in self.ldapconn.entries:
                        groups.append(json.loads(entry.entry_to_json())['dn'])
            if Config.LDAP_SEARCH_GROUPS=='userattribute':
                searchfilter=self.userdn.split(',')[0]
                if self.ldapconn.search(Config.LDAP_BASE_DN,f'({searchfilter})',attributes=[Config.LDAP_GROUP_ATTRIBUTE]):
                    groups=json.loads(self.ldapconn.entries[0])['attributes'][f'{Config.LDAP_GROUP_ATTRIBUTE}']
        except Exception as e:
            logger.error(f"Error while retrieving groups for user {self.userdn}: {e}")
            return None
        return groups
            
class ldapLoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField('Login')
