import web
from nose.tools import *

database = web.database(dbn='postgres', db='authenticationpy_test', user='postgres')
web.config.authdb = database
web.config.authmail = {'sender': 'admin@mysite.com',
                       'activation_subject': 'MySite.com Activation E-Mail',}

from authenticationpy import auth

invalid_usernames = (
    '12hours', # starts with a number
    '$mister', # starts with a special character
    '_boogy', # another one starting with a spec char
    '-peenutz', # yet another
)

invalid_emails = (
    # FIXME: Find more representative samples of FU'd emails
    '@nouser.com',
    '@double@atmark@server.com',
)

def setup_table():
    # create table for User object
    database.query("""
                   DROP TABLE IF EXISTS authenticationpy_users CASCADE;
                   CREATE TABLE authenticationpy_users (
                     id               SERIAL PRIMARY KEY,
                     username         VARCHAR(40) NOT NULL UNIQUE,
                     email            VARCHAR(80) NOT NULL UNIQUE,
                     password         CHAR(81) NOT NULL,
                     act_code         CHAR(92),
                     del_code         CHAR(92),
                     pwd_code         CHAR(92), 
                     registered_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                     active           BOOLEAN DEFAULT 'false' 
                   );
                   CREATE UNIQUE INDEX username_index ON authenticationpy_users
                   USING btree (username);
                   CREATE UNIQUE INDEX email_index ON authenticationpy_users
                   USING btree (username);
                   """)

def teardown_table():
    database.query("""
                   DROP TABLE IF EXISTS authenticationpy_users CASCADE;
                   """)

def test_username_regexp():
    for username in invalid_usernames:
        yield username_check, username

def username_check(string):
    assert_false(auth.username_re.match(string))

def test_email_regexp():
    for e in invalid_emails:
        yield email_check, e

def email_check(string):
    assert_false(auth.username_re.match(string))

@raises(TypeError)
def test_create_user_missing_args():
    auth.User()

def test_create_user_bad_username():
    for u in invalid_usernames:
        yield create_bad_username_check, u

@raises(ValueError)
def create_bad_username_check(string):
    auth.User(username=string, email="valid@email.com")

@with_setup(setup=setup_table, teardown=teardown_table)
def test_create_user_bad_email():
    for e in invalid_emails:
        yield create_bad_email_check, e

@raises(ValueError)
def create_bad_email_check(string):
    auth.User(username='myuser', email=string)

@with_setup(setup=setup_table, teardown=teardown_table)
def test_new_user_instance_has_no_password():
    user = auth.User(username='myuser', email='valid@email.com')
    assert user.password is None

@with_setup(setup=setup_table, teardown=teardown_table)
def test_setting_password():
    user = auth.User(username='myuser', email='valid@email.com')
    user.password = 'abc123'
    assert len(user.password) == 81

@with_setup(setup=setup_table, teardown=teardown_table)
def test_save_new_instance_no_password():
    user = auth.User(username='myuser', email='valid@email.com')
    user.create()
    assert len(user.password) == 81

@with_setup(setup=setup_table, teardown=teardown_table)
def test_save_new_instance_has_cleartext():
    user = auth.User(username='myuser', email='valid@email.com')
    assert user._cleartext is None
    user.create()
    assert len(user._cleartext) == 8

@with_setup(setup=setup_table, teardown=teardown_table)
def test_create_database_record():
    user = auth.User(username='myuser', email='valid@email.com')
    user.create()
    assert len(database.select('authenticationpy_users')) == 1
    record = database.select('authenticationpy_users')[0]
    assert record.username == 'myuser'

@with_setup(setup=setup_table, teardown=teardown_table)
@raises(auth.DuplicateUserError)
def test_double_create_record():
    user = auth.User(username='myuser', email='valid@email.com')
    user.create()
    user.create()

@with_setup(setup=setup_table, teardown=teardown_table)
@raises(auth.DuplicateUserError)
def test_create_duplicate_username():
    user = auth.User(username='myuser', email='valid@email.com')
    user.create()
    user = auth.User(username='myuser', email='other@email.com')
    user.create()

@with_setup(setup=setup_table, teardown=teardown_table)
@raises(auth.DuplicateEmailError)
def test_create_duplicate_email():
    user = auth.User(username='myuser', email='valid@email.com')
    user.create()
    user = auth.User(username='otheruser', email='valid@email.com')
    user.create()

@with_setup(setup=setup_table, teardown=teardown_table)
def test_activation_withut_email():
    user = auth.User(username='myuser', email='valid@email.com')
    user.create()
    assert_false(user.active)

@with_setup(setup=setup_table, teardown=teardown_table)
def test_create_with_email_sets_act_code():
    user = auth.User(username='myuser', email='valid@email.com')
    user.create(message='This is an activation mail')
    assert len(user._act_code) == 92

@with_setup(setup=setup_table, teardown=teardown_table)
def test_activation_code_in_db():
    user = auth.User(username='myuser', email='valid@email.com')
    user.create(message='This is the activation mail')
    record = database.select('authenticationpy_users',
                             what='act_code',
                             where="username = 'myuser'",
                             limit=1)[0]
    assert record.act_code == user._act_code

@with_setup(setup=setup_table, teardown=teardown_table)
def test_activation_on_create():
    user = auth.User(username='myuser', email='valid@email.com')
    user.create(activated=True)
    record = database.select('authenticationpy_users',
                             what='active',
                             where="username = 'myuser'",
                             limit=1)[0]
    assert record.active == True

