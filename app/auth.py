from flask_admin import expose, BaseView
from flask import flash, redirect
from flask_login import current_user, login_user
from .config import Config
from .config import Config
from .ldaplogin import ldapLogin, ldapLoginForm
from logging import getLogger
from .models import user_datastore

logger=getLogger(__name__)

class LoginView(BaseView):    
    @expose('/', methods=["GET","POST"])
    def index(self):
            # Instantiate a LDAPLoginForm which has a validator to check if the user
        # exists in LDAP.
        form = ldapLoginForm()
        if form.validate_on_submit():
            #Data from checked, now login on LDAP
            #First authenticate
            ldlogin=ldapLogin()
            if ldlogin.authenticate(userid=form.username.data,password=form.password.data):
                logger.debug(f"Login of {form.username.data} succeeded")
                #Get all attributes of user
                userattrs=ldlogin.getUserAttributes()
                logger.debug(f"User attributes: {userattrs}")
                #Now get the groups of the user
                groups=ldlogin.getGroups()
                logger.debug(f'Usergroups found: {groups}')
                if groups:
                    logger.debug(f"Reading groups for {form.username.data} succeeded")
                    #Check if groups are mapped to role, add to list if so
                    userroles=[]
                    for group in groups:
                        if group in Config.GROUP_ROLE_MAP:
                            userroles.append(Config.GROUP_ROLE_MAP[group])
                    if not userroles:
                        flash('U heeft geen toegang op deze applicatie.', category='error')
                        return self.render('admin/login.html',form=form)  # Send them home    
                    user=user_datastore.find_user(name=form.username.data)
                    logger.debug(f"Read user: {user}")
                    if not user:
                        user=user_datastore.create_user(email=userattrs['attributes'][Config.LDAP_MAIL_ATTRIBUTE][0],roles=userroles,name=ldlogin.cn)
                        user_datastore.commit()
                        logger.debug(f"Writing of {form.username.data} succeeded.")
                    #Reset all roles
                    for role in user.roles:
                        user_datastore.remove_role_from_user(user,role)
                    for role in userroles:
                        user_datastore.add_role_to_user(user,role)
                    user_datastore.commit()
                    logger.debug(f'Logging in user: {user} ')
                    login_user(user)  # Tell flask-login to log them in.
                    flash("U bent succesvol ingelogd.",'succes')
                    ldlogin.ldapconn.unbind()
                    return self.render('index.html')  # Send them home
                else:
                    flash('U heeft geen toegang op deze applicatie.', category='error')
                    return self.render('admin/login.html',form=form)  # Send them home    
            if form.errors:
                flash('Fout bij inloggen, probeer opnieuw.', 'error')
        return self.render('admin/login.html',form=form)       

    def is_accessible(self):
        return not current_user.is_authenticated 

