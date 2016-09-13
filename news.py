#
# Entry point for news app
#

from app import app as application, views, celery, tasks

application.run(host='127.0.0.1', port=8092)
