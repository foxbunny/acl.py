import web

def user_cache_hook():
    # Set empty cache if not already set
    web.ctx.auth_user_cache = {}

