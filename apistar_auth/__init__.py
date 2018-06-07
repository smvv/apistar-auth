# -*- coding: utf-8 -*-

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

__version__ = '0.5.0'
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

routes = login_routes + tokens_routes + users_routes
