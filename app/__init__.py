from flask import Flask, request
from .config import Config
from logging import getLogger
from logging.config import fileConfig
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.orm import configure_mappers
from .extensions import db, admin
from .models import groep, groeprechten, accounts, ipadressen, \
    groepview, groeprechtenview, accountsview, ipaddressenview
from .index import index
import pymysql
pymysql.install_as_MySQLdb()

#Get logging configuration
fileConfig("logging.config")
logger=getLogger(__name__)

def create_app():
    app = Flask(__name__)
    #Configuration from object, file config.py
    app.config.from_object(Config)

    #Initialize db
    db.init_app(app)
    app.register_blueprint(index, url_prefix='/')
    admin.name='API Accounts'
    admin.init_app(app)
    configure_mappers()
    admin.add_view(groepview(groep,db.session, name='Groepen'))
    admin.add_view(accountsview(accounts,db.session,name="Accounts"))
    admin.add_view(ipaddressenview(ipadressen,db.session,name="IP Adressen"))
    admin.add_view(groeprechtenview(groeprechten,db.session, name='Groep rechten'))
    logger.debug("Application started")
    return app

def init_db():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    with app.app_context():
        db.create_all()
