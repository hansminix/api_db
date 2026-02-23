import ssl

class Config:
    SECRET_KEY = '91f594b33a0c6e72223bd60f04fe0c3525d5759b19dfd44c'
    #SQLALCHEMY_DATABASE_URI="mysql://ftrdb:Instruct3@localhost/ftrdb"
    SQLALCHEMY_DATABASE_URI='sqlite:////home/hnoordam/workspace/api_db/api_db.sqlite'
    LOGLEVEL='INFO'
    LOGFILE='/home/hnoordam/workspace/api_db/flask.log'
    AUDIT_LOGFILE='/home/hnoordam/workspace/api_db/audit.log'
    
    #Application root for hosting on apache
    #APPLICATION_ROOT='/api-db'
    
    #LDAP configuration
    # Hostname of your LDAP Server
    LDAP_HOST = 'localhost'
    # Base DN of your directory
    LDAP_BASE_DN = 'dc=hans,dc=home'

    # Users DN to be prepended to the Base DN
    LDAP_USER_DN = 'ou=users'

    LDAP_SEARCH_FOR_GROUPS = False
    #LDAP_GROUP_OBJECT_FILTER = '(objectclass=groupOfNames)'
    # Groups DN to be prepended to the Base DN
    #'LDAP_GROUP_DN'] = 'ou=groups'

    # The RDN attribute for your user schema on LDAP
    LDAP_USER_RDN_ATTR = 'cn'

    # The Attribute you want users to authenticate to LDAP with.
    LDAP_USER_LOGIN_ATTR = 'cn'

    # The Username to bind to LDAP with
    LDAP_BIND_USER_DN = None

    # The Password to bind to LDAP with
    LDAP_BIND_USER_PASSWORD = None
    LDAP_SEARCH_GROUPS='groupattribute' #userattribute or groupattribute
    LDAP_GROUP_ATTRIBUTE='member'
    LDAP_MAIL_ATTRIBUTE='mail'
    LDAP_TLS=False
    LDAP_CA_FILE='CA'
    LDAP_TLS_VERSION=ssl.PROTOCOL_TLSv1_2
    GROUP_ROLE_MAP={'cn=ontwerp,ou=Groups,dc=hans,dc=home':'admin'}

    HIDE_LOG_DATA = ['password','csrf_token']

    """
    ACCES_GROUPS=['v5siabeheer']
    object_types=[]
    object_subtypes=[]
    with open('object_types.txt') as of:
        for line in of:
            object_types.append((line.strip(), line.strip()))
    with open('object_subtypes.txt') as of:
        for line in of:
            object_subtypes.append((line.strip(), line.strip()))
    """    
