import re
import random
import hashlib
import datetime

import web

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
act_subject = authmail_conf.get('activation_subject', 'Account activation')
rst_subject = authmail_conf.get('reset_subject', 'Password reset')
del_subject = authmail_conf.get('delete_subject', 'Account removed')
ssp_subject = authmail_conf.get('suspend_subject', 'Account suspended')

# minimum password length
try:
    min_pwd_length = web.config.min_pwd_length
except:
    min_pwd_length = 4

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

def _password_hexdigest(username, salt, password):
    return hashlib.sha256('%s%s%s' % (username, salt, password)).hexdigest()

def _encrypt_password(username, cleartext):
    """ Encrypts the ``cleartext`` password and returns it """
    # TODO: maybe find a better salt generation code, or use longer salt
    salt = ''.join([random.choice('abcdefghijklmnopqrstuvwxyz0123456789') for i in range(16)])
    hexdigest = _password_hexdigest(username, salt, cleartext) 
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
        # These properties are set directly during __init__
        object.__setattr__(self, 'password', None)
        object.__setattr__(self, 'registered_at', None)
        object.__setattr__(self, 'active', False)
        object.__setattr__(self, '_act_code', None)
        object.__setattr__(self, '_del_code', None)
        object.__setattr__(self, '_pwd_code', None)
        object.__setattr__(self, '_modified', False)
        object.__setattr__(self, '_cleartext', None)
        object.__setattr__(self, '_account_id', None)
        object.__setattr__(self, '_dirty_fields', [])
        
        self.username = username
        self.email = email

        # Reset ``_dirty_fields`` so it's empty after initialization
        object.__setattr__(self, '_dirty_fields', [])
       
    @classmethod
    def _validate_username(cls, username):
        return username_re.match(username)

    @classmethod
    def _validate_email(cls, email):
        return email_re.match(email)

    def __setattr__(self, name, value):
        if name == 'username':
            if not self._validate_username(value):
                raise ValueError('Invalid username')

        if name == 'email':
            if not self._validate_email(value):
                raise ValueError('Invalid e-mail')

        if name == 'password':
            self._cleartext = value
            value = _encrypt_password(self.username, value)    

        if name in ['username', 'email', 'password', 'active', '_act_code',
                    '_del_code', '_pwd_code']:
            self._dirty_fields.append(name)

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
        """ Stores a new user optionally gerating a password 
        
        This method fails with ``UserAccountError`` if the ``User`` instance is
        marked as an existing account.

        If ``message`` argument is passed, it is treated as a e-mail message,
        and is automatically sent to user's e-mail address. The message can
        contain template variables (in ``$varname`` form). The variables can
        be one or more of the following:

        * ``$username``: username of the user to be created
        * ``$email``: user's e-mail address
        * ``$password``: user's clear text password
        * ``$usr``: activation URL

        Activation URL is generated only when a ``message`` argument is passed,
        and stored in database.

        If ``activated`` argument is set to True, the user account will be
        activated upon creation. Otherwise, it is *not* activated, which is the
        default. Note that an unactivated account can be always activated
        later.
        
        """

        if db.where(TABLE, what='username', limit=1, username=self.username):
            raise DuplicateUserError("Username '%s' already exists" % self.username)

        if db.where(TABLE, what='email', limit=1, email=self.email):
            raise DuplicateEmailError("Email '%s' already exists" % self.email)

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
            self.send_email(message=message,
                            subject=act_subject,
                            username=self.username,
                            email=self.email,
                            password=self.password,
                            url=self._act_code)
        self.store()

    def store(self):
        """ Stores a user account """
        if self._modified:
            transaction = db.transaction()
            try:
                if self._new_account:
                    db.insert(TABLE, **self._data_to_insert)
                else:
                    db.update(TABLE, where='id = $id',
                              vars={'id': self._account_id},
                              **self._data_to_store)
            except:
                transaction.rollback()
                raise
            else:
                transaction.commit()

        # nothing to store
        pass

    @property
    def _data_to_insert(self):
        """ Returns a dictionary of data to insert """
        insert_dict = {'username': self.username,
                       'email': self.email,
                       'password': self.password,
                       'active': self.active}
        if self._act_code:
            insert_dict['act_code'] = self._act_code
        return insert_dict

    @property
    def _data_to_store(self):
        """ Returns a dictionary of dirty field names and values """
        store_dict = {}
        for field in self._dirty_fields:
            store_dict[field] = self.__dict__[field]
        return store_dict

    def activate(self):
        self.active = True

    def delete(self, message=None):
        raise NotImplementedError

    def authenticate(self, password):
        """ Test ``password`` and return boolean success status """
        if not self.active:
            raise UserAccountError('Cannot authenticate inactive account')
        salt, crypt = self.password.split('$')
        return _password_hexdigest(self.username,
                                   salt,
                                   password) == crypt

    def reset_password(self, password, message=None):
        raise NotImplementedError

    def send_email(self, message, subject, sender=sender, **kwargs):
        """ Send an arbitrary e-mail message to the user 
        
        Required argument for this method are:

        * ``message``: the body of the e-mail
        * ``subject``: e-mail's subject
        
        ``sender`` argument is optional, and it defaults to
        ``web.config.authmail['sender']``, which is usually the e-mail address
        of your site.

        Optionally, you can use ``kwargs`` to set template variables. The
        template variables follow the ``$varname`` pattern used by Python's
        built-in string formatting facilities. Any occurence of ``$varname`` in
        your message string will be replaced by appropriate variables you
        specify in ``kwargs``. For example::

            >>> user.send_email(message='Hi, $username!', subject='Hi',
            ...                 username='some_user')
            # results in a message 'Hi, some_user!'

        If ``kwargs`` are omitted, the default variables are provided. Those
        are:

        * ``$sender``: the sender's e-mail address
        * ``$username``: username of the receiving user
        * ``$email``: e-mail address of the receiving user

        If for some reason, the e-mail cannot be sent (e.g, because
        ``sendmail`` is not available on your system of SMTP parameters are
        incorrect, ``send_email`` will not raise any exceptions. The best way
        to make sure ``send_email`` is working is to send yourself a message.

        For information on how to set up web.py's e-mail sending facilities,
        read the web.py API documentation on `web.utils module
        <http://webpy.org/docs/0.3/api#web.utils>`.
        
        """
        if not kwargs:
            kwargs = {'sender': sender,
                      'username': self.username,
                      'email': self.email }
        body = message.format(**kwargs)
        try:
            web.utils.sendmail(from_address=sender,
                               to_address=self.email,
                               subject=subject,
                               message=body)
        except OSError:
            pass

    @property
    def _new_account(self):
        if self._account_id:
            return False
        return True
         
    @classmethod
    def get_user(cls, username=None, email=None):
        """ Get user from the database and return ``User`` instance

        Finds a user account that matches either or both of the optional
        arguments:

        * ``username``: username of the account
        * ``email``: user's e-mail address

        If neither of the arguments are supplied, ``UserAccountError`` is
        raised. If no match is found, ``None`` is returned.

        Returned accounts always have ``_new_account`` property set to False,
        but this is meant for internal use only. Nevertheless, if you need to
        know if the account is a new (unsaved) one, you can access this
        property.

        A successful query returns a ``User`` instance.

        """

        select_dict = {}
        if username:
            if not cls._validate_username(username):
                raise ValueError("'%s' does not look like a valid username" % username)
            select_dict['username'] = username
        if email:
            if not cls._validate_email(email):
                raise ValueError("'%s' does not look like a valid e-mail" % email)
            select_dict['email'] = email

        if not select_dict:
            raise UserAccountError('No user account information to look for')
        
        records = db.where(TABLE, **select_dict)

        if len(records) == 0:
            # There is nothing to return
            return None
        
        user_account = records[0]
        try:
            user_username = user_account.username
            user_email = user_account.email
            user_dict = {
                '_account_id': user_account.id,
                'password': user_account.password,
                '_act_code': user_account.act_code,
                '_del_code': user_account.del_code,
                '_pwd_code': user_account.pwd_code,
                'registered_at': user_account.registered_at,
                'active': user_account.active,
            }
        except AttributeError:
            raise UserAccountError('Missing data for user with id %s)' % user_account.id)
        
        user = User(username=user_username,
                    email=user_email)

        for key in user_dict.keys():
            object.__setattr__(user, key, user_dict[key])

        return user
