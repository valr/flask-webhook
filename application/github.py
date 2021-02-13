import hashlib
import hmac
import json
import os

from flask import Blueprint, current_app, jsonify, request

blueprint = Blueprint('github', __name__)


# https://docs.github.com/en/developers/webhooks-and-events/webhooks
@blueprint.route('/github', methods=['POST'])
def webhook_github():
    secret_key = current_app.config.get('GITHUB_SECRET_KEY')
    event_path = current_app.config.get('GITHUB_EVENT_PATH')

    if not secret_key or not event_path:
        return jsonify(
            error='Incorrect Github webhook configuration on server'), 503

    # get and verify the signature to ensure the payload is valid
    signature = request.headers.get('X-Hub-Signature-256')
    if not signature or not signature.startswith('sha256='):
        return jsonify(error='Missing or invalid X-Hub-Signature-256'), 400

    digest = hmac.new(bytes(secret_key, 'utf-8'),
                      request.data, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, 'sha256=' + digest):
        return jsonify(error='Invalid X-Hub-Signature-256'), 400

    # get and store the event
    event = request.headers.get('X-GitHub-Event')
    delivery = request.headers.get('X-GitHub-Delivery')
    payload = request.get_json(silent=True)

    with open(os.path.join(event_path, event + '.' + delivery), 'w') as file:
        file.write(json.dumps(payload))

    return jsonify({})
