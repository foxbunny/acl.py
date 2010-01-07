import web
from web import form

from authenticationpy import auth

if not hasattr(web.config, 'authform'):
    web.config.authform = {}

username_msg = web.config.authform.get('username error', 
                                       'Invalid username')
password_msg = web.config.authform.get('password error',
                                       'Password cannot be empty')

username_va = form.regexp('[A-Za-z]{1}[A-Za-z0-9.-_]{3,39}', username_msg)
password_va = form.regexp('^.{%s}.*' % auth.min_pwd_length, password_msg)

login_form = form.Form(
    form.Textbox('username', username_va),
    form.Password('password', password_va),
)
