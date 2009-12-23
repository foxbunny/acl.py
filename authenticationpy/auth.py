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

    
