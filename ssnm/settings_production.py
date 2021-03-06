# flake8: noqa
from settings_shared import *
from ccnmtlsettings.production import common

locals().update(
    common(
        project=project,
        base=base,
        INSTALLED_APPS=INSTALLED_APPS,
        STATIC_ROOT=STATIC_ROOT,
    ))

# Flash components are served off the local server
MEDIA_URL = '/flash/'
MEDIA_ROOT = "/var/www/ssnm/ssnm/flash/"

try:
    from local_settings import *
except ImportError:
    pass
