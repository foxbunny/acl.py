import web
from web import form

from authenticationpy import auth

if not hasattr(web.config, 'authform'):
    web.config.authform = {}

# The following validation error messages are simple and English. It is
# recommended that you change them by assigning a authform dictionary. For
# example, if you want to set ``username error`` and ``password error``, you
# will use those keys in ``web.config.authform``::
#
#     web.config.authform = {'username error': 'Watch the username format!',
#                            'password error': 'This password is too short.'}
#
username_msg = web.config.authform.get('username error', 
                                       'Invalid username')
password_msg = web.config.authform.get('password error',
                                       'Password cannot be empty')
email_msg = web.config.authform.get('email error',
                                    'Invalid e-mail address')
pw_confirm_msg = web.config.authform.get('password confirmation error',
                                         'You must correctly retype your password')
email_request_msg = web.config.authform.get('email request error',
                                            'This e-mail corresponds to no user')


username_va = form.regexp('[A-Za-z]{1}[A-Za-z0-9.-_]{3,39}', username_msg)
password_va = form.regexp('^.{%s}.*' % auth.min_pwd_length, password_msg)
email_va = form.regexp(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Za-z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Za-z]+)*"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"' # quoted-string
    r')@(?:[A-Za-z0-9]+(?:-*[A-Za-z0-9]+)*\.)+[A-Za-z]{2,6}$', # domain
    email_msg
)
confirmation_va = form.Validator(pw_confirm_msg,
                                 lambda i: i.password == i.confirm)
new_confirmation_va = form.Validator(pw_confirm_msg,
                                     lambda i: i.new == i.confirm)
email_belongs_va = form.Validator(email_request_msg,
                                  lambda i: auth.User.get_user(email=i.email) is not None)

username_field = form.Textbox('username', username_va)
password_field = form.Password('password', password_va)
new_pw_field = form.Password('new', password_va,
                             descrption='new password')
pw_confirmation_field = form.Password('confirm', password_va,
                                      description='confirm password')
email_field = form.Textbox('email', email_va, description='e-mail')

login_form = form.Form(
    username_field,
    password_field,
)

register_form = form.Form(
    username_field,
    email_field,
    password_field,
    pw_confirmation_field,
    validators = [
        confirmation_va, 
    ]
)

pw_reset_form = form.Form(
    password_field,
    new_pw_field,
    pw_confirmation_field,
    validators = [
        new_confirmation_va,
    ]   
)

email_request_form = form.Form(
    email_field,
    validators = [
        email_belongs_va,
    ]
)
