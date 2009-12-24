import web
import re
from authenticationpy import DATABASE

db = DATABASE

TABLE = 'authenticationpy_users'

# Usernames must start with a letter, and can contain letters, numbers, dots,
# dashes, and underscores
username_re = re.compile(r'[A-Za-z]{1}[A-Za-z0-9.-_]{3,39}')

class User():
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
        self.username = None
        self.password = None
        self.email = None
        self.registered_at = None

        self.active = False
        self.act_code = None
        self.del_code = None
        self.pwd_code = None

        raise NotImplementedError

    def __setattr__(self):
        raise NotImplementedError

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

    
