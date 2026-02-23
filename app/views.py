from .extensions import db
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, expose, BaseView
from wtforms.validators import Email
from flask_admin.menu import MenuLink
from flask import redirect, url_for, request, render_template
from flask_login import current_user
from .models import groep, groeprecht, accounts, ipadressen
from datetime import datetime,timedelta
from logging import getLogger

#Create logger
logger=getLogger(__name__)

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
    
    def is_visible(self):
        # Hide the index view from the menu
        return False
    #@expose('/')
    #def index(self):
    #    return self.render('admin/index.html', current_user=current_user)
    
    def is_accessible(self):
        return False
    
class LoginMenuLink(MenuLink):

    def is_accessible(self):
        return not current_user.is_authenticated 
    
    def get_url(self):
        return url_for('login.index')


class LogoutMenuLink(MenuLink):

    def is_accessible(self):
        return current_user.is_authenticated 

    def get_url(self):
        return url_for('logout')            

class HomeMainLink(MenuLink):

    def is_accessible(self):
        return current_user.is_authenticated             

    def get_url(self):
        return url_for('index.home')            

class ListAPIView(BaseView):
    #@expose('overzicht', methods=['GET'], defaults={ 'filter':''})
    @expose('/', methods=['GET'])
    def index(self):
        filter = request.args.get("filter", "")
        print(filter)
        if filter:
                if int(filter) <= 0:
                        today=datetime.strftime(datetime.now(), '%Y-%m-%d')
                        dateend=datetime.strftime(datetime.now()+timedelta(days=int(filter)), '%Y-%m-%d')
                        #Query to get all data ordered by group and account
                        qry_grp=(db.session.query(groep,accounts,groeprecht,ipadressen)
                                .join(accounts, accounts.groep_id==groep.id)
                                .join(groeprecht, groeprecht.groep_id==groep.id)
                                .join(ipadressen, ipadressen.groep_id==groep.id)
                                .filter(accounts.einddatum <= dateend)
                                .order_by(groep.name)
                                .order_by(accounts.name).all())                
                else:
                        today=datetime.strftime(datetime.now(), '%Y-%m-%d')
                        dateend=datetime.strftime(datetime.now()+timedelta(days=int(filter)), '%Y-%m-%d')
                        #Query to get all data ordered by group and account
                        qry_grp=(db.session.query(groep,accounts,groeprecht,ipadressen)
                                .join(accounts, accounts.groep_id==groep.id)
                                .join(groeprecht, groeprecht.groep_id==groep.id)
                                .join(ipadressen, ipadressen.groep_id==groep.id)
                                .filter(accounts.einddatum <= dateend, accounts.einddatum >= today)
                                .order_by(groep.name)
                                .order_by(accounts.name).all())
        else:
                #Query to get all data ordered by group and account
                qry_grp=(db.session.query(groep,accounts,groeprecht,ipadressen)
                        .join(accounts, accounts.groep_id==groep.id)
                        .join(groeprecht, groeprecht.groep_id==groep.id)
                        .join(ipadressen, ipadressen.groep_id==groep.id)
                        .order_by(groep.name)
                        .order_by(accounts.name).all())
        #Create empty dict to store data to be able to process it easily in the html template
        acc_list={}
        for grp in qry_grp:
                #Create new key for each group with dict for other data, and add the ID to it to use this in a link
                acc_list.setdefault(grp[0].name,{})
                acc_list[grp[0].name].setdefault('id',grp[0].id)
                acc_list[grp[0].name].setdefault('contact',grp[0].owner)
                acc_list[grp[0].name].setdefault('email',grp[0].emailaddress)
                #Create new key for accounts if it does not exits and add the account object to it in a set
                acc_list[grp[0].name].setdefault('accounts',set()).add(grp[1])
                #Create new key for access rights if it does not exits and add the object to it in a set
                acc_list[grp[0].name].setdefault('rights',set()).add(grp[2])
                #Create new key for ipaddresses if it does not exits and add the ip address to it in a set
                acc_list[grp[0].name].setdefault('ips',set()).add(grp[3].ipaddress)
        return self.render('accounts.html', acc_list=acc_list)

    def is_accessible(self):
        return current_user.has_role('admin')  # eventueel ook rollen checken

    def inaccessible_callback(self, name, **kwargs):
        # Redirect naar login pagina
        return redirect(url_for('login.index', next=request.url))    
    