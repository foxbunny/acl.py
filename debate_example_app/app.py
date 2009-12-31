import web

import config
from debate import *
from auth_forms import login_form, register_form

urls = (
    '/', 'debates',
    '/new', 'new_debate',
    '/(?P<title>[\w_]+)/', 'debate',
    '/(?P<title>[\w_]+)/delete', 'delete_debate',
    '/(?P<title>[\w_]+)/arguments/(?P<username>.*)/', 'argument',
    '/(?P<title>[\w_]+)/arguments/(?P<username>.*)/delete', 'delete_argument'
    '/login', 'login',
    '/logoff', 'logoff',
    '/register', 'register',
    '/unregister', 'unregister',
)

render = web.template.render('templates')

class login:
    def GET(self):
        f = login_form()
        content = render.login_page(f)
        return render.base_clean(content)
app = web.application(urls, globals())

web.config.session = web.session.Session(app, config.sess_store, config.sess_init)

if __name__ == '__main__':
    print "Starting up..."
    app.run()
