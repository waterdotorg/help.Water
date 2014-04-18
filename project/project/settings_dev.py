from settings_default import *
from settings_dev_private import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# Debug Toolbar Settings #
DEBUG_TOOLBAR_PATCH_SETTINGS = False

INSTALLED_APPS += (
    'debug_toolbar',
)

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)
