import web

render = web.template.render(web.config.auth_forms_templates)

valid_username = web.form.regexp(r'^[A-Za-z]{1}[A-Za-z0-9.-_]{3,39}$', 
                                 'This does not look like a valid username')

login_form = web.form.Form(
    web.form.Textbox('username', valid_username, description="username"),
    web.form.Password('password', description="password")
)

f = login_form()

def render_login_form():
    return render.login_form(f)
