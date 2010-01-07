import web
from web import form

if not hasattr(web.config, 'authform'):
    web.config.authform = {}

username_msg = web.config.authform.get('username error', 
                                       'Invalid username')
password_msg = web.config.authform.get('password error',
                                       'Invalid password')

username_va = form.regexp('[A-Za-z]{1}[A-Za-z0-9.-_]{3,39}', username_msg)

login_form = form.Form(
    form.Textbox('username', username_va),
    form.Password('password'),
)
