import os
import sys
import site

# Add the virtual environment's site-packages to Python path
site.addsitedir('/home/hnoordam/workspace/api_db/venv/lib/python3.12/site-packages/')

# Add your app's directory to the Python path
sys.path.insert(0, '/home/hnoordam/workspace/api_db')

# Activate the virtual environment
activate_env = os.path.expanduser('/home/hnoordam/workspace/api_db/venv/bin/activate')
with open(activate_env) as f:
    code = compile(f.read(), activate_env, 'exec')
    exec(code, dict(__file__=activate_env))

# Import the Flask app
from app import create_app as application
