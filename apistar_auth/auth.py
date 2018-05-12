from apistar import Route
from apistar.exceptions import HTTPException

from .models import User


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
    def on_request(self, route: Route, user: User):
        handler = route.handler
        if not hasattr(handler, 'needs_authorization'):
            return

        if not user:
            raise Unauthorized(dict(error='no authenticated user found'))

        # If there is no authorized role specified, we're done.
        if not hasattr(handler, 'authorized_role'):
            return

        required_role = handler.authorized_role

        if user.role != required_role:
            msg = 'invalid user role "{}" (expected: "{}")'
            error = msg.format(user.role.name, required_role.name)
            raise Unauthorized(dict(error=error))

        # Finally, the request is authorized!
