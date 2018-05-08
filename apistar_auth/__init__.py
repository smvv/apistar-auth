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
