import web

# modify the parameters according to your own situation
web.config.db = web.database(dbn='postgres', db='debate_example', user='postgres')

# site configuration
sitename = 'Debate club'
web.config.admin_user = 'administrator'

# sessions configuration
sess_store = web.session.DBStore(web.config.db, 'sessions')
sess_init = {
    'user': None, # should be taken as user == Guest
}

# e-mail configuration
web.config.smtp_server = 'smtp.gmail.com'
web.config.smtp_port = 587
web.config.smtp_username = ''
web.config.smtp_password = ''
web.config.smtp_starttls = True

# authentication.py config
web.config.authdb = web.config.db
web.config.authmail = {'sender': 'your.email@server.com',
                       'activation_subject': '%s: Account activation' % sitename,
                       'reset_subject': '%s: Password reset' % sitename,
                       'delete_subject': '%s: Confirm account removal' % sitename,
                       'suspend_subject': '%s: Account suspended' % sitename}
web.config.auth_forms_templates = 'templates' # path to templates used by auth
