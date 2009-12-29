import web

import config

urls = ()

app = web.application(urls, globals())

if __name__ == '__mail__':
    app.run()
