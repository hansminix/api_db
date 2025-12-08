from .extensions import db
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, expose, BaseView
from .config import Config
from wtforms.validators import Email, DataRequired
from wtforms import Form, SelectField
from .config import Config
from flask_login import UserMixin, current_user
from flask_admin.menu import MenuLink
from flask_ldap3_login.forms import LDAPLoginForm
from flask_login import login_user, current_user
from flask import redirect, url_for, request, flash
from datetime import datetime

server_applicatierollen = db.Table('server_applicatierollen',
    db.Column('server_id', db.Integer, db.ForeignKey('server.id')),
    db.Column('applicatierol_id',db.Integer, db.ForeignKey('applicatierollen.id'))
)

class applicatierollen(db.Model): 
    __table_name__ = 'applicatierollen'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    applicatierol = db.Column(db.String(25), nullable=False)

    def __repr__(self):
        return self.applicatierol

class server(db.Model):
    __table_name__ = 'server'
    id = db.Column(db.Integer(),primary_key=True, autoincrement=True)
    naam = db.Column(db.String(25),nullable=False)
    eigenaar = db.Column(db.String(255),nullable=False)
    omschrijving = db.Column(db.Text)
    email = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    datum = db.Column(db.Date(), nullable=False)
    os = db.Column(db.String(100), nullable=False)
    cpu = db.Column(db.Integer(), nullable=False)
    ram = db.Column(db.Integer(), nullable=False)
    dmz = db.Column(db.String(100), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'))
    notities = db.relationship('notities', backref='server')
    # Many-to-many relatie
    applicatierollen = db.relationship('applicatierollen',secondary=server_applicatierollen, backref=db.backref('servers'), lazy='dynamic')
    
    def __repr__(self):
        return self.naam
       
class ipregistratie(db.Model): 
    __table_name__ = 'ipregistration'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ipadres = db.Column(db.String(25),nullable=False,unique=True)
    gateway = db.Column(db.String(25),nullable=False)
    vlan = db.Column(db.Integer(), nullable=False)
    type = db.Column(db.String(25),nullable=False)
    server_id = db.Column(db.String, db.ForeignKey('server.id'))  # Relatie naar server
    server = db.relationship('server', backref=db.backref('ipadres', lazy=True))

    def __repr__(self):
        return self.ipadres
    
class tenants(db.Model): 
    __table_name__ = 'tenants'
    id = db.Column(db.Integer(),primary_key=True, autoincrement=True)
    tenant = db.Column(db.String(25))
    omschrijving= db.Column(db.Text)
    servers = db.relationship('server', backref='tenant')

    def __repr__(self):
        return self.tenant

class notities(db.Model): 
    __table_name__ = 'notities'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    omschrijving= db.Column(db.Text)
    datum= db.Column(db.Date, default=datetime.now())
    server_id = db.Column(db.String, db.ForeignKey('server.id'), nullable=False)  # Relatie naar server

class serverview(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated  # eventueel ook rollen checken

    def inaccessible_callback(self, name, **kwargs):
        # Redirect naar login pagina
        return redirect(url_for('login.index', next=request.url))    

    can_export = True
    form_columns = ['naam', 'eigenaar','email','omschrijving','status','datum','os','cpu','ram', 'dmz','applicatierollen','tenant']
    column_list = ['naam','eigenaar', 'status','dmz', 'omschrijving']
    #column_display_pk = True
    column_hide_backrefs = False

    column_labels = dict(naam='Naam',eigenaar='Eigenaar',email='Mailadres',omschrijving='Omschrijving',status='Status',datum='Datum', os='Operating system', \
                         cpu='CPU', ram='RAM', dmz='DMZ',tenant='tenant')
    
    form_args = {
        'naam': { 'label': 'Naam' },
        'email': { 'label' : 'Mailadres','validators': [Email(message='Geen geldig mail adres')] },
        'omschrijving': { 'label': 'Omschrijving', 'validators': [DataRequired()]},
        'eigenaar': { 'label': 'Eigenaar', 'validators': [DataRequired()]},
        'status': { 'label': 'Status', 'validators': [DataRequired()]},
        'datum': { 'label': 'Datum', 'validators': [DataRequired()]},
        'os': { 'label': 'Operating system', 'validators': [DataRequired()]},
        'cpu': { 'label': 'CPU', 'validators': [DataRequired()]},
        'ram': { 'label': 'RAM', 'validators': [DataRequired()]},
        'dmz': { 'label': 'DMZ', 'validators': [DataRequired()]},
        'applicatierollen': { 'label': 'Applicatierollen'},
        'tenant': { 'label': 'Tenant', 'validators': [DataRequired()]}
        }
    
    form_choices = {'status': [('Nieuw', 'Nieuw'), ('Actief', 'Actief'), ('Verwijderd', 'Verwijderd')], 'dmz': [('Frontend', 'Frontend'), ('Intermediate', 'Intermediate'), ('Backend', 'Backend')] }

class applicatierollenview(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated  # eventueel ook rollen checken

    def inaccessible_callback(self, name, **kwargs):
        # Redirect naar login pagina
        return redirect(url_for('login.index', next=request.url))    

    can_export = True
    form_columns = ['applicatierol']
    column_filters = ('applicatierol',)
    #column_display_pk = True
    column_labels = dict(applicatierol='Applicatierol',)
    form_args = {
        'applicatierol': { 'label': 'Applicatierol', 'validators': [DataRequired()] },
        }
    
class ipregistratieview(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated  # eventueel ook rollen checken

    def inaccessible_callback(self, name, **kwargs):
        # Redirect naar login pagina
        return redirect(url_for('login.index', next=request.url))    

    can_export = True
    form_columns = ['ipadres','gateway','vlan','type','server']
    column_filters = ('server',)
    #column_display_pk = True
    column_labels = dict(ipadres='IP Adres',gateway='Gateway',vlan='VLAN',type='Type',server='Server')
    form_args = {
        'ipadres': { 'label': 'IP Adres', 'validators': [DataRequired()] },
        'gateway': { 'label': 'Gateway', 'validators': [DataRequired()] },
        'vlan': { 'label': 'VLAN', 'validators': [DataRequired()] },
        'type': { 'label': 'Type', 'validators': [DataRequired()] },
        'server': { 'label': 'Server', 'validators': [DataRequired()] },
        }    
    form_choices = {'type': [('Management', 'Management'), ('Productie', 'Productie')] }

class tenantsview(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated  # eventueel ook rollen checken

    def inaccessible_callback(self, name, **kwargs):
        # Redirect naar login pagina
        return redirect(url_for('login.index', next=request.url))    

    can_export = True
    form_columns = ['tenant','omschrijving']
    #column_display_pk = True
    column_labels = dict(tenant='Tenant',omschrijving='Omschrijving')
    column_list = ['tenant', 'omschrijving']
    form_args = {
        'tenant': { 'label': 'Tenant', 'validators': [DataRequired()] },
        'omschrijving': { 'label': 'Omschrijving'},
        }
    
class notitiesview(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated  # eventueel ook rollen checken

    def inaccessible_callback(self, name, **kwargs):
        # Redirect naar login pagina
        return redirect(url_for('login.index', next=request.url))    

    can_export = True
    can_edit = False
    can_delete = False
    form_columns = ['server','omschrijving']
    #column_display_pk = True
    column_labels = dict(server='Server',omschrijving='Omschrijving')
    column_list = ['server', 'omschrijving']
    form_args = {
        'server': { 'label': 'Server', 'validators': [DataRequired()] },
        'omschrijving': { 'label': 'Omschrijving', 'validators': [DataRequired()]},
        }

class ServerView(Form):

    serverselect = SelectField(u'Select server')

class ServerOverview(BaseView):    
    @expose('/', methods=["GET","POST"])
    def index(self):
        form  = ServerView()
        form.serverselect.choices = [(g.naam, g.naam) for g in server.query.order_by('naam')]
        return self.render('admin/serveroverview.html',form=form)

    def is_accessible(self):
        return current_user.is_authenticated 
