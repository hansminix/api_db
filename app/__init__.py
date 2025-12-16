from flask import Flask, request, render_template, redirect
from .config import Config
from logging import getLogger, basicConfig, FileHandler, StreamHandler, Formatter
from logging.config import fileConfig
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin
from sqlalchemy.orm import configure_mappers
from .extensions import db, admin, migrate
from .models import groep, groeprechten, accounts, ipadressen, User,\
    groepview, groeprechtenview, accountsview, ipaddressenview, MyHomeView, LoginView, LogoutMenuLink
from .models_storage import server, applicatierollen, tenants, notities, ipregistratie, iegisid, \
    serverview, applicatierollenview, ipregistratieview, tenantsview, notitiesview, ServerOverview, iegisidview
from .index import index
import pymysql
pymysql.install_as_MySQLdb()
from flask_ldap3_login import LDAP3LoginManager
from flask_ldap3_login.forms import LDAPLoginForm
from flask_login import LoginManager, login_user, login_required, logout_user

#Get logging configuration
logger=getLogger(__name__)
logformat=Formatter('[%(asctime)s] %(levelname)s in %(name)s: %(message)s')
streamhandler=StreamHandler()
streamhandler.setFormatter(logformat)
fileHandler=FileHandler(filename=Config.LOGFILE)
fileHandler.setFormatter(logformat)
basicConfig(level=Config.LOGLEVEL,handlers=[streamhandler,fileHandler])

def create_app():
    app = Flask(__name__)
    #Configuration from object, file config.py
    app.config.from_object(Config)

    #Initialize db
    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(index, url_prefix='/')

    admin.name='API Accounts'
    admin.init_app(app)
    configure_mappers()
    admin.index_view=MyHomeView
    admin.add_view(groepview(groep,db.session, name='Groepen', category='IB Delegaties'))
    admin.add_view(accountsview(accounts,db.session,name="Accounts", category='IB Delegaties'))
    admin.add_view(ipaddressenview(ipadressen,db.session,name="IP Adressen", category='IB Delegaties'))
    admin.add_view(groeprechtenview(groeprechten,db.session, name='Groep rechten', category='IB Delegaties'))
    admin.add_view(ipregistratieview(ipregistratie,db.session, name='IP Registraties', category='IEGI VM'))
    admin.add_view(serverview(server,db.session, name='Servers', category='IEGI VM'))
    admin.add_view(applicatierollenview(applicatierollen,db.session, name='Applicatierollen', category='IEGI VM'))
    admin.add_view(notitiesview(notities,db.session, name='Server notities', category='IEGI VM'))
    admin.add_view(ServerOverview(name='Server overview',endpoint='serveroverview',url="/admin/serveroverview", category='IEGI VM'))
    admin.add_view(tenantsview(tenants,db.session, name='Tenants', category='Tabellen'))
    admin.add_view(iegisidview(iegisid,db.session, name='IEGISID', category='Tabellen'))
    admin.add_view(LoginView(name='Login',endpoint='login',url="/login"))
    admin.add_link(LogoutMenuLink(name='Logout', category='', url="/logout"))

    #Initialize flask login
    login_manager = LoginManager()
    login_manager.init_app(app)
    ldap_manager = LDAP3LoginManager(app)          # Setup a LDAP3 Login Manager.

    @login_manager.user_loader
    def load_user(user):
        qset=User.query.filter_by(cn=user).first()
        if qset:
            return qset
        else:
            return None
    logger.debug("Application started")

    # Declare The User Saver for Flask-Ldap3-Login
    # This method is called whenever a LDAPLoginForm() successfully validates.
    # Here you have to save the user, and return it so it can be used in the
    # login controller.
    @ldap_manager.save_user
    def save_user(dn, username, userdata, memberships):
        user=User.query.filter_by(cn=username).first()
        if not user:
            user = User(username, dn, "")
            db.session.add(user)
            db.session.commit()
        return user
    """
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        # Instantiate a LDAPLoginForm which has a validator to check if the user
        # exists in LDAP.
        form = LDAPLoginForm()

        if form.validate_on_submit():
            # Successfully logged in, We can now access the saved user object
            # via form.user.
            login_user(form.user)  # Tell flask-login to log them in.
            return redirect('/admin')  # Send them home

        return render_template('login.html', form=form)
    """
    @app.route('/logout',methods=['GET', 'POST'])
    @login_required
    def logout():
        logout_user()
        return redirect('/admin')    
    
    return app


def init_db():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    with app.app_context():
        db.create_all()
