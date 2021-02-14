import os

import pytest
from application import create_application


@pytest.fixture
def application():
    application = create_application(os.environ.get('INSTANCE_PATH'))
    application.testing = True

    return application


@pytest.fixture
def client(application):
    return application.test_client()
