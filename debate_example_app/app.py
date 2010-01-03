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
    '/register(/done|)', 'register',
    '/unregister', 'unregister',
    '/reset_password', 'reset_password',
    '/change_password', 'change_password',
    '/confirm/(a|d|r)/([a-f0-9]{64})', 'confirm',
    '/confirm/request_code/(a|d|r|done)', 'request_code',
)

render = web.template.render('templates')


class login:
    def GET(self):
        self.f = login_form()
        content = render.login_page(self.f)
        return render.base_clean(content)

    def POST(self):
        self.f = login_form()
        if not self.f.validates():
            content = render.login_page(self.f)
            return render.base_clean(content)
        self.user = User.get_user(username=self.f.d.username)
        if not self.user or not self.user.authenticate(self.f.d.password):
            self.f.note = "Wrong username or password. Please try again."
            content = render.login_page(self.f)
            return render.base_clean(content)
        web.config.session['user'] = self.user.username
        raise web.seeother(web.ctx.env.get('HTTP_REFERRER', '/'))


class register:
    def GET(self, done):
        if done:
            content = render.register_success()
            return render.base_clean(content)
        self.f = register_form()
        content = render.register_page(f)
        return render.base_clean(content)

    def POST(self, done):
        if done: return

        self.f = register_form()
        if not self.f.validates():
            return self.render_reg_page()
        self.user = User(username=self.f.d.username,
                         email=self.f.d.email)

        # Here's how to trap min_pwd_length errors:
        try:
            self.user.password = self.f.d.password
        except ValueError:
            self.f.note = 'Minimum password length is %s characters.' % min_pwd_length
            return self.render_reg_page()
        
        # Here's how to trap duplicate username or e-mail error:
        try:
            self.user.create(message=render.activation_email().__unicode__())
        except (DuplicateUserError, DuplicateEmailError):
            self.f.note = 'You cannot register using this username or e-mail'
            return self.render_reg_page()

        raise web.seeother('/register/done')

    def render_reg_page(self):
        content = render.register_page(self.f)
        return render.base_clean(content)


class confirm:
    def GET(self, action, code):
        self.action = action
        self.code = code
        try:
            self.user = User.get_user_by_act_code(self.code)
        except UserAccountError:
            # Activation code is not valid format
            return self.render_failed()

        if not self.user:
            # No account matches the code
            return self.render_failed()

        if self.action == 'a':
            self.activation()
        elif self.action == 'd':
            self.delete()
        elif self.action == 'r':
            self.reset()

        content = render.confirmation_success(self.action)
        return render.base_clean(content)

    def activation(self):
        deadline = 172800 # 48 hours in seconds

        if not self.user.is_interaction_timely('activation', deadline):
            # User took too long to activate
            return self.render_failed()

        # Seems like activation was successful, let's activate the user
        self.user.activate()
        self.user.store()
        # Let's also log in the user
        web.config.session['user'] = self.user.username

    def delete(self):
        User.confirm_delete(username = self.user.username)
        # Let's also log off the user
        web.config.session['user'] = None

    def reset(self):
        self.user.confirm_reset()
        # Let's log in the user
        web.config.session['user'] = self.user.username

    def render_failed(self):
        f = request_code_form()
        content = render.confirmation_failed(f, self.action)
        return render.base_clean(content)


class request_code:
    def GET(self, action):
        self.action = action
        if self.action == 'done':
            content = render.request_success()
            return render.base_clean(content)
        else:
            self.f = request_code_form()
            return self.render_failed()

    def POST(self, action):
        self.action = action

        if self.action == 'done': return

        self.f = request_code_form()
        if not self.f.validates():
            return self.render_failed()
        # Form returns e-mail address so we fetch the user using that.
        self.user = User.get_user(email=self.f.d.email)
        if not self.user:
            # There's no such user, so we ask the visitor to register.
            self.f.note = 'You don\'t have an account. Please <a href="/register">register</a> first.'
            return self.render_failed()
        self.user.store()
        raise web.seeother('/confirm/request_code/done')

    def send_activation_code(self):
        self.user.send_email(subject = web.config.authmail['activation_subject'],
                             message = render.activation_email().__unicode__(),
                             username = self.user.username,
                             email = self.user.email,
                             url = self.user.set_interaction(self.action))

    def send_delete_code(self):
        self.user.send_email(subject = web.config.authmail['delete_subject'],
                             message = render.delete_email().__unicode__(),
                             username = self.user.username,
                             email = self.user.email,
                             url = self.user.set_interaction(self.action))

    def send_reset_code(self):
        self.user.send_email(subject = web.config.authmail['reset_subject'],
                             message = render.reset_email().__unicode__(),
                             username = self.user.username,
                             email = self.user.email,
                             url = self.user.set_interaction(self.action))

    def render_failed(self):
        content = render.confirmation_failed(self.f, self.action)
        return render.base_clean(content)


class logoff:
    def GET(self):
        web.config.session['user'] = None
        raise web.seeother(web.ctx.env.get('HTTP_REFERRER', '/'))


class reset_password:
    def GET(self):
        if not web.config.session['user']:
            return self.render_reset_pw_page()
        self.user = User.get_user(web.config.session['user'])
        if not self.user:
            return self.render_reset_pw_page()
        self.user.reset_password(message=render.reset_message().__unicode__())
        content = render.reset_successful(user._cleartext)
        return render.base_clean(content)

    def render_reset_pw_page(self):
        content = render.reset_password_page()
        return render.base_clean(content)


app = web.application(urls, globals())

web.config.session = web.session.Session(app, config.sess_store, config.sess_init)

if __name__ == '__main__':
    print "Starting up..."
    app.run()
