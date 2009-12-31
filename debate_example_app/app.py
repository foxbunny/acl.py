import web

import config
from debate import *
from authenticationpy.auth import User, UserAccountError
from auth_forms import login_form, register_form

urls = (
    '/', 'debates',
    '/new', 'new_debate',
    '/(?P<title>[\w_]+)/', 'debate',
    '/(?P<title>[\w_]+)/delete', 'delete_debate',
    '/(?P<title>[\w_]+)/arguments/(?P<username>.*)/', 'argument',
    '/(?P<title>[\w_]+)/arguments/(?P<username>.*)/delete', 'delete_argument',
    '/login', 'login',
    '/logoff', 'logoff',
    '/register', 'register',
    '/unregister', 'unregister',
)

render = web.template.render('templates')

class login:
    def GET(self):
        f = login_form()
        content = render.login_page(f)
        return render.base_clean(content)

    def POST(self):
        f = login_form()
        if not f.validates():
            content = render.login_page(f)
            return render.base_clean(content)
        user = User.get_user(username=f.username.value)
        if not user or not user.authenticate(f.password.value):
            f.note = "Wrong username or password. Please try again."
            content = render.login_page(f)
            return render.base_clean(content)
        web.config.session['user'] = user.username
        raise web.seeother(web.ctx.env.get('HTTP_REFERRER', '/'))

class register:
    def GET(self):
        f = register_form()
        content = render.register_page(f)
        return render.base_clean(content)

    def POST(self):
        f = register_form()
        if not f.validates():
            content = render.register_page(f)
            return render.base_clean(content)
        user = User(username=f.username.value,
                    email=f.email.value)
        user.password = f.password.value
        try:
            user.create(message=render.activation_email())
        except UserAccountError:
            f.note = 'You cannot register using this username or e-mail'
            content = render.register_page(f)
            return render.base_clean(content)
        raise web.seeother(web.ctx.env.get('HTTP_REFERRER', '/'))


app = web.application(urls, globals())

web.config.session = web.session.Session(app, config.sess_store, config.sess_init)

if __name__ == '__main__':
    print "Starting up..."
    app.run()
