from .testutil import TestCaseUnauthenticatedBase
from apistar_auth.auth import SESSION_COOKIE_NAME
from apistar_auth.login import get_session_cookie


class TestCaseLogin(TestCaseUnauthenticatedBase):
    def test_login_unknown_user(self, client):
        resp = client.post('/login/', json={
            'username': 'foo',
            'password': 'bar',
        })
        assert resp.status_code == 400
        assert resp.json()['error'] == 'Invalid username/password'

    def test_login_success(self, client, user_data):
        resp = client.post('/users/', json=user_data)
        assert resp.status_code == 201
        assert resp.json()['id']

        resp = client.post('/login/', json=user_data)
        assert resp.status_code == 200
        assert resp.json()['username'] == user_data['username']
        assert 'password' not in resp.json()

    def test_login_failure(self, client, user_data):
        resp = client.post('/users/', json=user_data)
        assert resp.status_code == 201
        assert resp.json()['id']

        user_data.update({'password': 'invalid'})
        resp = client.post('/login/', json=user_data)
        assert resp.status_code == 400
        assert resp.json()['error'] == 'Invalid username/password'

    def test_session_cookie_security(self):
        url = 'https://testserver.local'
        cookie = get_session_cookie(url, 'session value')
        assert cookie[SESSION_COOKIE_NAME]['httponly']
        assert cookie[SESSION_COOKIE_NAME]['secure']
