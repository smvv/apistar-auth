from apistar_auth.cookies import get_session_cookie, SESSION_COOKIE_NAME

from .testutil import TestCaseUnauthenticatedBase


class TestCaseLogin(TestCaseUnauthenticatedBase):
    def test_session_cookie_security(self):
        url = 'https://testserver.local'
        cookie = get_session_cookie(url, 'session value')
        assert cookie[SESSION_COOKIE_NAME]['httponly']
        assert cookie[SESSION_COOKIE_NAME]['secure']
