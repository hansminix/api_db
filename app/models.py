from .extensions import db
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, expose, BaseView
from wtforms.validators import Email
from .extensions import validateIBObject
from flask_admin.menu import MenuLink
from flask import redirect, url_for, request
from flask_security import SQLAlchemyUserDatastore
from flask_security.models.fsqla_v3 import FsRoleMixin, FsUserMixin, FsModels
from flask_login import current_user
from logging import getLogger

#Create logger
logger=getLogger(__name__)

#Set flask-security db model
FsModels.set_db_info(db)

class User(db.Model, FsUserMixin):
    __tabel_name__='user'
    name = db.Column(db.String(50),unique=True)
    email = db.Column(db.String(50))

    def __repr__(self):
        return self.name 

    def get_id(self):
        return self.name 

class Role(db.Model, FsRoleMixin):
    __tabel_name__='role'

#Define userdatastore for Flask security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)

class groep(db.Model):
    __table_name__ = 'groep'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255),nullable=False,unique=True)
    owner = db.Column(db.String(255),nullable=False)
    description = db.Column(db.Text)
    emailaddress = db.Column(db.String(100), nullable=False)
    documentation = db.Column(db.Text)
    software = db.Column(db.String(100), nullable=False)
    accesstype = db.Column(db.String(10), nullable=False)
    adgroep = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return self.name 
    
class accounts(db.Model): 
    __table_name__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255),nullable=False,unique=True)
    einddatum = db.Column(db.Date, nullable=False)
    groep_id = db.Column(db.Integer, db.ForeignKey('groep.id'), nullable=False)  # Relatie naar groep
    groep = db.relationship('groep', backref=db.backref('accounts', lazy=True))

    def __repr__(self):
        return self.name

class groeprecht(db.Model):
    __table_name__ = 'groeprecht'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    object = db.Column(db.String(100), nullable=False) #Naam van zone, netwerk etc.
    permission = db.Column(db.String(25), nullable=False) #READ, WRITE, DENY
    groep_id = db.Column(db.Integer, db.ForeignKey('groep.id'), nullable=False)  # Relatie naar groep
    groep = db.relationship('groep', backref=db.backref('groeprechten', lazy=True))  # Relatie naar groep
    resource_type_id = db.Column(db.Integer, db.ForeignKey('resource_type.id'))

class ipadressen(db.Model):
    __table_name__ = 'ipadressen'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ipaddress = db.Column(db.String(100))
    groep_id = db.Column(db.Integer, db.ForeignKey('groep.id'), nullable=False)  # Relatie naar groep
    groep = db.relationship('groep', backref=db.backref('ipadressen', lazy=True))
    
    def __repr__(self):
        return f"{self.ipaddress}"

class resource_type(db.Model):
    __table_name__ = 'resource_type'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    groeprechten = db.relationship('groeprecht', backref='resource_type')

    def __repr__(self):
        return f"{self.name}"

