from http.cookies import SimpleCookie

from apistar import http, Route
from apistar.exceptions import HTTPException
from sqlalchemy.orm import Session

from .models import User, UserSession


SESSION_COOKIE_NAME = 'session_id'


def _mark_authorization(f, role=None):
    f.needs_authorization = True
    if role is not None:
        f.authorized_role = role


def authorized(role=None):
    if hasattr(role, '__call__'):
        _mark_authorization(role)
        return role

    def outer(f):
        _mark_authorization(f, role)
        return f
    return outer


class Unauthorized(HTTPException):
    default_status_code = 401
    default_detail = 'Unauthorized'


class AuthorizationHook:
    def get_session_id(self, headers):
        cookie_header = headers.get('cookie')
        if not cookie_header:
            raise Unauthorized(dict(error='no cookie header found'))

        cookie = SimpleCookie()
        cookie.load(cookie_header)

        session_id_cookie = cookie.get(SESSION_COOKIE_NAME)
        if not session_id_cookie:
            error = 'no cookie named "{}" found'.format(SESSION_COOKIE_NAME)
            raise Unauthorized(dict(error=error))

        session_id = session_id_cookie.value
        if not session_id:
            error = 'invalid value for cookie "{}"'.format(SESSION_COOKIE_NAME)
            raise Unauthorized(dict(error=error))

        return session_id

    # TODO purge expired sessions.

    def on_request(self, route: Route, request: http.Request,
                   session: Session):
        handler = route.handler
        if not hasattr(handler, 'needs_authorization'):
            return

        session_id = self.get_session_id(request.headers)

        user = session.query(User) \
            .join(UserSession) \
            .filter(UserSession.id == session_id).first()

        if not user:
            raise Unauthorized()

        # If there is no authorized role specified, we're done.
        if not hasattr(handler, 'authorized_role'):
            return

        required_role = handler.authorized_role

        if user.role != required_role:
            msg = 'invalid user role "{}" (expected: "{}")'
            error = msg.format(user.role.name, required_role.name)
            raise Unauthorized(dict(error=error))

        # Finally, the request is authorized!
