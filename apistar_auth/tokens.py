from typing import List

from apistar import Route, validators, types, http
from sqlalchemy.orm import Session

from .auth import authorized
from .models import Token, User
from .validators import UUID


class TokenType(types.Type):
    id = UUID()
    user_id = validators.Integer()

    created = validators.DateTime()
    updated = validators.DateTime()


@authorized
def list_tokens(session: Session, user: User) -> List[TokenType]:
    tokens = session.query(Token).filter(Token.user_id == user.id).all()
    return list(map(TokenType, tokens))


@authorized
def create_token(session: Session, user: User) -> http.JSONResponse:
    token = Token(user=user)
    session.add(token)
    session.commit()
    return http.JSONResponse(TokenType(token), status_code=201)


routes = [
    Route('/', 'GET', list_tokens),
    Route('/', 'POST', create_token),
]
