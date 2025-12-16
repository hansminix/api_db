from .extensions import db
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, expose, BaseView
from flask_admin.form import rules
from .config import Config
from wtforms.validators import Email, DataRequired
from wtforms import SelectField, StringField
from flask_wtf import FlaskForm
from .config import Config
from flask_login import UserMixin, current_user
from flask_admin.menu import MenuLink
from flask_login import login_user, current_user
from flask import redirect, url_for, request, flash
from datetime import datetime

server_applicatierollen = db.Table('server_applicatierollen',
    db.Column('server_id', db.Integer, db.ForeignKey('server.id')),
    db.Column('applicatierol_id',db.Integer, db.ForeignKey('applicatierollen.id'))
)

def getCurrentUser():
    print(current_user.cn)
    return current_user.cn

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
    os = db.Column(db.String(100), nullable=False)
    cpu = db.Column(db.Integer(), nullable=False)
    ram = db.Column(db.Integer(), nullable=False)
    dmz = db.Column(db.String(100), nullable=False)
    updated_by = db.Column(db.String(15), default=getCurrentUser, onupdate=getCurrentUser)
    last_updated = db.Column(db.DateTime(), default=datetime.now(), onupdate=datetime.now)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'))
    iegisid_id = db.Column(db.Integer, db.ForeignKey('iegisid.id'))
    notities = db.relationship('notities', backref='server')
    ipregistratie = db.relationship('ipregistratie', backref='server')
    # Many-to-many relatie
    applicatierollen = db.relationship('applicatierollen',secondary=server_applicatierollen, backref=db.backref('servers'), lazy='dynamic')
    
    def __repr__(self):
        return self.naam
       
class ipregistratie(db.Model): 
    __table_name__ = 'ipregistratie'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ipadres = db.Column(db.String(25),nullable=False,unique=True)
    gateway = db.Column(db.String(25),nullable=False)
    vlan = db.Column(db.Integer(), nullable=False)
    type = db.Column(db.String(25),nullable=False)
    server_id = db.Column(db.String, db.ForeignKey('server.id'))  # Relatie naar server
    

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

class iegisid(db.Model): 
    __table_name__ = 'iegisid'
    id = db.Column(db.Integer(),primary_key=True, autoincrement=True)
    iegisid = db.Column(db.String(25))
    omschrijving= db.Column(db.Text)
    servers = db.relationship('server', backref='iegisid')

    def __repr__(self):
        return self.iegisid

class notities(db.Model): 
    __table_name__ = 'notities'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    omschrijving= db.Column(db.Text)
    datum= db.Column(db.Date, default=datetime.now())
    server_id = db.Column(db.String, db.ForeignKey('server.id'), nullable=False)  # Relatie naar server

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
    form_edit_rules = [
        rules.Row('server','type','vlan',),
        rules.Row('ipadres','gateway')
    ]
    form_create_rules = form_edit_rules

