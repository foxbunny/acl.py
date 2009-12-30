import web

import config

urls = (
    '/', 'debates',
    '/new', 'new_debate',
    '/(?P<title>[\w_]+)/', 'debate',
    '/(?P<title>[\w_]+)/delete', 'delete_debate',
    '/(?P<title>[\w_]+)/arguments/(?P<username>.*)/', 'argument',
    '/(?P<title>[\w_]+)/arguments/(?P<username>.*)/delete', 'delete_argument'
)

app = web.application(urls, globals())

if __name__ == '__mail__':
    app.run()
