import enum
import uuid
import secrets

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import now
from sqlalchemy_utils.types.choice import ChoiceType
from apistar_sqlalchemy import database

from .guid import GUID
from .hasher import hasher


class UserRole(enum.Enum):
    admin = 1
    user = 2


def can_user_create_user(user, new_user):
    if not user:
        # Unauthenticated users can only create a new user account.
        return new_user.role == UserRole.user

    # Admins can create any account.
    if user.role == UserRole.admin:
        return True

    # Else, users can only create a user account.
    assert user.role == UserRole.user
    return user.role == new_user.role


class User(database.Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    role = Column(ChoiceType(UserRole, impl=Integer()), nullable=False)
    fullname = Column(String)

    created = Column(DateTime(timezone=True), server_default=now())
    updated = Column(DateTime(timezone=True), server_default=now(),
                     onupdate=now())

    sessions = relationship('UserSession',  # order_by='user_sessions.created',
                            back_populates='user')

    def __init__(self, *args, **kwargs):
        # Convert role name to enum value.
        kwargs['role'] = UserRole[kwargs['role']]
        super().__init__(*args, **kwargs)
        self.password = hasher().encrypt(self.password)

    def verify_password(self, password):
        return hasher().verify(password, self.password)

    def __repr__(self):
        msg = '<User(username=%r, role=%s, fullname=%r)>'
        return msg % (self.username, self.role.name, self.fullname)


class UserSession(database.Base):
    __tablename__ = 'user_sessions'

    id = Column(GUID, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))

    created = Column(DateTime(timezone=True), server_default=now())
    updated = Column(DateTime(timezone=True), server_default=now(),
                     onupdate=now(), index=True)

    user = relationship('User', back_populates='sessions')

    def __init__(self, user):
        self.id = self.generate_session_id()
        self.user = user

    def __repr__(self):
        msg = '<UserSession(id=%r, user_id=%r, created=%s, updated=%s)>'
        return msg % (self.id, self.user_id, self.created, self.updated)

    def generate_session_id(self):
        return uuid.UUID(bytes=secrets.token_bytes(16))


class Token(database.Base):
    __tablename__ = 'tokens'

    id = Column(GUID, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))

    created = Column(DateTime(timezone=True), server_default=now())
    updated = Column(DateTime(timezone=True), server_default=now(),
                     onupdate=now(), index=True)

    user = relationship('User')

    def __init__(self, user):
        self.id = self.generate_session_id()
        self.user = user

    def __repr__(self):
        msg = '<Token(id=%r, user_id=%r, created=%s, updated=%s)>'
        return msg % (self.id, self.user_id, self.created, self.updated)

    def generate_session_id(self):
        return uuid.UUID(bytes=secrets.token_bytes(16))
