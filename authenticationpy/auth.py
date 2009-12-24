import web
import re
import random
import hashlib
from authenticationpy import DATABASE

db = DATABASE

TABLE = 'authenticationpy_users'

PASSWORD_CHARS = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ234567890'

# Usernames must start with a letter, and can contain letters, numbers, dots,
# dashes, and underscores
username_re = re.compile(r'[A-Za-z]{1}[A-Za-z0-9.-_]{3,39}')

# regexp for e-mail address taken from Django (http://www.djangoproject.com/)
email_re = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"' # quoted-string
    r')@(?:[A-Z0-9]+(?:-*[A-Z0-9]+)*\.)+[A-Z]{2,6}$', # domain
    re.IGNORECASE)

def _generate_password():
    """ Generates a random 8-character string using characters from PASSWORD_CHARS """
    return ''.join([random.choice(PASSWORD_CHARS) for i in range(8)])

def _encrypt_password(username, cleartext):
    """ Encrypts the ``cleartext`` password and returns it """
    # TODO: maybe find a better salt generation code, or use longer salt
    salt = ''.join([random.choice('abcdefghijklmnopqrstuvwxyz0123456789') for i in range(16)])
    sh = hashlib.sha256('%s%s%s' % (username, salt, cleartext))
    hexdigest = sh.hexdigest()
    return '%s$%s' % (salt, hexdigest)

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
        object.__setattr__(self, '_modified', False)
        object.__setattr__(self, '_cleartext', None)
        object.__setattr__(self, 'act_code', None)
        object.__setattr__(self, 'del_code', None)
        object.__setattr__(self, 'pwd_code', None)

    def __setattr__(self, name, value):
        if name == 'username':
            if not username_re.match(value):
                raise ValueError('Invalid username')

        if name == 'email':
            if not email_re.match(value):
                raise ValueError('Invalid e-mail')

        if name == 'password':
            self._cleartext = value
            value = _encrypt_password(self.username, value)    

        # no errors so far, so go ahead and assign
        object.__setattr__(self, '_modified', True)
        object.__setattr__(self, name, value)

    @property
    def is_logged_in(self):
        raise NotImplementedError

    @property
    def registered_since(self):
        raise NotImplementedError

    def create(self, message=None):
        """ Stores a new user optionally gerating a password """
        if not self.password:
            self._cleartext = _generate_password()
            self.password = self._cleartext
        self.store()

    def store(self):
        """ Stores a user account """
        if self._modified:
            # store this account
            pass
        # nothing to store
        pass


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

    
