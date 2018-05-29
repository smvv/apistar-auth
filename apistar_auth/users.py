from http.cookies import SimpleCookie
from typing import List
from datetime import datetime, timedelta, timezone
import uuid

from apistar import Route, validators, types, http, Component
from apistar.exceptions import BadRequest
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import now
from sqlalchemy.exc import IntegrityError

from .auth import authorized
from .cookies import SESSION_COOKIE_NAME
from .models import Token, User, UserRole, UserSession, can_user_create_user
from .validators import UUID


class UserBaseType(types.Type):
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


class UserType(UserBaseType):
    created = validators.DateTime()
    updated = validators.DateTime()


class UserInputType(UserBaseType):
    password = validators.String(min_length=1)


class UserSessionType(types.Type):
    id = UUID()
    user_id = validators.Integer()

    created = validators.DateTime()
    updated = validators.DateTime()


session_expires_after = timedelta(days=3 * 30)
session_update_delay = timedelta(days=1)


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

    def resolve(self, request: http.Request, session: Session,
                token: http.QueryParam
                # pylint: disable=arguments-differ
                ) -> User:
        if token:
            try:
                token = uuid.UUID(token)
            except ValueError:
                return None

            user = session.query(User) \
                .join(Token) \
                .filter(Token.id == token).first()
            return user

        session_id = self.get_session_id(request.headers)
        if session_id:
            return self.resolve_with_session(session, session_id)

        return None

    def resolve_with_session(self, session, session_id):
        user, session_updated = session.query(User, UserSession.updated) \
            .join(UserSession) \
            .filter(UserSession.id == session_id).first()

        # SQLite does not support datetime timezones. Therefore, it will drop
        # the timezone part. When that's the case, we assume that the timezone
        # was utc since we're comparing with the current utc time.
        if session_updated.tzinfo is None:
            session_updated = session_updated.replace(tzinfo=timezone.utc)

        now_utc = datetime.now(timezone.utc)

        # Reject expired sessions.
        if session_updated <= now_utc - session_expires_after:
            prune_expired_sessions(session)
            session.commit()
            return None

        # Update session field 'updated' when the difference between now and
        # the last update is more than 'session_update_delay'. This avoids
        # updating the field too often.
        if now_utc - session_updated >= session_update_delay:
            session.query(UserSession) \
                .filter(UserSession.id == session_id) \
                .update({'updated': now()}, synchronize_session=False)
            session.commit()

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


@authorized
def list_user_session(session: Session, user: User) -> List[UserSessionType]:
    sessions = session.query(UserSession) \
        .filter(UserSession.user_id == user.id) \
        .all()
    return list(map(UserSessionType, sessions))


@authorized
def prune_expired_sessions(session: Session):
    expiration_date = datetime.now(timezone.utc) - session_expires_after
    session.query(UserSession) \
        .filter(UserSession.updated <= expiration_date) \
        .delete(synchronize_session=False)


routes = [
    Route('/', 'GET', list_users),
    Route('/', 'POST', create_user),
    Route('/sessions/', 'GET', list_user_session),
    Route('/sessions/expired/', 'DELETE', prune_expired_sessions),
]
