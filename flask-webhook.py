import os

from flask_webhook import create_application

application = create_application(os.environ.get("INSTANCE_PATH"))
