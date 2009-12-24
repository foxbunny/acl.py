import web
import re
import random
import hashlib
import datetime

class ConfigurationError(Exception):
    pass

try:
    db = web.config.authdb
except AttributeError:
    raise ConfigurationError('Cannot find database object in web.config.authdb')

try:
    authmail_conf = web.config.authmail
except AttributeError:
    authmail_conf = {}

# TODO: loggin for emails
# TODO: cc site admin on account-related events

sender = authmail_conf.get('sender')
act_subject = authmail_conf.get('activation_subject')

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
    hexdigest = hashlib.sha256('%s%s%s' % (username, salt, cleartext)).hexdigest()
    return '%s$%s' % (salt, hexdigest)

def _generate_interaction_code(username):
    timestamp = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%s')
    hexdigest = hashlib.sha256('%s%s' % (username, timestamp)).hexdigest()
    return '%s$%s' % (timestamp, hexdigest)


class UserError(Exception):
    pass


class UserAccountError(UserError):
    pass


class DuplicateUserError(UserError):
    pass


class DuplicateEmailError(UserError):
    pass


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
        object.__setattr__(self, '_act_code', None)
        object.__setattr__(self, '_del_code', None)
        object.__setattr__(self, '_pwd_code', None)
        object.__setattr__(self, '_modified', False)
        object.__setattr__(self, '_cleartext', None)
        object.__setattr__(self, '_new_account', True)

    def __setattr__(self, name, value):
        if name == 'username':
            if not username_re.match(value):
                raise ValueError('Invalid username')

            if db.where(TABLE, what='username', limit=1, username=value):
                raise DuplicateUserError("Username '%s' already exists" % value)

        if name == 'email':
            if not email_re.match(value):
                raise ValueError('Invalid e-mail')

            if db.where(TABLE, what='email', limit=1, email=value):
                raise DuplicateEmailError("Email '%s' already exists" % value)

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

    def create(self, message=None, activated=False):
        """ Stores a new user optionally gerating a password """
        # FIXME: Clean this up in a more OOP way
        if not self._new_account:
            raise UserAccountError('Account for %s (%s) is not new' % (self.username,
                                                                       self.email))
        if not self.password:
            self._cleartext = _generate_password()
            self.password = self._cleartext

        if activated:
            self.activate()
        
        if message:
            self._act_code = _generate_interaction_code(self.username)
            msg_body = message.format(username=self.username,
                                      email=self.email,
                                      password=self.password,
                                      url=self._act_code)
            try:
                web.utils.sendmail(from_address=sender,
                                   to_address=self.email,
                                   subject=act_subject,
                                   message=msg_body)
            except OSError:
                pass

        self.store()

    def store(self):
        """ Stores a user account """
        if self._modified:
            transaction = db.transaction()
            try:
                if self._new_account:
                    insert_dict = {'username': self.username,
                                   'email': self.email,
                                   'password': self.password,
                                   'active': self.active}
                    if self._act_code:
                        insert_dict['act_code'] = self._act_code
                    db.insert(TABLE, **insert_dict)
                    self._new_account = False
                else:
                    # TODO: update only fields that have been modified
                    pass
            except:
                transaction.rollback()
                raise
            else:
                transaction.commit()

        # nothing to store
        pass

    def activate(self):
        self.active = True

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

    
