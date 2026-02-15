from flask import Blueprint, render_template
from .extensions import db
from .models import groep, groeprecht, accounts, ipadressen
from datetime import datetime,timedelta

overzicht = Blueprint('overzicht', __name__)

#@overzicht.route('overzicht', methods=['GET','POST'])
@overzicht.route('overzicht', strict_slashes=False ,methods=['GET'], defaults={ 'filter':''})
@overzicht.route('overzicht/<filter>/', methods=['GET'])
def acc(filter):
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
        return render_template('accounts.html', acc_list=acc_list)