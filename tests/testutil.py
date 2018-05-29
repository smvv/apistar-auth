from apistar import App, TestClient, http
from apistar_sqlalchemy import database
from apistar_sqlalchemy.components import SQLAlchemySessionComponent
import pytest
import os

from sqlalchemy.orm import Session

from apistar_auth import (
    AuthorizationHook,
    UserComponent,
    SESSION_COOKIE_NAME,
    routes,
    User,
    UserSession,
    disable_bcrypt_hasher,
)

from . import db_logger  # noqa


class SQLAlchemyTransactionHook:
    def on_request(self, session: Session):
        self.txn = session.begin_nested()

    def on_response(self, response: http.Response, session: Session,
                    exc: Exception) -> http.Response:
        if exc is None:
            self.txn.commit()
        return response

    def on_error(self, response: http.Response, session: Session
                 ) -> http.Response:
        self.txn.rollback()
        return response


def create_app(db_url: str):
    components = [
        SQLAlchemySessionComponent(url=db_url),
        UserComponent(),
    ]

    event_hooks = [
        AuthorizationHook(),
        SQLAlchemyTransactionHook(),
    ]

    # Create all SQL tables, if they do not exist.
    engine = components[0].engine
    database.Base.metadata.create_all(engine)

    app = App(routes=routes, components=components, event_hooks=event_hooks)
    app.debug = True

    return {
        "app": app,
        "engine": engine,
        "database": database,
    }


apps = [create_app('sqlite:///:memory:')]

if os.getenv('DATABASE_URL'):
    psql_app = create_app(os.getenv('DATABASE_URL'))
    apps += [psql_app]


class TestCaseBase(object):
    def setup_method(self, test_method):
        # Disable bcrypt rounds to speedup testing.
        disable_bcrypt_hasher()

    @pytest.fixture(scope='function', params=apps)
    def app(self, request):
        return request.param

    @pytest.fixture(scope='function')
    def session(self, app, request):
        app['database'].Session.remove()
        app['database'].Session.configure(bind=app['engine'])
        session = app['database'].Session()
        tnx = session.begin_nested()
        yield session
        tnx.rollback()

    @pytest.fixture(scope='function')
    def client(self, app, session):
        # Adding '.local' to the hostname is necessary because
        # `eff_request_host()` (in http/cookiejar.py) adds it as well.
        # When it is not added here, the cookie will be discarded since
        # the domain 'testserver' != 'testserver.local'.
        yield TestClient(app['app'], hostname='testserver.local')

    @pytest.fixture(scope='function')
    def admin(self, app, session):
        admin = User(**self.admin_data())
        session.add(admin)

        admin_session = UserSession(user=admin)
        session.add(admin_session)

        client = TestClient(app['app'], hostname='testserver.local')
        client.cookies[SESSION_COOKIE_NAME] = str(admin_session.id)
        yield client

    @pytest.fixture(scope='function')
    def admin_data(self):
        return {
            'username': 'admin',
            'password': 'bar',
            'role': 'admin',
            'fullname': 'foo bar',
        }


class TestCaseUnauthenticatedBase(TestCaseBase):
    @pytest.fixture(scope='function')
    def user_data(self):
        return {
            'username': 'user',
            'password': 'bar',
            'role': 'user',
            'fullname': 'foo bar',
        }
