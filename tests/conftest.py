# tests/conftest.py
import pytest
from testcontainers.postgres import PostgresContainer
from main import create_app
from db import db
import os


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:15-alpine") as postgres:
        url = postgres.get_connection_url()

        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg2://")

        yield url


@pytest.fixture(scope="session")
def app(postgres_container):

    os.environ["SQLALCHEMY_DATABASE_URI"] = postgres_container

    flask_app = create_app()

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture(autouse=True)
def mock_auth(monkeypatch):
    fake_token = {"sub": "test-user", "https://social-insper.com/roles": ["ADMIN"]}
    monkeypatch.setattr("auth.require_auth.acquire_token", lambda *a, **kw: fake_token)
    monkeypatch.setattr(
        "auth.require_auth.__call__",
        lambda *a, **kw: (lambda f: f),
    )


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def unauth_client(app, monkeypatch):
    from authlib.oauth2.rfc6749.errors import MissingAuthorizationError

    def raise_missing(*args, **kwargs):
        raise MissingAuthorizationError()

    monkeypatch.setattr("auth.require_auth.acquire_token", raise_missing)
    return app.test_client()


@pytest.fixture()
def non_admin_client(app, monkeypatch):
    fake_token = {"sub": "test-user", "https://social-insper.com/roles": []}
    monkeypatch.setattr("auth.require_auth.acquire_token", lambda *a, **kw: fake_token)
    return app.test_client()
