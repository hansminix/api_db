from .extensions import db
import sqlalchemy as sqldb
from flask_admin.contrib.sqla import ModelView
from .config import Config
from sqlalchemy.sql import func
from wtforms.validators import Email, Regexp, DataRequired
#from wtforms_alchemy import Unique
from wtforms import SelectField, StringField
from datetime import datetime
from .config import Config
import itertools

class groep(db.Model):
    __table_name__ = 'groep'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255),nullable=False,unique=True)
    owner = db.Column(db.String(255),nullable=False)
    description = db.Column(db.Text)
    emailaddress = db.Column(db.String(100), nullable=False)
    documentation = db.Column(db.Text)
    software = db.Column(db.String(100), nullable=False)
    
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

class groeprechten(db.Model):
    __table_name__ = 'groeprechten'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    object_name = db.Column(db.String(100), nullable=False)
    object_type = db.Column(db.String(100), nullable=False)
    object_sub = db.Column(db.String(100))
    rwrechten = db.Column(db.String(25), nullable=False)
    groep_id = db.Column(db.Integer, db.ForeignKey('groep.id'), nullable=False)  # Relatie naar groep
    groep = db.relationship('groep', backref=db.backref('groeprechten', lazy=True))  # Relatie naar groep

    def __repr__(self):
        return f'{self.name}'

class ipadressen(db.Model):
    __table_name__ = 'ipadressen'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ipaddress = db.Column(db.String(100))
    groep_id = db.Column(db.Integer, db.ForeignKey('groep.id'), nullable=False)  # Relatie naar groep
    groep = db.relationship('groep', backref=db.backref('ipadressen', lazy=True))
    
    def __repr__(self):
        return f"{self.name}"

"""
class objecttypes(db.Model):
    __table_name__ = 'objectnames'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)

class object_subtypes(db.Model):
    __table_name__ = 'object_subtypes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
"""
class groepview(ModelView):
    can_export = True
    form_columns = ['name', 'owner','emailaddress','description','documentation','software']
    column_labels = dict(name='Naam',emailaddress='Mailadres',description='Omschrijving',owner='Eigenaar',documentation='Documentatie',software='Software')
    form_args = {
        'name': { 'label': 'Naam' },
        'emailaddress': { 'label' : 'Mailadres','validators': [Email(message='Geen geldig mail adres')] },
        'description': { 'label': 'Omschrijving'},
        'owner': { 'label': 'Eigenaar'},
        'documentation': { 'label': 'Documentatie'},
        'software': { 'label': 'Software'}
        }

class accountsview(ModelView):
    can_export = True
    form_columns = ['name','groep','einddatum']
    column_labels = dict(name='Naam',groep='Groep',einddatum='Einddatum')
    column_filters = ('groep','name','einddatum')
    form_args = {
        'name' : { 'label': 'Naam'},
        'einddatum' : { 'label': 'Einddatum'},
        'groep' : { 'label': 'Groep'},
        }

class groeprechtenview(ModelView):
    can_export = True
    form_columns = ['object_name','object_type', 'object_sub', 'rwrechten','groep']
    column_labels = dict(object_name='Object',object_type='Type object',object_sub='Subtype',rwrechten='Read/write',groep='Groep')
    column_filters = ('object_name','object_type','object_sub','rwrechten','groep')
    form_args = {
        'object_name' : { 'label': 'Object'},
        'object_type' :  { 'label': 'Type object'},
        'object_sub':  { 'label': 'Subtype'},
        'rwrechten':  { 'label': 'Read/write'},
        'groep':  { 'label': 'Groep'},
        }
    form_choices = {'rwrechten': [('READ', 'READ'), ('WRITE', 'WRITE'), ('DENY', 'DENY')], 'object_type': Config.object_types,
                    'object_sub': Config.object_subtypes}

class ipaddressenview(ModelView):
    can_export = True
    form_columns = ['ipaddress','groep']
    column_labels = dict(ipaddress='IP adres',groep='Groep')
    form_args = {
        'ipaddress' : { 'label': 'IP adres'},
        'groep' : { 'label': 'Groep'},
        }

"""
class objecttypesview(ModelView):
    can_export = True
    form_columns = ['name']
    column_labels = dict(name='Naam')
    form_args = {
        'name': { 'label': 'Naam'},
        }

class object_subtypesview(ModelView):
    can_export = True
    form_columns = ['name']
    column_labels = dict(name='Naam')
    form_args = {
        'name': { 'label': 'Naam'},
        }
"""