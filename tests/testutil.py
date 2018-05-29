from apistar import App, TestClient
from apistar_sqlalchemy import database
from apistar_sqlalchemy.components import SQLAlchemySessionComponent
from apistar_sqlalchemy.event_hooks import SQLAlchemyTransactionHook
import pytest

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


sqlite_app = create_app('sqlite:///:memory:')


class TestCaseBase(object):
    def setup_method(self, test_method):
        # Disable bcrypt rounds to speedup testing.
        disable_bcrypt_hasher()

    @pytest.fixture(scope='function', params=[sqlite_app])
    def app(self, request):
        return request.param

    @pytest.fixture(scope='function')
    def session(self, app, request):
        app['database'].Session.configure(bind=app['engine'])
        return app['database'].Session()

    @pytest.fixture(scope='function')
    def client(self, app):
        app['database'].Base.metadata.create_all(app['engine'])
        # Adding '.local' to the hostname is necessary because
        # `eff_request_host()` (in http/cookiejar.py) adds it as well.
        # When it is not added here, the cookie will be discarded since
        # the domain 'testserver' != 'testserver.local'.
        yield TestClient(app['app'], hostname='testserver.local')
        app['database'].Base.metadata.drop_all(app['engine'])

    @pytest.fixture(scope='function')
    def admin(self, app, session):
        app['database'].Base.metadata.create_all(app['engine'])
        admin = User(**self.admin_data())
        session.add(admin)

        admin_session = UserSession(user=admin)
        session.add(admin_session)

        session.commit()

        client = TestClient(app['app'], hostname='testserver.local')
        client.cookies[SESSION_COOKIE_NAME] = str(admin_session.id)
        yield client
        app['database'].Base.metadata.drop_all(app['engine'])

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
