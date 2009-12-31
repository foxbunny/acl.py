import re

import web


valid_username = web.form.regexp(r'^[A-Za-z]{1}[A-Za-z0-9.-_]{3,39}$', 
                                 'This does not look like a valid username')

valid_email = web.form.regexp(r"(^[-!#$%&'*+/=?^_`{}|~0-9a-z]+(\.[-!#$%&'*+/=?^_`{}|~0-9a-z]+)*"  # dot-atom
                              r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"' # quoted-string
                              r')@(?:[a-z0-9]+(?:-*[a-z0-9]+)*\.)+[a-z]{2,6}$', # domain
                              'Please enter a valid e-mail')

valid_password = web.form.regexp(r'.+', 'Please enter your password')

login_form = web.form.Form(
    web.form.Textbox('username', valid_username, description='username'),
    web.form.Password('password', valid_password, description='password'),
)

register_form = web.form.Form(
    web.form.Textbox('username', valid_username, description='username'),
    web.form.Textbox('email', valid_email, description='email'),
    web.form.Password('password', valid_password, description='password'),
    web.form.Password('confirm', description='password confirmation'),
    validators = [
        web.form.Validator('You must correctly retype your password',
                           lambda i: i.password == i.confirm),
    ]
)
