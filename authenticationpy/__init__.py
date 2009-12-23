import web

try:
    DATABASE = web.config.db
except AttributeError:
    DATABASE = None
