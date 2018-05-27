# -*- coding: utf-8 -*-

from apistar import Include

from .auth import (
    AuthorizationHook,
    authorized,
    Unauthorized,
)

from .cookies import SESSION_COOKIE_NAME

from .models import (
    Token,
    User,
    UserRole,
    UserSession,
)

from .login import (
    routes as login_routes
)

from .tokens import (
    routes as tokens_routes,
)

from .users import (
    routes as users_routes,
    UserInputType,
    UserType,
    UserComponent,
)

from .hasher import (
    disable_bcrypt_hasher,
    enable_bcrypt_hasher,
)

__version__ = '0.3.0'
__license__ = 'MIT'

__author__ = 'Sander Mathijs van Veen'
__email__ = 'sandervv+pypi@gmail.com'

__url__ = 'https://github.com/smvv/apistar-auth'
__description__ = \
    'Authentication integration based on SQLAlchemy for API Star.'

__all__ = [
    'AuthorizationHook', 'authorized', 'Unauthorized',
    'SESSION_COOKIE_NAME',
    'disable_bcrypt_hasher', 'enable_bcrypt_hasher',
    'Token',
    'User', 'UserInputType', 'UserType', 'UserRole', 'UserSession',
    'UserComponent',
    'routes',
]

routes = [
    Include('/login', name='login', routes=login_routes),
    Include('/tokens', name='tokens', routes=tokens_routes),
    Include('/users', name='users', routes=users_routes),
]
