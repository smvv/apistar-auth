from http.cookies import SimpleCookie
from typing import List

from apistar import Route, validators, types, http, Component
from apistar.exceptions import BadRequest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .auth import authorized
from .models import User, UserRole, UserSession, can_user_create_user


SESSION_COOKIE_NAME = 'session_id'


class UserType(types.Type):
    id = validators.Integer(allow_null=True)
    username = validators.String(min_length=1)
    role = validators.String(
        enum=list(UserRole.__members__.keys()),
        allow_null=True,
        default='user'
    )
    fullname = validators.String(min_length=1)

    def __init__(self, *args, **kwargs):
        patched = []
        for arg in args:
            if isinstance(arg, User):
                # Convert enum name to string.
                role = arg.role.name
                arg = arg.__dict__
                arg['role'] = role
            patched.append(arg)
        super().__init__(*patched, **kwargs)


class UserInputType(UserType):
    password = validators.String(min_length=1)


class UserComponent(Component):
    def __init__(self) -> None:
        pass

    def get_session_id(self, headers):
        cookie_header = headers.get('cookie')
        if not cookie_header:
            return None

        cookie = SimpleCookie()
        cookie.load(cookie_header)

        session_id_cookie = cookie.get(SESSION_COOKIE_NAME)
        if not session_id_cookie:
            return None

        return session_id_cookie.value

    def resolve(self, request: http.Request, session: Session
                # pylint: disable=arguments-differ
                ) -> User:
        session_id = self.get_session_id(request.headers)
        if not session_id:
            return None

        user = session.query(User) \
            .join(UserSession) \
            .filter(UserSession.id == session_id).first()

        return user


@authorized(UserRole.admin)
def list_users(session: Session) -> List[UserType]:
    return list(map(UserType, session.query(User).all()))


def create_user(session: Session, user_data: UserInputType,
                user: User) -> http.JSONResponse:
    new_user = User(**dict(user_data))

    if new_user.id is not None:
        raise BadRequest({'error': 'user ID cannot be set'})

    if not can_user_create_user(user, new_user):
        msg = 'user cannot create user with role "{}"'
        raise BadRequest({'error': msg.format(new_user.role.name)})

    session.add(new_user)

    try:
        session.commit()
    except IntegrityError:
        raise BadRequest({'error': 'username already exists'})

    return http.JSONResponse(UserType(new_user), status_code=201)


routes = [
    Route('/', 'GET', list_users),
    Route('/', 'POST', create_user),
]
