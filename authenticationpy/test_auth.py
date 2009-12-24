import web
import authenticationpy
from authenticationpy import auth
from nose.tools import *

database = web.database(dbn='postgres', db='authenticationpy_test', user='postgres')

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

def setup_module():
    web.config.db = database
    # create table for User object
    database.query("""
                   DROP TABLE IF EXISTS authenticationpy_users CASCADE;
                   CREATE TABLE authenticationpy_users (
                     id               SERIAL PRIMARY KEY,
                     username         VARCHAR(40) NOT NULL UNIQUE,
                     email            VARCHAR(80) NOT NULL UNIQUE,
                     password         VARCHAR(40) NOT NULL,
                     act_code         VARCHAR(40),
                     del_code         VARCHAR(40),
                     pwd_code         VARCHAR(40), 
                     regiestered_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                     active           BOOLEAN DEFAULT 'false' 
                   );
                   CREATE UNIQUE INDEX username_index ON authenticationpy_users
                   USING btree (username);
                   CREATE UNIQUE INDEX email_index ON authenticationpy_users
                   USING btree (username);
                   """)

def teardown_module():
    database.query("""
                   DROP TABLE IF EXISTS authenticationpy_users CASCADE;
                   """)

def test_username_regexp():
    for username in invalid_usernames:
        yield username_check, username

def username_check(string):
    assert_false(auth.username_re.match(string))

def test_email_regexp():
    for email in invalid_emails:
        yield email_check, email

def email_check(string):
    assert_false(auth.username_re.match(string))

@raises(TypeError)
def test_create_user_missing_args():
    user = auth.User()

def test_create_user_bad_username():
    for u in invalid_usernames:
        yield create_bad_username_check, u

@raises(ValueError)
def create_bad_username_check(string):
    print string
    user = auth.User(username=string, email="valid@email.com")