class serverview(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated  # eventueel ook rollen checken

    def inaccessible_callback(self, name, **kwargs):
        # Redirect naar login pagina
        return redirect(url_for('login.index', next=request.url))    
    
    can_export = True
    form_columns = ['naam', 'eigenaar','email','omschrijving','status','os','cpu','ram', 'dmz','applicatierollen','tenant','iegisid','last_updated','updated_by']
    column_list = ['naam','eigenaar', 'status','dmz', 'omschrijving']
    column_filters = ('naam','eigenaar','applicatierollen','tenant','iegisid','status')

    #column_display_pk = True
    column_hide_backrefs = False

    column_labels = dict(naam='Naam',eigenaar='Eigenaar',email='Mailadres',omschrijving='Omschrijving',status='Status',datum='Datum', os='Operating system', \
                         cpu='CPU', ram='RAM', dmz='DMZ',tenant='tenant',iegisid='iegisid',last_updated='Bijgewerkt op',updated_by='Bijgewerkt door')
    
    form_args = {
        'naam': { 'label': 'Naam' },
        'email': { 'label' : 'Mailadres','validators': [Email(message='Geen geldig mail adres')] },
        'omschrijving': { 'label': 'Omschrijving', 'validators': [DataRequired()]},
        'eigenaar': { 'label': 'Eigenaar', 'validators': [DataRequired()]},
        'status': { 'label': 'Status', 'validators': [DataRequired()]},
        'os': { 'label': 'Operating system', 'validators': [DataRequired()]},
        'cpu': { 'label': 'CPU', 'validators': [DataRequired()]},
        'ram': { 'label': 'RAM', 'validators': [DataRequired()]},
        'dmz': { 'label': 'DMZ', 'validators': [DataRequired()]},
        'applicatierollen': { 'label': 'Applicatierollen'},
        'tenant': { 'label': 'Tenant', 'validators': [DataRequired()]},
        'iegisid': { 'label': 'IEGISID', 'validators': [DataRequired()]},
        'last_updated': { 'label': 'Bijgewerkt op'},
        'updated_by': { 'label': 'Bijgewerkt door'}
        }
    
    form_choices = {'status': [('Nieuw', 'Nieuw'), ('Actief', 'Actief'), ('Verwijderd', 'Verwijderd')], 'dmz': [('Frontend', 'Frontend'), ('Intermediate', 'Intermediate'), ('Backend', 'Backend')] }

    form_edit_rules = [
        rules.Row('naam','eigenaar','email','status'),
        rules.Row('omschrijving','os','ram','cpu'),
        rules.Row('dmz','applicatierollen','tenant'),
        rules.Row('iegisid','last_updated','updated_by')
    ]
    form_create_rules = form_edit_rules


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

class iegisidview(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated  # eventueel ook rollen checken

    def inaccessible_callback(self, name, **kwargs):
        # Redirect naar login pagina
        return redirect(url_for('login.index', next=request.url))    

    can_export = True
    form_columns = ['iegisid','omschrijving']
    #column_display_pk = True
    column_labels = dict(iegisid='IEGISID',omschrijving='Omschrijving')
    column_list = ['iegisid', 'omschrijving']
    form_args = {
        'iegisid': { 'label': 'IEGISID', 'validators': [DataRequired()] },
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
    column_labels = dict(server='Server',datum='Datum',omschrijving='Omschrijving')
    column_list = ['server', 'datum', 'omschrijving']
    form_args = {
        'server': { 'label': 'Server', 'validators': [DataRequired()] },
        'omschrijving': { 'label': 'Omschrijving', 'validators': [DataRequired()]},
        }

class ServerView(FlaskForm):

    #serverselect = SelectField(u'Select server', validate_choice=False)
    serverselect=StringField('servernames', validators=[DataRequired()])

class ServerOverview(BaseView):    
    @expose('/', methods=["GET","POST"])
    def index(self):
        form  = ServerView()
        serverdata=None
        ipdata=None
        appldata=None
        notitiesdata=None
        #form.serverselect.choices = [('', '')] + [(g.naam, g.naam) for g in server.query.order_by('naam')]
        servernames=[g.naam for g in server.query.order_by('naam')]
        if form.validate_on_submit():
            #Get server date
            print(form.serverselect.data)
            serverdata = (db.session.query(server, tenants, iegisid)
                .join(tenants, tenants.id==server.tenant_id, isouter=True)
                .join(iegisid, iegisid.id==server.iegisid_id, isouter=True)
                .filter(server.naam == form.serverselect.data)).all()
            ipdata=(db.session.query(server, ipregistratie)
                .join(server, ipregistratie.server_id==server.id, isouter=True)
                .filter(server.naam == "v2lqah4901")).all()
            appldata=(db.session.query(server, applicatierollen)
                .join(server_applicatierollen, server_applicatierollen.c['server_id'] == server.id, isouter=True)
                .join(applicatierollen, applicatierollen.id==server_applicatierollen.c['applicatierol_id'], isouter=True)
                .filter(server.naam == form.serverselect.data)).all()
            notitiesdata=(db.session.query(server, notities)
                .join(notities, notities.server_id == server.id, isouter=True)
                .filter(server.naam == form.serverselect.data)
                .order_by(notities.datum)).all()
        return self.render('admin/serveroverview.html',form=form, servernames=servernames,serverdata=serverdata, ipdata=ipdata, appldata=appldata, notitiesdata=notitiesdata)

    def is_accessible(self):
        return current_user.is_authenticated 

    def inaccessible_callback(self, name, **kwargs):
        # Redirect naar login pagina
        return redirect(url_for('login.index', next=request.url))    
