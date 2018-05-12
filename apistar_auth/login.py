from apistar import Route, validators, types, http
from apistar.exceptions import BadRequest
from sqlalchemy.orm import Session

from .users import User, UserType, UserSession, prune_expired_sessions
from .cookies import get_session_cookie


class LoginType(types.Type):
    username = validators.String(min_length=1)
    password = validators.String(min_length=1)


def login(session: Session, request: http.Request,
          data: LoginType) -> UserType:
    user = session.query(User).filter(User.username == data.username).first()
    if not user:
        raise BadRequest(dict(error='Invalid username/password'))

    verified = user.verify_password(data.password)
    if not verified:
        raise BadRequest(dict(error='Invalid username/password'))

    user_session = UserSession(user=user)
    session.add(user_session)

    cookie = get_session_cookie(request.url, str(user_session.id))
    headers = {'Set-Cookie': cookie.output(header='')}

    prune_expired_sessions(session)

    return http.JSONResponse(UserType(user), headers=headers)


routes = [
    Route('/', 'POST', login),
]
