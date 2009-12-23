import web
import authenticationpy

database = web.database(dbn='postgres', db='authenticationpy_test', user='postgres')

def setup_package():
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

def teardown_package():
    database.query("""
                   DROP TABLE IF EXISTS authenticationpy_users CASCADE;
                   """)
