import web

# Set empty cache if not already set
if not hasattr(web.ctx, 'auth_user_cache'):
    web.ctx.auth_user_cache = {}

