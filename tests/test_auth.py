from .testutil import TestCaseUnauthenticatedBase
from apistar_auth import SESSION_COOKIE_NAME


class TestCaseAuth(TestCaseUnauthenticatedBase):
    def test_authorize_success(self, user_data, admin_data, client, admin):
        resp = client.post('/users', json=user_data)
        assert resp.status_code == 201

        resp = client.post('/login', json=user_data)
        assert resp.status_code == 200
        assert resp.cookies[SESSION_COOKIE_NAME]

        resp = admin.get('/users')
        assert resp.status_code == 200
        body = resp.json()
        assert len(body) == 2
        assert body[0]['username'] == admin_data['username']
        assert body[1]['username'] == user_data['username']

    def test_invalid_user_role(self, user_data, client):
        resp = client.post('/users', json=user_data)
        assert resp.status_code == 201

        resp = client.post('/login', json=user_data)
        assert resp.status_code == 200
        assert resp.json()['role'] == 'user'
        assert resp.cookies[SESSION_COOKIE_NAME]

        resp = client.get('/users')
        assert resp.status_code == 401
        assert 'invalid user role' in resp.json()['error']

    def test_authorize_invalid_cookie(self, user_data, client):
        error_no_user_found = 'no authenticated user found'

        resp = client.get('/users', json=user_data)
        assert resp.status_code == 401
        assert resp.json()['error'] == error_no_user_found

        client.cookies['unknown_cookie_name'] = 'session_value'
        resp = client.get('/users', json=user_data)
        assert resp.status_code == 401
        assert resp.json()['error'] == error_no_user_found

        client.cookies[SESSION_COOKIE_NAME] = ''
        resp = client.get('/users', json=user_data)
        assert resp.status_code == 401
        assert resp.json()['error'] == error_no_user_found
