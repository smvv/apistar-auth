# -*- coding: utf-8 -*-
__version__ = '0.0.1'
__license__ = 'MIT'

__author__ = 'Sander Mathijs van Veen'
__email__ = 'sandervv+pypi@gmail.com'

__url__ = 'https://github.com/smvv/apistar-auth'
__description__ = \
    'Authentication integration based on SQLAlchemy for API Star.'

from apistar import Include

from .auth import (
    AuthorizationHook,
    authorized,
    Unauthorized,
    SESSION_COOKIE_NAME,
    UserRole,
    UserSession,
)

from .login import (
    routes as login_routes
)

from .users import (
    routes as users_routes,
    User,
    UserComponent,
)

from .hasher import (
    disable_bcrypt_hasher,
    enable_bcrypt_hasher,
)

__all__ = [
    'AuthorizationHook', 'authorized', 'Unauthorized',
    'SESSION_COOKIE_NAME',
    'disable_bcrypt_hasher', 'enable_bcrypt_hasher',
    'User', 'UserInputType', 'UserType', 'UserRole', 'UserSession',
    'UserComponent',
    'routes',
]

routes = [
    Include('/login', name='login', routes=login_routes),
    Include('/users', name='users', routes=users_routes),
]
