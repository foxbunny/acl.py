import web
from nose.tools import *

database = web.database(dbn='postgres', db='authenticationpy_test', user='postgres')
web.config.authdb = database

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
                     act_code         CHAR(40),
                     del_code         CHAR(40),
                     pwd_code         CHAR(40), 
                     regiestered_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
    user.password = 'abc'
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
@raises(auth.UserAccountError)
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
