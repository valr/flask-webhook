from flask import Flask


def create_application(instance_path, config_file='flask-webhook.conf'):
    if instance_path:
        application = Flask(
            __name__, instance_relative_config=True, instance_path=instance_path
        )
    else:
        application = Flask(__name__, instance_relative_config=True)

    application.config.from_pyfile(config_file)

    from .github import blueprint as github_blueprint
    application.register_blueprint(github_blueprint, url_prefix="")

    return application