@with_setup(setup=setup_table, teardown=teardown_table)
def test_get_user_by_username():
    user = auth.User(username='myuser', email='valid@email.com')
    user.create()
    user = auth.User.get_user(username='myuser')
    assert user.email == 'valid@email.com'

@with_setup(setup=setup_table, teardown=teardown_table)
def test_get_user_by_email():
    user = auth.User(username='myuser', email='valid@email.com')
    user.create()
    user = auth.User.get_user(email='valid@email.com')
    assert user.username == 'myuser'

@with_setup(setup=setup_table, teardown=teardown_table)
def test_get_user_by_username_and_email():
    user = auth.User(username='myuser', email='valid@email.com')
    user.create()
    user = auth.User.get_user(username='myuser', email='valid@email.com')
    assert user.username == 'myuser'

@with_setup(setup=setup_table, teardown=teardown_table)
def test_get_nonexistent_username():
    user = auth.User(username='myuser', email='valid@email.com')
    user.create()
    user = auth.User.get_user(username='nouser')
    assert user is None

@with_setup(setup=setup_table, teardown=teardown_table)
def test_get_nonexistent_email():
    user = auth.User(username='myuser', email='valid@email.com')
    user.create()
    user = auth.User.get_user(email='not.me@email.com')
    assert user is None

@with_setup(setup=setup_table, teardown=teardown_table)
def test_get_user_with_combined_nonexistent():
    user = auth.User(username='myuser', email='valid@email.com')
    user.create()
    user = auth.User.get_user(username='nouser', email='valid@email.com')
    assert user is None

@with_setup(setup=setup_table, teardown=teardown_table)
def test_get_user_with_combined_nonexistent_email():
    user = auth.User(username='myuser', email='valid@email.com')
    user.create()
    user = auth.User.get_user(username='myuser', email='not.me@email.com')
    assert user is None

@with_setup(setup=setup_table, teardown=teardown_table)
def test_existing_user_has_no_new_account_flag():
    user = auth.User(username='myuser', email='valid@email.com')
    user.create()
    user = auth.User.get_user(username='myuser')
    assert user._new_account == False

@with_setup(setup=setup_table, teardown=teardown_table)
def test_authenticate():
    password = 'abc123'
    user = auth.User(username='myuser', email='valid@email.com')
    user.password = password
    user.create(activated=True)
    assert user.authenticate(password)

@with_setup(setup=setup_table, teardown=teardown_table)
def test_authenticate_wrong_password():
    password = 'abc123'
    user = auth.User(username='myuser', email='valid@email.com')
    user.create(activated=True)
    assert_false(user.authenticate(password))

@with_setup(setup=setup_table, teardown=teardown_table)
@raises(auth.UserAccountError)
def test_authenticate_inactive_account():
    user = auth.User(username='myuser', email='valid@email.com')
    user.password = 'abc123'
    user.create()
    user.authenticate('abc123')

@with_setup(setup=setup_table, teardown=teardown_table)
def test_user_has_dirty_fields_property():
    user = auth.User(username='myuser', email='valid@email.com')
    assert user._dirty_fields == []

@with_setup(setup=setup_table, teardown=teardown_table)
def test_dirty_fields_empty_after_get_user():
    user = auth.User(username='myuser', email='valid@email.com')
    user.create()
    user = auth.User.get_user(username='myuser')
    assert user._dirty_fields == []

@with_setup(setup=setup_table, teardown=teardown_table)
def test_dirty_fields_list_on_modification():
    user = auth.User(username='myuser', email='valid@email.com')
    user.create()
    user = auth.User.get_user(username='myuser')
    user.email = 'another@email.com'
    assert user._dirty_fields == ['email']

@with_setup(setup=setup_table, teardown=teardown_table)
def test_data_to_store():
    user = auth.User(username='myuser', email='valid@email.com')
    user.create()
    user = auth.User.get_user(username='myuser')
    user.username = 'otheruser'
    user.email = 'another@email.com'
    assert user._data_to_store == {'username': 'otheruser', 
                                   'email': 'another@email.com'}

@with_setup(setup=setup_table, teardown=teardown_table)
def test_store_modifications():
    user = auth.User(username='myuser', email='valid@email.com')
    user.create()
    user = auth.User.get_user(username='myuser')
    user.username = 'otheruser'
    user.store()
    user = auth.User.get_user(email='valid@email.com')
    assert user.username == 'otheruser'

@with_setup(setup=setup_table, teardown=teardown_table)
def test_change_password():
    user = auth.User(username='myuser', email='valid@email.com')
    user.password = 'abc123'
    user.create(activated=True)
    user = auth.User.get_user(username='myuser')
    user.authenticate('abc123')
    user.password = '123abc'
    user.store()
    user = auth.User.get_user(username='myuser')
    assert user.authenticate('123abc')

@with_setup(setup=setup_table, teardown=teardown_table)
@raises(ValueError)
def test_change_password_with_short_password():
    auth.min_pwd_length = 2
    user = auth.User(username='myuser', email='valid@email.com')
    user.password = 'a'

@with_setup(setup=setup_table, teardown=teardown_table)
@raises(ValueError)
def test_change_password_with_blank_password():
    auth.min_pwd_length = 0
    user = auth.User(username='myuser', email='valid@email.com')
    user.password = ''

@with_setup(setup=setup_table, teardown=teardown_table)
def test_reset_password():
    user = auth.User(username='myuser', email='valid@email.com')
    user.password = 'abc123'
    user.create(activated=True)
    user = auth.User.get_user(username='myuser')
    user.reset_password('123abc')
    user = auth.User.get_user(username='myuser')
    assert user.authenticate('123abc')
