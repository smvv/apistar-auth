from .testutil import TestCaseUnauthenticatedBase
from datetime import datetime


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

        date_format = '%Y-%m-%dT%H:%M:%S'
        created = datetime.strptime(body[1]['created'], date_format)
        updated = datetime.strptime(body[1]['updated'], date_format)
        assert created == updated
        assert (created - datetime.now()).total_seconds() <= 1.5

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

    def test_invalid_user_roles(self, client, user_data):
        user_data['role'] = 'admin'
        resp = client.post('/users/', json=user_data)
        assert resp.status_code == 400
        error = 'user cannot create user with role "admin"'
        assert resp.json()['error'] == error

        user_data['role'] = 'unknown_role'
        resp = client.post('/users/', json=user_data)
        assert resp.status_code == 400
        assert resp.json()['role'] == 'Must be a valid choice.'

    def test_user_can_create_user(self, client, user_data):
        resp = client.post('/users/', json=user_data)
        assert resp.status_code == 201
        assert resp.json()['id'] == 1
        assert resp.json()['role'] == 'user'

        resp = client.post('/login/', json=user_data)
        assert resp.status_code == 200

        user_data['username'] = 'new_user'
        resp = client.post('/users/', json=user_data)
        assert resp.status_code == 201
        assert resp.json()['id'] == 2
        assert resp.json()['role'] == 'user'

        user_data['user_data'] = 'new_admin'
        user_data['role'] = 'admin'
        resp = client.post('/users/', json=user_data)
        assert resp.status_code == 400
        error = 'user cannot create user with role "admin"'
        assert resp.json()['error'] == error

    def test_admin_can_create_user(self, admin, user_data):
        resp = admin.post('/users/', json=user_data)
        assert resp.status_code == 201
        assert resp.json()['id'] == 2
        assert resp.json()['username'] == user_data['username']
        assert resp.json()['role'] == 'user'

    def test_admin_can_create_admin(self, admin, user_data):
        user_data['role'] = 'admin'
        resp = admin.post('/users/', json=user_data)
        assert resp.status_code == 201
        assert resp.json()['id'] == 2
        assert resp.json()['username'] == user_data['username']
        assert resp.json()['role'] == 'admin'

    def test_list_user_sessions(self, client, user_data):
        resp = client.get('/users/sessions/')
        assert resp.status_code == 401
        assert resp.json()['error'] == 'no authenticated user found'

        resp = client.post('/users/', json=user_data)
        assert resp.status_code == 201

        resp = client.post('/login/', json=user_data)
        assert resp.status_code == 200

        resp = client.get('/users/sessions/')
        assert resp.status_code == 200
        body = resp.json()
        assert len(body) == 1

        assert body[0]['id']
        assert body[0]['user_id'] == 1

        date_format = '%Y-%m-%dT%H:%M:%S'
        created = datetime.strptime(body[0]['created'], date_format)
        updated = datetime.strptime(body[0]['updated'], date_format)
        assert created == updated
        assert (created - datetime.now()).total_seconds() <= 1.5

        resp = client.post('/login/', json=user_data)
        assert resp.status_code == 200

        resp = client.get('/users/sessions/')
        assert resp.status_code == 200
        assert len(resp.json()) == 2
