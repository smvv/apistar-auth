import re
import time
import logging

from sqlalchemy import event
from sqlalchemy.engine import Engine

logging.basicConfig(format='%(message)s')
logger = logging.getLogger('db')
logger.setLevel(logging.DEBUG)


@event.listens_for(Engine, 'before_cursor_execute')
def before_cursor_execute(conn, cursor, statement,
                          parameters, context, executemany):
    context._query_start_time = time.time()


@event.listens_for(Engine, 'after_cursor_execute')
def after_cursor_execute(conn, cursor, statement,
                         parameters, context, executemany):

    total = int(round((time.time() - context._query_start_time) * 1000))

    if statement.startswith('PRAGMA table_info(') and total == 0:
        return

    statement = re.sub('\s+', ' ', statement).strip()
    print('SQL %dms %s' % (total, statement))

    if parameters:
        print('SQL parameters: %r' % (parameters,))
