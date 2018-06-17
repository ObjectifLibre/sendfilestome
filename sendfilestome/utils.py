from django.conf import settings


def auth_enabled():
    return (settings.SFTM_UPLOAD_AUTH_ENABLED or
            settings.SFTM_DOWNLOAD_AUTH_ENABLED)
