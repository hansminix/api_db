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

class resource_typeview(ModelView):
    def is_accessible(self):
        return current_user.has_role('admin')  # eventueel ook rollen checken

    def inaccessible_callback(self, name, **kwargs):
        # Redirect naar login pagina
        return redirect(url_for('login.index', next=request.url))    

    can_export = True
    form_columns = ['name']
    column_labels = dict(name='Naam')
    column_filters = ('name',)
    form_args = {
        'name': { 'label': 'Naam' }
        }


class groepview(ModelView):
    def is_accessible(self):
        return current_user.has_role('admin')  # eventueel ook rollen checken

    def inaccessible_callback(self, name, **kwargs):
        # Redirect naar login pagina
        return redirect(url_for('login.index', next=request.url))    

    can_export = True
    form_columns = ['name', 'owner','emailaddress','description','documentation','software','accesstype', 'adgroep']
    column_labels = dict(name='Naam',emailaddress='Mailadres',description='Omschrijving',owner='Eigenaar',documentation='Documentatie',software='Software',
                         accesstype='Access type', adgroep='AD Groep')
    column_filters = ('name',)
    form_args = {
        'name': { 'label': 'Naam' },
        'emailaddress': { 'label' : 'Mailadres','validators': [Email(message='Geen geldig mail adres')] },
        'description': { 'label': 'Omschrijving'},
        'owner': { 'label': 'Eigenaar'},
        'documentation': { 'label': 'Documentatie'},
        'software': { 'label': 'Software'},
        'accesstype': { 'label': 'Access type'},
        'adgroep' : { 'label': 'AD Groep'}
        }
    form_choices = {
        'accesstype': [
            ('GUI', 'GUI'),
            ('API', 'API')
        ]
    }

class accountsview(ModelView):
    def is_accessible(self):
        return current_user.has_role('admin')  # eventueel ook rollen checken

    def inaccessible_callback(self, name, **kwargs):
        # Redirect naar login pagina
        return redirect(url_for('login.index', next=request.url))    

    can_export = True
    form_columns = ['name','groep','einddatum']
    column_labels = dict(name='Naam',groep='Groep',einddatum='Einddatum')
    column_filters = ('groep','name','einddatum')
    form_args = {
        'name' : { 'label': 'Naam'},
        'einddatum' : { 'label': 'Einddatum'},
        'groep' : { 'label': 'Groep'},
        }

class groeprechtview(ModelView):
    def is_accessible(self):
        return current_user.has_role('admin')  # eventueel ook rollen checken

    def inaccessible_callback(self, name, **kwargs):
        # Redirect naar login pagina
        return redirect(url_for('login.index', next=request.url))    

    can_export = True
    form_columns = ['object','resource_type', 'permission','groep']
    column_labels = dict(object='Object',resource_type='Resource type',permission='Read/write',groep='Groep')
    column_filters = ('object','resource_type','permission','groep')
    form_args = {
        'object' : { 'label': 'Object'},
        'resource_type' :  { 'label': 'Resource type'},
        'permission':  { 'label': 'Read/write'},
        'groep':  { 'label': 'Groep'},
        }
    form_choices = {'permission': [('READ', 'READ'), ('WRITE', 'WRITE'), ('DENY', 'DENY')]}

class ipaddressenview(ModelView):
    def is_accessible(self):
        return current_user.has_role('admin')  # eventueel ook rollen checken

    def inaccessible_callback(self, name, **kwargs):
        # Redirect naar login pagina
        return redirect(url_for('login.index', next=request.url))    

    can_export = True
    form_columns = ['ipaddress','groep']
    column_labels = dict(ipaddress='IP adres',groep='Groep')
    form_args = {
        'ipaddress' : { 'label': 'IP adres'},
        'groep' : { 'label': 'Groep'},
        }


class MyHomeView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html', current_user=current_user)
    
class LoginMenuLink(MenuLink):

    def is_accessible(self):
        return not current_user.is_authenticated 


class LogoutMenuLink(MenuLink):

    def is_accessible(self):
        return current_user.is_authenticated             

class HomeMainLink(MenuLink):

    def is_accessible(self):
        return current_user.is_authenticated             
