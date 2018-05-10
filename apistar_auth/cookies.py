from http.cookies import SimpleCookie
from datetime import datetime, timedelta
from urllib.parse import urlparse


SESSION_COOKIE_NAME = 'session_id'


def get_session_cookie(url: str, session_id: str) -> SimpleCookie:
    parsed = urlparse(url)

    cookie = SimpleCookie()
    cookie[SESSION_COOKIE_NAME] = session_id
    cookie[SESSION_COOKIE_NAME]['path'] = '/'
    cookie[SESSION_COOKIE_NAME]['httponly'] = True

    if parsed.scheme == 'https':
        cookie[SESSION_COOKIE_NAME]['secure'] = True

    cookie[SESSION_COOKIE_NAME]['domain'] = '.' + parsed.netloc

    expires = datetime.utcnow() + timedelta(days=3 * 30)
    date_format = '%a, %d %b %Y %H:%M:%S GMT'
    cookie[SESSION_COOKIE_NAME]['expires'] = expires.strftime(date_format)

    return cookie
