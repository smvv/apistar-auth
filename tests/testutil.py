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

components = [
    SQLAlchemySessionComponent(url='sqlite:///:memory:'),
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


class TestCaseBase(object):
    def setup_method(self, test_method):
        # Disable bcrypt rounds to speedup testing.
        disable_bcrypt_hasher()

    @pytest.fixture(scope='function', params=[app])
    def client(self, request):
        database.Base.metadata.create_all(engine)
        # Adding '.local' to the hostname is necessary because
        # `eff_request_host()` (in http/cookiejar.py) adds it as well.
        # When it is not added here, the cookie will be discarded since
        # the domain 'testserver' != 'testserver.local'.
        yield TestClient(request.param, hostname='testserver.local')
        database.Base.metadata.drop_all(engine)

    @pytest.fixture(scope='function', params=[app])
    def admin(self, request):
        database.Base.metadata.create_all(engine)

        database.Session.configure(bind=engine)
        session = database.Session()

        admin = User(**self.admin_data())
        session.add(admin)

        admin_session = UserSession(user=admin)
        session.add(admin_session)

        session.commit()

        client = TestClient(request.param, hostname='testserver.local')
        client.cookies[SESSION_COOKIE_NAME] = str(admin_session.id)

        yield client

        database.Base.metadata.drop_all(engine)

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
