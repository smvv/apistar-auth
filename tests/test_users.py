from .testutil import TestCaseUnauthenticatedBase
from apistar_auth import User


class TestCaseUsers(TestCaseUnauthenticatedBase):
    def test_create_and_list_users(self, admin, client, user_data):
        resp = admin.get('/users/')
        assert resp.status_code == 200
        assert len(resp.json()) == 1

        resp = client.post('/users/', json=user_data)
        assert resp.status_code == 201
        assert resp.json()['id']

        resp = admin.get('/users/')
        assert resp.status_code == 200
        body = resp.json()
        assert len(body) == 2
        assert body[1]['id'] == 2

        assert 'password' not in body[1]
        for key, value in user_data.items():
            if key == 'password':
                continue
            assert body[1][key] == value

    def test_create_failures(self, client, admin):
        resp = client.post('/users/', json={})
        assert resp.status_code == 400

        resp = client.post('/users/', json={
            'username': '',
            'password': '',
            'fullname': '',
        })
        assert resp.status_code == 400

        resp = client.post('/users/', json={
            'id': 42,
            'username': 'a',
            'password': 'b',
            'fullname': 'c',
        })
        assert resp.status_code == 400
        assert resp.json()['error'] == 'user ID cannot be set'

        resp = admin.get('/users/')
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        assert resp.json()[0]['role'] == 'admin'

    def test_create_duplicate_user(self, admin, client):
        resp = client.post('/users/', json={
            'username': 'a',
            'password': 'b',
            'fullname': 'c',
        })
        assert resp.status_code == 201

        resp = client.post('/users/', json={
            'username': 'a',
            'password': 'b',
            'fullname': 'c',
        })
        assert resp.status_code == 400
        assert resp.json()['error'] == 'username already exists'

        resp = admin.get('/users/')
        assert resp.status_code == 200
        body = resp.json()
        assert len(body) == 2
        assert body[0]['role'] == 'admin'
        assert body[1]['username'] == 'a'
        assert body[1]['role'] == 'user'

    def test_create_admin_as_user(self, client):
        resp = client.post('/users/', json={
            'username': 'a',
            'password': 'a',
            'role': 'user',
            'fullname': 'a',
        })
        assert resp.status_code == 201

        resp = client.post('/users/', json={
            'username': 'b',
            'password': 'b',
            'role': 'admin',
            'fullname': 'b',
        })
        assert resp.status_code == 201
