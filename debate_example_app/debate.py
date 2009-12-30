""" 
authentication.py Example App: Debate
=====================================

Database schema
---------------

This is an example of the database schema for PostgreSQL. You must adapt the
schema to your own database server, and create the specified tables before
using the example app. It is assumed that the autentication.py users table is
called ``authenticationpy_users``, and you should edit this name if your table
is called differently. ::

   CREATE TABLE debates (
     id         serial PRIMARY KEY,
     summary    varchar(255),
     topic      text,
     posted_at  timestamp DEFAULT CURRENT_TIMESTAMP
     author_id  integer REFERENCES authenticationpy_users (id)
   );

   CREATE TABLE arguments (
     id         serial PRIMARY KEY,
     debate_id  integer REFERENCES debates (id)
     argument   text,
     posted_at  timestamp DEFAULT CURRENT_TIMESTAMP
     author_id  integer REFERENCES authenticationpy_users (id)
     UNIQUE (debate_id, author_id)
   );

"""

import web
from authenticationpy.auth import User

db = web.config.db
admin_username = web.config.admin


class debates:
    def GET(self):
        pass

    def POST(self):
        pass


class debate:
    def GET(self):
        pass

    def POST(self):
        pass


class argument:
    def GET(self):
        pass

    def POST(self):
        pass
