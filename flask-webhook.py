import hashlib
import hmac
import os

from flask import Flask, request

instance_path = os.environ.get('INSTANCE_PATH')
if instance_path:
    application = Flask(__name__,
                        instance_relative_config=True,
                        instance_path=instance_path)
else:
    application = Flask(__name__, instance_relative_config=True)

application.config.from_pyfile('flask-webhook.conf')


# https://docs.github.com/en/developers/webhooks-and-events/webhooks
@application.route('/github', methods=['POST'])
def webhook_github():
    # get and verify the signature to ensure the payload is valid
    signature = request.headers.get('X-Hub-Signature-256')
    if not signature or not signature.startswith('sha256='):
        return 'Missing or invalid X-Hub-Signature-256', 400

    key = bytes(application.config.get('GITHUB_SECRET_KEY', ''), 'utf-8')
    if not key:
        return 'Missing Github secret key on server', 503

    digest = hmac.new(key, request.data, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, 'sha256=' + digest):
        return 'Invalid X-Hub-Signature-256', 400

    # get the event and the payload
    event = request.headers.get('X-GitHub-Event')
    payload = request.get_json(silent=True)

    # print(event)
    # print(payload)

    # process push event
    if event == 'push':
        repository = payload.get('repository', {}).get('name')
        print(f'processing event: "{event}" on repository: "{repository}"')

    return 'OK'
