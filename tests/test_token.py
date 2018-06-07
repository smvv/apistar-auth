from .testutil import TestCaseUnauthenticatedBase


class TestCaseUsers(TestCaseUnauthenticatedBase):
    def test_create_token(self, client, user_data):
        resp = client.post('/users', json=user_data)
        assert resp.status_code == 201
        assert resp.json()['id']

        resp = client.post('/login', json=user_data)
        assert resp.status_code == 200

        resp = client.post('/tokens')
        assert resp.status_code == 201

        token = resp.json()['id']

        client.cookies.clear()
        resp = client.get('/tokens')
        assert resp.status_code == 401

        resp = client.get('/tokens', params=dict(token=token))
        assert resp.status_code == 200

        body = resp.json()
        assert len(body) == 1
        assert body[0]['id'] == token

    def test_invalid_token(self, client):
        token = 'abc' * 20
        resp = client.get('/tokens', params=dict(token=token))
        assert resp.status_code == 401
