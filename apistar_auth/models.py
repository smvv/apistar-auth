import enum
import uuid
import secrets

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy_utils.types.choice import ChoiceType
from apistar_sqlalchemy import database

from .guid import GUID
from .hasher import hasher


class UserRole(enum.Enum):
    admin = 1
    user = 2


class User(database.Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    role = Column(ChoiceType(UserRole, impl=Integer()), nullable=False)
    fullname = Column(String)

    # TODO add Column 'created'

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
        msg = '<User(username=%s, role=%s, fullname=%s)>'
        return msg % (self.username, self.role, self.fullname)


class UserSession(database.Base):
    __tablename__ = 'user_sessions'

    id = Column(GUID, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))

    # TODO add Column 'created'

    user = relationship('User', back_populates='sessions')

    def __init__(self, user):
        self.id = self.generate_session_id()
        self.user = user

    def generate_session_id(self):
        return uuid.UUID(bytes=secrets.token_bytes(16))
