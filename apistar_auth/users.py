from typing import List

from apistar import Route, validators, types, http, Component
from apistar.exceptions import BadRequest
from apistar_sqlalchemy import database
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session, relationship
from sqlalchemy.exc import IntegrityError
from sqlalchemy_utils.types.choice import ChoiceType

from .auth import UserRole, authorized, UserSession
from .hasher import hasher


class User(database.Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    role = Column(ChoiceType(UserRole, impl=Integer()), nullable=False)
    fullname = Column(String)

    sessions = relationship('UserSession', order_by=UserSession.id,
                            back_populates='user')

    def __init__(self, *args, **kwargs):
        if 'role' in kwargs:
            kwargs['role'] = UserRole[kwargs['role']]
        super().__init__(*args, **kwargs)
        self.password = hasher().encrypt(self.password)

    def verify_password(self, password):
        return hasher().verify(password, self.password)

    def __repr__(self):
        msg = '<User(username=%s, role=%s, fullname=%s)>'
        return msg % (self.username, self.role, self.fullname)


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


class InputUserType(UserType):
    password = validators.String(min_length=1)


class UserComponent(Component):
    def __init__(self) -> None:
        pass

    def resolve(self, request: http.Request) -> User:
        return None


@authorized(UserRole.admin)
def list_users(session: Session) -> List[UserType]:
    return list(map(UserType, session.query(User).all()))


def create_user(session: Session, user_data: InputUserType,
                user: User) -> http.JSONResponse:
    new_user = User(**dict(user_data))
    if new_user.id is not None:
        raise BadRequest({'error': 'user ID cannot be set'})
    session.add(new_user)

    # TODO: check if current user has admin rights when trying to create an
    # admin account.

    try:
        session.commit()
    except IntegrityError as e:
        raise BadRequest({'error': 'username already exists'})

    return http.JSONResponse(UserType(new_user), status_code=201)


routes = [
    Route('/', 'GET', list_users),
    Route('/', 'POST', create_user),
]
