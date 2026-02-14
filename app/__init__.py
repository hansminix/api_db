from flask import Flask, request, redirect
from .config import Config
from logging import getLogger, basicConfig, FileHandler, StreamHandler, Formatter
from sqlalchemy.orm import configure_mappers
from flask_security import Security
from flask_security.core import AnonymousUser
from .extensions import db, admin, migrate
from .models import groep, groeprecht, accounts, ipadressen, User, Role, resource_type, resource_typeview, \
    groepview, groeprechtview, accountsview, ipaddressenview, user_datastore, MyHomeView, LogoutMenuLink, HomeMainLink
from .auth import LoginView
#from .models_storage import server, applicatierollen, tenants, notities, ipregistratie, iegisid, \
#    serverview, applicatierollenview, ipregistratieview, tenantsview, notitiesview, ServerOverview, iegisidview, MsiLinkPageview
from .index import index
from .lists import overzicht
from flask_login import LoginManager, login_required, logout_user, current_user
from datetime import datetime
from flask import current_app

#Get logging configuration
logger=getLogger(__name__)
logformat=Formatter('[%(asctime)s] %(levelname)s in %(name)s: %(message)s')
streamhandler=StreamHandler()
streamhandler.setFormatter(logformat)
fileHandler=FileHandler(filename=Config.LOGFILE)
fileHandler.setFormatter(logformat)
basicConfig(level=Config.LOGLEVEL,handlers=[streamhandler,fileHandler])
app = Flask(__name__)

def create_app():
    #Configuration from object, file config.py
    app.config.from_object(Config)

    #Initialize db
    db.init_app(app)
    migrate.init_app(app, db)

    # Setup Flask-Security
    security = Security(app, user_datastore)

    app.register_blueprint(index, url_prefix='/')
    app.register_blueprint(overzicht, url_prefix='/')

    admin.name='API Accounts'
    admin.init_app(app)
    configure_mappers()
    admin.index_view=MyHomeView
    admin.add_link(HomeMainLink(name='Main Menu', category='', url="/"))
    #admin.add_view(MsiLinkPageview(name='MSI URL link pagina',endpoint='msilinkpage',url="/admin/msilinkpageview"))
    admin.add_view(groepview(groep,db.session, name='Groepen', category='Infoblox delegatie'))
    admin.add_view(accountsview(accounts,db.session,name="Accounts", category='Infoblox delegatie'))
    admin.add_view(ipaddressenview(ipadressen,db.session,name="IP Adressen", category='Infoblox delegatie'))
    admin.add_view(groeprechtview(groeprecht,db.session, name='Groep rechten', category='Infoblox delegatie'))
    admin.add_view(resource_typeview(resource_type, db.session, name='Resource types', category='Infoblox delegatie'))
    #admin.add_view(ipregistratieview(ipregistratie,db.session, name='IP Registraties', category='IEGI VM'))
    #admin.add_view(notitiesview(notities,db.session, name='Server notities', category='IEGI VM'))
    #admin.add_view(serverview(server,db.session, name='Servers', category='IEGI VM'))
    #admin.add_view(applicatierollenview(applicatierollen,db.session, name='Applicatierollen', category='IEGI VM'))
    #admin.add_view(ServerOverview(name='Server overview',endpoint='serveroverview',url="/admin/serveroverview", category='IEGI VM'))
    #admin.add_view(tenantsview(tenants,db.session, name='Tenants', category='Tabellen'))
    #admin.add_view(iegisidview(iegisid,db.session, name='IEGISID', category='Tabellen'))
    admin.add_view(LoginView(name='Login',endpoint='login',url="/login"))
    admin.add_link(LogoutMenuLink(name='Logout', category='', url="/logout"))
    
    #Initialize flask login
    login_manager = LoginManager()
    login_manager.init_app(app)

    # Set Flask-Security's AnonymousUser as the anonymous user class
    login_manager.anonymous_user = AnonymousUser

    @login_manager.user_loader
    def load_user(user):
        qset=User.query.filter_by(name=user).first()
        if qset:
            return qset
        else:
            return None
    logger.debug("Application started")

    @app.route('/logout',methods=['GET', 'POST'])
    @login_required
    def logout():
        logout_user()
        return redirect('/admin')

    with app.app_context():
        for k,v in Config.GROUP_ROLE_MAP.items():
            role=Role.query.filter_by(name=v).first()
            if not role:
                user_datastore.create_role(name=v)
                db.session.commit()

    return app

@app.after_request
def after_request(response):
    """ Logging all of the requests in JSON Per Line Format. """
    if request.method != 'GET':
        audit_logger = getLogger('inbound_requests')
        alHandler=FileHandler(filename=Config.AUDIT_LOGFILE)
        alHandler.setFormatter(logformat)
        audit_logger.addHandler(alHandler)
        reqdata=request.form.to_dict()
        for key in Config.HIDE_LOG_DATA:
            if key in reqdata:
                del reqdata[key]
        audit_logger.info({
                "user": current_user,
                "datetime": datetime.now().isoformat(),
                "response_status": response.status,
                "request_body": reqdata,
            })
    return response

def init_db():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    with app.app_context():
        db.create_all()
