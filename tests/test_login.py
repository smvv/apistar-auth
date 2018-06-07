from datetime import datetime
import pytest

from .testutil import TestCaseUnauthenticatedBase

from apistar_auth import UserSession
from apistar_auth.users import session_expires_after, session_update_delay


class TestCaseLogin(TestCaseUnauthenticatedBase):
    def test_login_unknown_user(self, client):
        resp = client.post('/login', json={
            'username': 'foo',
            'password': 'bar',
        })
        assert resp.status_code == 400
        assert resp.json()['error'] == 'Invalid username/password'

    def test_login_success(self, client, user_data):
        resp = client.post('/users', json=user_data)
        assert resp.status_code == 201
        assert resp.json()['id']

        resp = client.post('/login', json=user_data)
        assert resp.status_code == 200
        assert resp.json()['username'] == user_data['username']
        assert 'password' not in resp.json()

    def test_login_failure(self, client, user_data):
        resp = client.post('/users', json=user_data)
        assert resp.status_code == 201
        assert resp.json()['id']

        user_data.update({'password': 'invalid'})
        resp = client.post('/login', json=user_data)
        assert resp.status_code == 400
        assert resp.json()['error'] == 'Invalid username/password'

    @pytest.fixture(scope='function', params=[True, False])
    def use_session_endpoint(self, request):
        return request.param

    def test_purge_expired_sessions(self, client, user_data, session,
                                    use_session_endpoint):
        resp = client.post('/users', json=user_data)
        assert resp.status_code == 201
        user_id = resp.json()['id']

        resp = client.post('/login', json=user_data)
        assert resp.status_code == 200

        resp = client.post('/login', json=user_data)
        assert resp.status_code == 200

        sessions = session.query(UserSession) \
            .filter(UserSession.user_id == user_id).all()
        assert len(sessions) == 2
        session_id = sessions[0].id

        # Set the created and updated field to an expired date.
        sessions[0].created = datetime.utcnow() - session_expires_after
        sessions[0].updated = datetime.utcnow() - session_expires_after

        if use_session_endpoint:
            resp = client.delete('/users/sessions/expired')
            assert resp.status_code == 200
        else:
            resp = client.post('/login', json=user_data)
            assert resp.status_code == 200

        sessions = session.query(UserSession) \
            .filter(UserSession.user_id == user_id).all()

        if use_session_endpoint:
            assert len(sessions) == 1
        else:
            assert len(sessions) == 2

        assert sessions[0].id != session_id

    def test_reject_expired_session(self, client, user_data, session):
        resp = client.post('/users', json=user_data)
        assert resp.status_code == 201
        user_id = resp.json()['id']

        resp = client.post('/login', json=user_data)
        assert resp.status_code == 200

        sessions = session.query(UserSession) \
            .filter(UserSession.user_id == user_id).all()
        assert len(sessions) == 1

        # Set the created and updated field to an expired date.
        sessions[0].created = datetime.utcnow() - session_expires_after
        sessions[0].updated = datetime.utcnow() - session_expires_after

        resp = client.get('/users/sessions')
        assert resp.status_code == 401

        sessions = session.query(UserSession) \
            .filter(UserSession.user_id == user_id).all()
        assert len(sessions) == 0

    def test_throttle_session_update(self, client, user_data, session):
        resp = client.post('/users', json=user_data)
        assert resp.status_code == 201
        user_id = resp.json()['id']

        resp = client.post('/login', json=user_data)
        assert resp.status_code == 200

        sessions = session.query(UserSession) \
            .filter(UserSession.user_id == user_id).all()
        assert len(sessions) == 1

        # Subtract the update delay from the created and updated fields.
        created = datetime.utcnow() - session_update_delay
        sessions[0].created = created
        sessions[0].updated = created

        resp = client.get('/users/sessions')
        assert resp.status_code == 200

        sessions = session.query(UserSession) \
            .filter(UserSession.user_id == user_id).all()
        assert len(sessions) == 1
        assert sessions[0].created == created
        assert (sessions[0].updated - datetime.utcnow()).total_seconds() <= 1.5
