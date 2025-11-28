from app import create_app
import logging
from datetime import datetime
from flask import request
from flask_login import UserMixin

logging.basicConfig(filename='error.log',level=logging.DEBUG)

app=create_app()

@app.after_request
def after_request(response):
    """ Logging all of the requests in JSON Per Line Format. """
    if request.method != 'GET':
        audit_logger = logging.getLogger('inbound_requests')
        audit_logger.info({
                "datetime": datetime.now().isoformat(),
                "response_status": response.status,
                "request_referrer": request.referrer,
                "request_user_agent": request.referrer,
                "request_body": request.form.to_dict(),
                "request_form": request.form,
                "response_body": response.json
            })
    return response

if __name__ == '__main__':
    app.config['FLASK_ENV'] = 'development'
    app.run(debug=True, host='0.0.0.0', port=5000)
    