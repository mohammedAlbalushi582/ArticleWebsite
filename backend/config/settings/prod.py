from .base import *  # noqa: F401, F403

DEBUG = False

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"

# Behind the nginx TLS-terminating reverse proxy: trust the forwarded scheme so
# Django treats proxied requests as HTTPS (fixes admin CSRF referer checks).
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Django 4.0+ requires the POST Origin to be trusted for CSRF (e.g. admin login).
CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS",
    default=[
        "https://thearticleanalyzer.com",
        "https://www.thearticleanalyzer.com",
    ],
)
