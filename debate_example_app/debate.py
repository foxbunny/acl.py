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
from auth_forms import login_form
from slugize import slugize

render = web.template.render('templates')
login_form = login_form()

title_re = web.form.regexp('.{5,255}', 'Title must be 5 to 255 characters long')
topic_re = web.form.regexp('.+', 'You must write your debate description')

debate_form = web.form.Form(
    web.form.Textbox('title', title_re, description='debate title'),
    web.form.Textarea('topic', topic_re, 
                      description='detailed topic description'),
    validators = [
        web.form.Validator('Debate with such title already exists',
                           lambda i: not web.config.db.where('debates',
                                                             title=i.title,
                                                             limit=1))
    ]
)

def in_base(content):
    """ Render content using base_template """
    return render.base_template(content, 
                                web.ctx.session.user,
                                login_form)

def render_login_required():
    """ Render the login required page """
    content = render.debates(debates)
    return in_base(content)


class debates:
    def GET(self):
        debates = web.config.db.select('debates')
        return in_base(render.debates(debates))
        
class new_debate:
    def GET(self):
        if not web.ctx.session.user:
            return in_base(render.debate_login_required())
        self.f = debate_form()
        return self.render_new_debate_page()

    def POST(self):
        if not web.ctx.session.user:
            return render_login_required()
        self.f = debate_form()
        if not self.f.validates():
            return render_new_debate_page()
        web.config.db.insert('debates',
                             title=self.f.d.title,
                             slug=slugize(self.f.d.title),
                             topic=self.f.d.topic,
                             author_id=web.ctx.session.user.id)
        web.seeother('/debate/%s' % slugize(self.f.d.title))

    def render_new_debate_page(self):
        return in_base(render.new_debate(self.f))

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

