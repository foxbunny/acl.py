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
     title      varchar(255) UNIQUE,
     slug       varchar(255) UNIQUE,
     topic      text,
     posted_at  timestamp DEFAULT CURRENT_TIMESTAMP,
     author_id  integer REFERENCES authenticationpy_users (id)
   );
   CREATE UNIQUE INDEX title_index ON debates USING btree (title);
   CREATE UNIQUE INDEX debates_slug_index ON debates USING btree (slug);

   CREATE TABLE arguments (
     id         serial PRIMARY KEY,
     debate_id  integer REFERENCES debates (id),
     slug       varchar(255) UNIQUE,
     argument   text,
     posted_at  timestamp DEFAULT CURRENT_TIMESTAMP,
     author_id  integer REFERENCES authenticationpy_users (id),
     UNIQUE (debate_id, author_id)
   );
   CREATE UNIQUE INDEX arguements_slug_index ON arguments USING btree (slug);

"""

import web

from authenticationpy.auth import User
from login_form import render_login_form

render = web.template.render('templates')

login_form_html = render_login_form()

class debates:
    def GET(self):
        # we have stored username in session at some point if authenticated
        uname = web.config.session.get('user')
        # we will take ``user == None`` to mean 'not authenticated'
        user = None
        if uname:
            # if username is not ``None``, grab the user from the database
            user = User.get_user(username=uname)
        debates = web.config.db.select('debates')
        return render.debates(debates, user, login_form_html)

class new_debate:
    def POST(self):
        pass


class debate:
    def GET(self, title):
        pass

    def POST(self, title):
        pass


class delete_debate:
    def POST(self, title):
        pass


class argument:
    def GET(self, title, username):
        pass

    def POST(self, title, username):
        pass


class delete_argument:
    def POST(self, title, username):
        pass

