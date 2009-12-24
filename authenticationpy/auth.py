import web
import re
from authenticationpy import DATABASE

db = DATABASE

TABLE = 'authenticationpy_users'

# Usernames must start with a letter, and can contain letters, numbers, dots,
# dashes, and underscores
username_re = re.compile(r'[A-Za-z]{1}[A-Za-z0-9.-_]{3,39}')

# regexp for e-mail address taken from Django (http://www.djangoproject.com/)
email_re = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"' # quoted-string
    r')@(?:[A-Z0-9]+(?:-*[A-Z0-9]+)*\.)+[A-Z]{2,6}$', # domain
    re.IGNORECASE)


class User(object):
    """ User and user management class

    To create a new unsaved user, you have to initialize a User instance
    passing it two required arguments:

    * ``username``: valid username
    * ``email``: a valid e-mail address

    If either of the parameters are missing, ``TypeError`` is raised, and if
    either or both of the arguments are invalid, ``ValueError`` is raised.

    A valid username must start with a letter and can contain only letters,
    numbers, dots, dashes, or underscores. A valid e-mail address must be a
    canonical e-mail addres.

    """

    def __init__(self, username, email):
        self.username = username
        self.email = email

        # These properties are set directly during __init__
        object.__setattr__(self, 'password', None)
        object.__setattr__(self, 'registered_at', None)
        object.__setattr__(self, 'active', False)
        object.__setattr__(self, 'act_code', None)
        object.__setattr__(self, 'del_code', None)
        object.__setattr__(self, 'pwd_code', None)

    @property
    def is_logged_in(self):
        raise NotImplementedError

    @property
    def registered_since(self):
        raise NotImplementedError

    def create(self, message=None):
        raise NotImplementedError

    def store(self):
        raise NotImplementedError

    def delete(self, message=None):
        raise NotImplementedError

    def authenticate(self, password):
        raise NotImplementedError

    def reset_password(self, password, message=None):
        raise NotImplementedError

    def send_email(self, message=None):
        raise NotImplementedError
    
    @classmethod
    def get_user(cls, username=None, email=None):
        raise NotImplementedError

    
