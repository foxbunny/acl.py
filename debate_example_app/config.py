import web

# modify the parameters according to your own situation
db = web.database(dbn='postgres', db='debate_example', user='postgres')

# site configuration
sitename = 'Debate club'
web.config.admin_user = 'administrator'

# authentication.py config
web.config.authdb = db
web.config.authmail = {'sender': 'your.email@server.com',
                       'activation_subject': '%s: Account activation' % sitename,
                       'reset_subject': '%s: Password reset' % sitename,
                       'delete_subject': '%s: Confirm account removal' % sitename,
                       'suspend_subject': '%s: Account suspended' % sitename}
