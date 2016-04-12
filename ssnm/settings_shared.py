# Django settings for ssnm project.
import os.path
from ccnmtlsettings.shared import common

project = 'ssnm'
base = os.path.dirname(__file__)
locals().update(common(project=project, base=base))

PROJECT_APPS = [
    'ssnm.main'
]

USE_TZ = True

TEMPLATE_CONTEXT_PROCESSORS += [  # noqa
    'ssnm.main.views.context_processor',
]

INSTALLED_APPS += [  # noqa
    'django_extensions',
    'bootstrapform',
    'registration',
    'typogrify',
    'ssnm.main',
]

REGISTRATION_APPLICATION_MODEL = 'registration.Application'

MIGRATION_MODULES = {
    'registration': 'ssnm.migrations.registration',
}

ACCOUNT_ACTIVATION_DAYS = 1

INTERNAL_IPS = ('127.0.0.1', )

# Flash components are served off the local server
MEDIA_URL = '/flash/'
MEDIA_ROOT = 'flash'
