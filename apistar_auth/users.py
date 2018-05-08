from typing import List

from apistar import Route, validators, types, http, Component
from apistar.exceptions import BadRequest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .auth import authorized
from .models import User, UserRole


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

    def resolve(self, _: http.Request  # pylint: disable=arguments-differ
                ) -> User:
        return None


@authorized(UserRole.admin)
def list_users(session: Session) -> List[UserType]:
    return list(map(UserType, session.query(User).all()))


def create_user(session: Session, user_data: UserInputType,
                _: User) -> http.JSONResponse:
    new_user = User(**dict(user_data))
    if new_user.id is not None:
        raise BadRequest({'error': 'user ID cannot be set'})
    session.add(new_user)

    # TODO: check if current user has admin rights when trying to create an
    # admin account.

    try:
        session.commit()
    except IntegrityError:
        raise BadRequest({'error': 'username already exists'})

    return http.JSONResponse(UserType(new_user), status_code=201)


routes = [
    Route('/', 'GET', list_users),
    Route('/', 'POST', create_user),
]
