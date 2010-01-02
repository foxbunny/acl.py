import web

import config
from debate import *
from authenticationpy.auth import *
from auth_forms import login_form, register_form, request_code_form

urls = (
    '/', 'debates',
    '/new', 'new_debate',
    '/([\w_]+)/', 'debate',
    '/([\w_]+)/delete', 'delete_debate',
    '/([\w_]+)/arguments/(.*)/', 'argument',
    '/([\w_]+)/arguments/(.*)/delete', 'delete_argument',
    '/login', 'login',
    '/logoff', 'logoff',
    '/register', 'register',
    '/unregister', 'unregister',
    '/reset_password', 'reset_password',
    '/confirm/(a|d|r)/([a-f0-9]{64})', 'confirm',
    '/confirm/request_code', 'request_code',
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
        original_path = web.ctx.env.get('HTTP_REFERRER', '/')

        f = register_form()
        if not f.validates():
            content = render.register_page(f)
            return render.base_clean(content)
        user = User(username=f.username.value,
                    email=f.email.value)
        user.password = f.password.value
        try:
            user.create(message=render.activation_email().__unicode__())
        except UserAccountError:
            f.note = 'You cannot register using this username or e-mail'
            content = render.register_page(f)
            return render.base_clean(content)
        raise web.seeother(web.ctx.env.get('HTTP_REFERRER', '/'))

class activate:
    def GET(self, code):
        try:
            user = User.get_user_by_act_code(code)
        except UserAccountError:
            # Activation code is not valid format
            return self.render_failed()

        if not user:
            # No account matches the code
            return self.render_failed()

        deadline = 172800 # 48 hours in seconds

        if not user.is_interaction_timely('activation', deadline):
            # User took too long to activate
            return self.render_failed()

        # Seems like activation was successful, let's activate the user
        user.activate()
        user.store()

        content = render.activation_success()
        return render.base_clean(content)

    def render_failed(self):
        f = request_code_form()
        content = render.activation_failed(f)
        return render.base_clean(content)

class request_code:
    def GET(self):
        i = web.input(status='none')
        if i.status == 'done':
            content = render.request_success()
            return render.base_clean(content)
        else:
            f = request_code_form()
            content = render.activation_failed(f)
            return render.base_clean(content)

    def POST(self):
        f = request_code_form()
        if not f.validates():
            content = render.activation_failed(f)
            return render.base_clean(content)
        # Form returns e-mail address so we fetch the user using that.
        user = User.get_user(email=f.email.value)
        if not user:
            # There's no such user, so we ask the visitor to register.
            f.note = 'You don\'t have an account. Please <a href="/register">register</a> first.'
            content = render.activation_failed(f)
            return render.base_clean(content)
        # Assign new activation code
        code = user.set_activation()
        user.store()
        # Send out the new activation e-mail
        user.send_email(subject = web.config.authmail['activation_subject'],
                        message = render.activation_email().__unicode__(),
                        username = user.username,
                        email = user.email,
                        url = code)
        raise web.seeother('/activate/request_code?status=done')
        content = render.request_success()
        return render.base_clean(content)

app = web.application(urls, globals())

web.config.session = web.session.Session(app, config.sess_store, config.sess_init)

if __name__ == '__main__':
    print "Starting up..."
    app.run()
