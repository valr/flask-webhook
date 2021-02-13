import os

from application import create_application

application = create_application(os.environ.get('INSTANCE_PATH'))
