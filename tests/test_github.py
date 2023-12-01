import hashlib
import hmac
import json
from pathlib import Path

from flask import Flask
from flask.testing import FlaskClient
from pytest import MonkeyPatch


def test_github_incorrect_configuration(
    application: Flask, client: FlaskClient, monkeypatch: MonkeyPatch
):
    data = {"key": "value"}
    headers = {"Content-Type": "application/json"}

    monkeypatch.delitem(application.config, "GITHUB_SECRET_KEY")

    response = client.post("/github", headers=headers, data=json.dumps(data))

    assert response.status_code == 503

    monkeypatch.undo()
    monkeypatch.delitem(application.config, "GITHUB_EVENT_PATH")

    response = client.post("/github", headers=headers, data=json.dumps(data))

    assert response.status_code == 503


def test_github_missing_or_invalid_signature(client: FlaskClient):
    data = {"key": "value"}
    headers = {"Content-Type": "application/json"}

    response = client.post("/github", headers=headers, data=json.dumps(data))

    assert response.status_code == 400
    assert b"Missing" in response.data

    headers = {"Content-Type": "application/json", "X-Hub-Signature-256": "invalid"}

    response = client.post("/github", headers=headers, data=json.dumps(data))

    assert response.status_code == 400
    assert b"Missing" in response.data


def test_github_invalid_signature(client: FlaskClient):
    data = {"key": "value"}
    headers = {
        "Content-Type": "application/json",
        "X-Hub-Signature-256": "sha256=invalid",
    }

    response = client.post("/github", headers=headers, data=json.dumps(data))

    assert response.status_code == 400
    assert b"Missing" not in response.data


def test_github_valid_signature(
    application: Flask, client: FlaskClient, tmp_path: Path, monkeypatch: MonkeyPatch
):
    directory = tmp_path / "github"
    directory.mkdir()

    monkeypatch.setitem(application.config, "GITHUB_EVENT_PATH", str(directory))

    data = {"key": "value"}

    event = "ping"
    delivery = "01234567-89ab-cedf-0123-456789abcdef"
    signature = (
        "sha256="
        + hmac.new(
            bytes(application.config.get("GITHUB_SECRET_KEY"), "utf-8"),
            bytes(json.dumps(data), "utf-8"),
            hashlib.sha256,
        ).hexdigest()
    )

    headers = {
        "Content-Type": "application/json",
        "X-GitHub-Event": event,
        "X-GitHub-Delivery": delivery,
        "X-Hub-Signature-256": signature,
    }

    response = client.post("/github", headers=headers, data=json.dumps(data))

    assert response.status_code == 200

    file = directory / str(event + "." + delivery)
    assert file.read_text() == json.dumps(data)
