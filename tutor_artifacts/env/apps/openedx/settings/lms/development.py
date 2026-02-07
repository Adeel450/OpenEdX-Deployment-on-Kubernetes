# -*- coding: utf-8 -*-
import os
from lms.envs.devstack import *

####### Settings common to LMS and CMS
import json
import os

from xmodule.modulestore.modulestore_settings import update_module_store_settings

# Mongodb connection parameters: simply modify `mongodb_parameters` to affect all connections to MongoDb.
mongodb_parameters = {
    "db": "openedx",
    "host": "10.0.5.90",
    "port": 27017,
    "user": "admin",
    "password": "password123",
    # Connection/Authentication
    "connect": False,
    "ssl": False,
    "authsource": "admin",
    "replicaSet": None,
    
}
DOC_STORE_CONFIG = mongodb_parameters
CONTENTSTORE = {
    "ENGINE": "xmodule.contentstore.mongo.MongoContentStore",
    "ADDITIONAL_OPTIONS": {},
    "DOC_STORE_CONFIG": DOC_STORE_CONFIG
}
# Load module store settings from config files
update_module_store_settings(MODULESTORE, doc_store_settings=DOC_STORE_CONFIG)
DATA_DIR = "/openedx/data/modulestore"

for store in MODULESTORE["default"]["OPTIONS"]["stores"]:
   store["OPTIONS"]["fs_root"] = DATA_DIR

# Behave like memcache when it comes to connection errors
DJANGO_REDIS_IGNORE_EXCEPTIONS = True

# Meilisearch connection parameters
MEILISEARCH_ENABLED = True
MEILISEARCH_URL = "http://meilisearch:7700"
MEILISEARCH_PUBLIC_URL = "https://10.0.5.90"
MEILISEARCH_INDEX_PREFIX = "tutor_"
MEILISEARCH_API_KEY = "889ab193cdfeef4d81f80e6b239557aa7af5d366c2d5a9862973a220ce32087e"
MEILISEARCH_MASTER_KEY = "password123"
SEARCH_ENGINE = "search.meilisearch.MeilisearchEngine"

# Common cache config
CACHES = {
    "default": {
        "KEY_PREFIX": "default",
        "VERSION": "1",
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://@redis:6379/1",
    },
    "general": {
        "KEY_PREFIX": "general",
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://@redis:6379/1",
    },
    "mongo_metadata_inheritance": {
        "KEY_PREFIX": "mongo_metadata_inheritance",
        "TIMEOUT": 300,
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://@redis:6379/1",
    },
    "configuration": {
        "KEY_PREFIX": "configuration",
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://@redis:6379/1",
    },
    "celery": {
        "KEY_PREFIX": "celery",
        "TIMEOUT": 7200,
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://@redis:6379/1",
    },
    "course_structure_cache": {
        "KEY_PREFIX": "course_structure",
        "TIMEOUT": 604800, # 1 week
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://@redis:6379/1",
    },
    "ora2-storage": {
        "KEY_PREFIX": "ora2-storage",
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://@redis:6379/1",
    }
}

# The default Django contrib site is the one associated to the LMS domain name. 1 is
# usually "example.com", so it's the next available integer.
SITE_ID = 2

# Contact addresses
CONTACT_MAILING_ADDRESS = "Adeel OpenEdX - https://lms.biolnks.io"
DEFAULT_FROM_EMAIL = ENV_TOKENS.get("DEFAULT_FROM_EMAIL", ENV_TOKENS["CONTACT_EMAIL"])
DEFAULT_FEEDBACK_EMAIL = ENV_TOKENS.get("DEFAULT_FEEDBACK_EMAIL", ENV_TOKENS["CONTACT_EMAIL"])
SERVER_EMAIL = ENV_TOKENS.get("SERVER_EMAIL", ENV_TOKENS["CONTACT_EMAIL"])
TECH_SUPPORT_EMAIL = ENV_TOKENS.get("TECH_SUPPORT_EMAIL", ENV_TOKENS["CONTACT_EMAIL"])
CONTACT_EMAIL = ENV_TOKENS.get("CONTACT_EMAIL", ENV_TOKENS["CONTACT_EMAIL"])
BUGS_EMAIL = ENV_TOKENS.get("BUGS_EMAIL", ENV_TOKENS["CONTACT_EMAIL"])
UNIVERSITY_EMAIL = ENV_TOKENS.get("UNIVERSITY_EMAIL", ENV_TOKENS["CONTACT_EMAIL"])
PRESS_EMAIL = ENV_TOKENS.get("PRESS_EMAIL", ENV_TOKENS["CONTACT_EMAIL"])
PAYMENT_SUPPORT_EMAIL = ENV_TOKENS.get("PAYMENT_SUPPORT_EMAIL", ENV_TOKENS["CONTACT_EMAIL"])
BULK_EMAIL_DEFAULT_FROM_EMAIL = ENV_TOKENS.get("BULK_EMAIL_DEFAULT_FROM_EMAIL", ENV_TOKENS["CONTACT_EMAIL"])
API_ACCESS_MANAGER_EMAIL = ENV_TOKENS.get("API_ACCESS_MANAGER_EMAIL", ENV_TOKENS["CONTACT_EMAIL"])
API_ACCESS_FROM_EMAIL = ENV_TOKENS.get("API_ACCESS_FROM_EMAIL", ENV_TOKENS["CONTACT_EMAIL"])

# Get rid completely of coursewarehistoryextended, as we do not use the CSMH database
INSTALLED_APPS.remove("lms.djangoapps.coursewarehistoryextended")
DATABASE_ROUTERS.remove(
    "openedx.core.lib.django_courseware_routers.StudentModuleHistoryExtendedRouter"
)

# Set uploaded media file path
MEDIA_ROOT = "/openedx/media/"

# Video settings
VIDEO_IMAGE_SETTINGS["STORAGE_KWARGS"]["location"] = MEDIA_ROOT
VIDEO_TRANSCRIPTS_SETTINGS["STORAGE_KWARGS"]["location"] = MEDIA_ROOT

GRADES_DOWNLOAD = {
    "STORAGE_TYPE": "",
    "STORAGE_KWARGS": {
        "base_url": "/media/grades/",
        "location": "/openedx/media/grades",
    },
}

# ORA2
ORA2_FILEUPLOAD_BACKEND = "filesystem"
ORA2_FILEUPLOAD_ROOT = "/openedx/data/ora2"
FILE_UPLOAD_STORAGE_BUCKET_NAME = "openedxuploads"
ORA2_FILEUPLOAD_CACHE_NAME = "ora2-storage"

# Change syslog-based loggers which don't work inside docker containers
LOGGING["handlers"]["local"] = {
    "class": "logging.handlers.WatchedFileHandler",
    "filename": os.path.join(LOG_DIR, "all.log"),
    "formatter": "standard",
}
LOGGING["handlers"]["tracking"] = {
    "level": "DEBUG",
    "class": "logging.handlers.WatchedFileHandler",
    "filename": os.path.join(LOG_DIR, "tracking.log"),
    "formatter": "standard",
}
LOGGING["loggers"]["tracking"]["handlers"] = ["console", "local", "tracking"]

# Silence some loggers (note: we must attempt to get rid of these when upgrading from one release to the next)
LOGGING["loggers"]["blockstore.apps.bundles.storage"] = {"handlers": ["console"], "level": "WARNING"}

# These warnings are visible in simple commands and init tasks
import warnings

# REMOVE-AFTER-V20: check if we can remove these lines after upgrade.
try:
    from django.utils.deprecation import RemovedInDjango50Warning, RemovedInDjango51Warning
    # RemovedInDjango5xWarning: 'xxx' is deprecated. Use 'yyy' in 'zzz' instead.
    warnings.filterwarnings("ignore", category=RemovedInDjango50Warning)
    warnings.filterwarnings("ignore", category=RemovedInDjango51Warning)
    # DeprecationWarning: 'imghdr' is deprecated and slated for removal in Python 3.13
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="pgpy.constants")
except ImportError:
    pass # If the warnings don't exist we don't need to filter them.
    
# Email
EMAIL_USE_SSL = False
# Forward all emails from edX's Automated Communication Engine (ACE) to django.
ACE_ENABLED_CHANNELS = ["django_email"]
ACE_CHANNEL_DEFAULT_EMAIL = "django_email"
ACE_CHANNEL_TRANSACTIONAL_EMAIL = "django_email"
EMAIL_FILE_PATH = "/tmp/openedx/emails"

# Language/locales
LANGUAGE_COOKIE_NAME = "openedx-language-preference"

# Allow the platform to include itself in an iframe
X_FRAME_OPTIONS = "SAMEORIGIN"


JWT_AUTH["JWT_ISSUER"] = "https://lms.biolnks.io/oauth2"
JWT_AUTH["JWT_AUDIENCE"] = "openedx"
JWT_AUTH["JWT_SECRET_KEY"] = "vFfopWzSgDwH1wbJAL66wS7m"
JWT_AUTH["JWT_PRIVATE_SIGNING_JWK"] = json.dumps(
    {
        "kid": "openedx",
        "kty": "RSA",
        "e": "AQAB",
        "d": "wP__LnKm3C3g00bL4ihK2r96O2Tm69qPNnSD1uH1EGih9U_M19PdV4QaK2gSOaV4GIF6-LEbKTvZz-5C_x4JDshvxdQjYiCR21dO-t8tok5qbDyjPkqcMnZxJ_fzN6KywSIHLXGS_GtR0kKzS6KxJ9PDSw83YhhlexvlH5RSIZu1g_83ZUulaSr4jG3Vq6joAlGbnZP_pbKyk3kM3KpCAN28x9h0jVqonEh45N47_jOC1Ris3zfbo1sYgABsfsd9-zra2uMFfTyDJEytZV6TQdPCSc_sGJkNCk04bJMMmSaczTAD6Qh8TeabvjxrLapjRsgmw_MDYXuEzUi9CbeB",
        "n": "xFN_VjzdDLZ-epAPa8c28R8xe_hWcgTlnrNuf46K9zejd6LZKgFl5Owbe_ClxWRkyAcHRFQrQG419ZsIEFJtXAsDnfBP5dKEON-d_tO-DmUYIz_OpQ5uW0jfZnqDaQe2epKY5gg5Zrt6pmWTC4f0mRxmLvNLYqXr5xVnp05wRyPWAv_UB0fQaEQ1vX2vNpGNPuKqY98MvHa8zazp2rOM1JVKa3Q0uUPxfB2QDatOVB-K2B6B_cJXigMQ-9xuLbpRk2xptF70Bze79ZQgIQ7vtU_fwdXd7sUJqqt0FrLgpofzN8vJpbQUiXCN2TpDnjIdjdY0vqtu1GHmFO9qOoB6OQ",
        "p": "2m7SkbEF0RE2tmBuSC5VY2mts2-YlUa53NGDFQTkv2yaL1pUKRCM7lFr-_-Fv6ALgKBY61MFxZ1eCEdSUZvy6u8uUE2Z911wccQ6yP6xqOh8UpWb3hV6vunmzjXz6nbOYLDYrxoTLTUTVNU_VQTHNOiBSN7k9erniDPM_hLb5HE",
        "q": "5hdbpUkxAFEjfPB9Nhq4Wv8F4lZqzQQeLVqXZJm-EOE-Kq834TWfvbFdZ3Tg7yQ1GGy6OMamIHstReKN6zzN2y_iYIU1r0-pcyzLHR-arZR4UxLkrYwhdCYhoLtRTHlwdROHdwNFoSMlBoRO24dcbkypQRpVG6uaAK8m9X2ktkk",
        "dq": "0hqaMP_4otV0lm3zqCgWF-GvudI3jCYqeDe07sQE7tz_K3L8j8WrrEf9hq8Phs-FPFxsX9PldtuDp8EM3rWTNIcxK_n337HahbVtc5acY8yjYxhpgJ_pHGqFYoQp5K8vpXjDxkVSm6W_9Ydzirq8CGwwUaZ9-NplsiI-bQTiFyE",
        "dp": "MxgtRUslUyw1oh-YbGX6L1DvAsQd6v0qSM7xXJ9SaryarGzyttBaRvzgx4eT36kuR546boFzHjCbaFBWnyRdhDsCmGIum8BNpy8BmTaKlDodqqu4VBCuL65DAQV50uSLje6QIRV2WuLJbNSdBeQiPOwOId-RqzyRgDitwNjkeuE",
        "qi": "UwstrlTYJhHa_pBilEpj1JJZ4e33GsX5HMHFRPA4Lw-9JAK5TVUQEDZ9AFZbzu9QYG6rY5_uH8uO0xhEaIr6W0Xw6G8eEsN0w10p_wLn0baeFO50FRbUQSoiTyK-DFp9WPq6pmZWS7XFtqqd36DpMLBWu0U-0Y4f1NCfrJTReNU",
    }
)
JWT_AUTH["JWT_PUBLIC_SIGNING_JWK_SET"] = json.dumps(
    {
        "keys": [
            {
                "kid": "openedx",
                "kty": "RSA",
                "e": "AQAB",
                "n": "xFN_VjzdDLZ-epAPa8c28R8xe_hWcgTlnrNuf46K9zejd6LZKgFl5Owbe_ClxWRkyAcHRFQrQG419ZsIEFJtXAsDnfBP5dKEON-d_tO-DmUYIz_OpQ5uW0jfZnqDaQe2epKY5gg5Zrt6pmWTC4f0mRxmLvNLYqXr5xVnp05wRyPWAv_UB0fQaEQ1vX2vNpGNPuKqY98MvHa8zazp2rOM1JVKa3Q0uUPxfB2QDatOVB-K2B6B_cJXigMQ-9xuLbpRk2xptF70Bze79ZQgIQ7vtU_fwdXd7sUJqqt0FrLgpofzN8vJpbQUiXCN2TpDnjIdjdY0vqtu1GHmFO9qOoB6OQ",
            }
        ]
    }
)
JWT_AUTH["JWT_ISSUERS"] = [
    {
        "ISSUER": "https://lms.biolnks.io/oauth2",
        "AUDIENCE": "openedx",
        "SECRET_KEY": "vFfopWzSgDwH1wbJAL66wS7m"
    }
]

# Enable/Disable some features globally
FEATURES["ENABLE_DISCUSSION_SERVICE"] = False
FEATURES["PREVENT_CONCURRENT_LOGINS"] = False
FEATURES["ENABLE_CORS_HEADERS"] = True

# CORS
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOW_INSECURE = False
# Note: CORS_ALLOW_HEADERS is intentionally not defined here, because it should
# be consistent across deployments, and is therefore set in edx-platform.

# Add your MFE and third-party app domains here
CORS_ORIGIN_WHITELIST = []

# Disable codejail support
# explicitely configuring python is necessary to prevent unsafe calls
import codejail.jail_code
codejail.jail_code.configure("python", "nonexistingpythonbinary", user=None)
# another configuration entry is required to override prod/dev settings
CODE_JAIL = {
    "python_bin": "nonexistingpythonbinary",
    "user": None,
}

OPENEDX_LEARNING = {
    'MEDIA': {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {
            "location": "/openedx/media-private/openedx-learning",
        }
    }
}

# edx-event-bus-redis settings
EVENT_BUS_PRODUCER = 'edx_event_bus_redis.create_producer'
EVENT_BUS_REDIS_CONNECTION_URL = 'redis://@redis:6379/'
EVENT_BUS_TOPIC_PREFIX = 'dev'
EVENT_BUS_CONSUMER = 'edx_event_bus_redis.RedisEventConsumer'


######## End of settings common to LMS and CMS

######## Common LMS settings
LOGIN_REDIRECT_WHITELIST = ["cms.biolnks.io"]

# Better layout of honor code/tos links during registration
REGISTRATION_EXTRA_FIELDS["terms_of_service"] = "hidden"
REGISTRATION_EXTRA_FIELDS["honor_code"] = "hidden"

# Fix media files paths
PROFILE_IMAGE_BACKEND["options"]["location"] = os.path.join(
    MEDIA_ROOT, "profile-images/"
)

COURSE_CATALOG_VISIBILITY_PERMISSION = "see_in_catalog"
COURSE_ABOUT_VISIBILITY_PERMISSION = "see_about_page"

# Allow insecure oauth2 for local interaction with local containers
OAUTH_ENFORCE_SECURE = False

# Email settings
DEFAULT_EMAIL_LOGO_URL = LMS_ROOT_URL + "/theming/asset/images/logo.png"
BULK_EMAIL_SEND_USING_EDX_ACE = True
FEATURES["ENABLE_FOOTER_MOBILE_APP_LINKS"] = False

# Branding
MOBILE_STORE_ACE_URLS = {}
SOCIAL_MEDIA_FOOTER_ACE_URLS = {}

# Make it possible to hide courses by default from the studio
SEARCH_SKIP_SHOW_IN_CATALOG_FILTERING = False

# Caching
CACHES["staticfiles"] = {
    "KEY_PREFIX": "staticfiles_lms",
    "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    "LOCATION": "staticfiles_lms",
}

# Enable search features
FEATURES["ENABLE_COURSE_DISCOVERY"] = True
FEATURES["ENABLE_COURSEWARE_SEARCH"] = True
FEATURES["ENABLE_DASHBOARD_SEARCH"] = True

# Create folders if necessary
for folder in [DATA_DIR, LOG_DIR, MEDIA_ROOT, STATIC_ROOT, ORA2_FILEUPLOAD_ROOT]:
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

# MFE: enable API and set a low cache timeout for the settings. otherwise, weird
# configuration bugs occur. Also, the view is not costly at all, and it's also cached on
# the frontend. (5 minutes, hardcoded)
ENABLE_MFE_CONFIG_API = True
MFE_CONFIG_API_CACHE_TIMEOUT = 1

# MFE-specific settings

FEATURES['ENABLE_AUTHN_MICROFRONTEND'] = True


FEATURES['ENABLE_NEW_BULK_EMAIL_EXPERIENCE'] = True


LEARNER_HOME_MFE_REDIRECT_PERCENTAGE = 100


######## End of common LMS settings

# Setup correct webpack configuration file for development
WEBPACK_CONFIG_PATH = "webpack.dev.config.js"

LMS_BASE = "lms.biolnks.io:8000"
LMS_ROOT_URL = "http://{}".format(LMS_BASE)
LMS_INTERNAL_ROOT_URL = LMS_ROOT_URL
SITE_NAME = LMS_BASE
CMS_BASE = "cms.biolnks.io:8001"
CMS_ROOT_URL = "http://{}".format(CMS_BASE)
LOGIN_REDIRECT_WHITELIST.append(CMS_BASE)

MEILISEARCH_PUBLIC_URL = "https://10.0.5.90:7700"

# Session cookie
SESSION_COOKIE_DOMAIN = "lms.biolnks.io"
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SAMESITE = "Lax"

# CMS authentication
IDA_LOGOUT_URI_LIST.append("http://cms.biolnks.io:8001/logout/")

FEATURES["ENABLE_COURSEWARE_MICROFRONTEND"] = False

# Disable enterprise integration
FEATURES["ENABLE_ENTERPRISE_INTEGRATION"] = False
SYSTEM_WIDE_ROLE_CLASSES.remove("enterprise.SystemWideEnterpriseUserRoleAssignment")

LOGGING["loggers"]["oauth2_provider"] = {
    "handlers": ["console"],
    "level": "DEBUG"
}


# Dynamic config API settings
# https://openedx.github.io/frontend-platform/module-Config.html
MFE_CONFIG = {
    "BASE_URL": "apps.lms.biolnks.io",
    "CSRF_TOKEN_API_PATH": "/csrf/api/v1/token",
    "CREDENTIALS_BASE_URL": "",
    "DISCOVERY_API_BASE_URL": "",
    "FAVICON_URL": "http://lms.biolnks.io/favicon.ico",
    "INFO_EMAIL": "adeel.octaloop@gmail.com",
    "LANGUAGE_PREFERENCE_COOKIE_NAME": "openedx-language-preference",
    "LMS_BASE_URL": "http://lms.biolnks.io:8000",
    "LOGIN_URL": "http://lms.biolnks.io:8000/login",
    "LOGO_URL": "http://lms.biolnks.io:8000/theming/asset/images/logo.png",
    "LOGO_WHITE_URL": "http://lms.biolnks.io:8000/theming/asset/images/logo.png",
    "LOGO_TRADEMARK_URL": "http://lms.biolnks.io:8000/theming/asset/images/logo.png",
    "LOGOUT_URL": "http://lms.biolnks.io:8000/logout",
    "MARKETING_SITE_BASE_URL": "http://lms.biolnks.io:8000",
    "PASSWORD_RESET_SUPPORT_LINK": "mailto:adeel.octaloop@gmail.com",
    "REFRESH_ACCESS_TOKEN_ENDPOINT": "http://lms.biolnks.io:8000/login_refresh",
    "SITE_NAME": "Adeel OpenEdX",
    "STUDIO_BASE_URL": "http://cms.biolnks.io:8001",
    "USER_INFO_COOKIE_NAME": "user-info",
    "ACCESS_TOKEN_COOKIE_NAME": "edx-jwt-cookie-header-payload",
}

# MFE-specific settings

AUTHN_MICROFRONTEND_URL = "http://apps.lms.biolnks.io:1999/authn"
AUTHN_MICROFRONTEND_DOMAIN  = "apps.lms.biolnks.io/authn"
MFE_CONFIG["DISABLE_ENTERPRISE_LOGIN"] = True



ACCOUNT_MICROFRONTEND_URL = "http://apps.lms.biolnks.io:1997/account/"
MFE_CONFIG["ACCOUNT_SETTINGS_URL"] = ACCOUNT_MICROFRONTEND_URL



MFE_CONFIG["COURSE_AUTHORING_MICROFRONTEND_URL"] = "http://apps.lms.biolnks.io:2001/authoring"
MFE_CONFIG["ENABLE_ASSETS_PAGE"] = "true"
MFE_CONFIG["ENABLE_HOME_PAGE_COURSE_API_V2"] = "true"
MFE_CONFIG["ENABLE_PROGRESS_GRAPH_SETTINGS"] = "true"
MFE_CONFIG["ENABLE_TAGGING_TAXONOMY_PAGES"] = "true"
MFE_CONFIG["ENABLE_UNIT_PAGE"] = "true"
MFE_CONFIG["MEILISEARCH_ENABLED"] = "true"



DISCUSSIONS_MICROFRONTEND_URL = "http://apps.lms.biolnks.io:2002/discussions"
MFE_CONFIG["DISCUSSIONS_MFE_BASE_URL"] = DISCUSSIONS_MICROFRONTEND_URL
DISCUSSIONS_MFE_FEEDBACK_URL = None



WRITABLE_GRADEBOOK_URL = "http://apps.lms.biolnks.io:1994/gradebook"



LEARNER_HOME_MICROFRONTEND_URL = "http://apps.lms.biolnks.io:1996/learner-dashboard/"



LEARNING_MICROFRONTEND_URL = "http://apps.lms.biolnks.io:2000/learning"
MFE_CONFIG["LEARNING_BASE_URL"] = "http://apps.lms.biolnks.io:2000/learning"



ORA_GRADING_MICROFRONTEND_URL = "http://apps.lms.biolnks.io:1993/ora-grading"



PROFILE_MICROFRONTEND_URL = "http://apps.lms.biolnks.io:1995/profile/u/"
MFE_CONFIG["ACCOUNT_PROFILE_URL"] = "http://apps.lms.biolnks.io:1995/profile"



COMMUNICATIONS_MICROFRONTEND_URL = "http://apps.lms.biolnks.io:1984/communications"
MFE_CONFIG["SCHEDULE_EMAIL_SECTION"] = True



ADMIN_CONSOLE_MICROFRONTEND_URL = "http://apps.lms.biolnks.io:2025/admin-console"
MFE_CONFIG["ADMIN_CONSOLE_URL"] = ADMIN_CONSOLE_MICROFRONTEND_URL


# Cors configuration

# admin-console MFE
CORS_ORIGIN_WHITELIST.append("http://apps.lms.biolnks.io:2025")
LOGIN_REDIRECT_WHITELIST.append("apps.lms.biolnks.io:2025")
CSRF_TRUSTED_ORIGINS.append("http://apps.lms.biolnks.io:2025")

# authn MFE
CORS_ORIGIN_WHITELIST.append("http://apps.lms.biolnks.io:1999")
LOGIN_REDIRECT_WHITELIST.append("apps.lms.biolnks.io:1999")
CSRF_TRUSTED_ORIGINS.append("http://apps.lms.biolnks.io:1999")

# authoring MFE
CORS_ORIGIN_WHITELIST.append("http://apps.lms.biolnks.io:2001")
LOGIN_REDIRECT_WHITELIST.append("apps.lms.biolnks.io:2001")
CSRF_TRUSTED_ORIGINS.append("http://apps.lms.biolnks.io:2001")

# account MFE
CORS_ORIGIN_WHITELIST.append("http://apps.lms.biolnks.io:1997")
LOGIN_REDIRECT_WHITELIST.append("apps.lms.biolnks.io:1997")
CSRF_TRUSTED_ORIGINS.append("http://apps.lms.biolnks.io:1997")

# communications MFE
CORS_ORIGIN_WHITELIST.append("http://apps.lms.biolnks.io:1984")
LOGIN_REDIRECT_WHITELIST.append("apps.lms.biolnks.io:1984")
CSRF_TRUSTED_ORIGINS.append("http://apps.lms.biolnks.io:1984")

# discussions MFE
CORS_ORIGIN_WHITELIST.append("http://apps.lms.biolnks.io:2002")
LOGIN_REDIRECT_WHITELIST.append("apps.lms.biolnks.io:2002")
CSRF_TRUSTED_ORIGINS.append("http://apps.lms.biolnks.io:2002")

# gradebook MFE
CORS_ORIGIN_WHITELIST.append("http://apps.lms.biolnks.io:1994")
LOGIN_REDIRECT_WHITELIST.append("apps.lms.biolnks.io:1994")
CSRF_TRUSTED_ORIGINS.append("http://apps.lms.biolnks.io:1994")

# learner-dashboard MFE
CORS_ORIGIN_WHITELIST.append("http://apps.lms.biolnks.io:1996")
LOGIN_REDIRECT_WHITELIST.append("apps.lms.biolnks.io:1996")
CSRF_TRUSTED_ORIGINS.append("http://apps.lms.biolnks.io:1996")

# learning MFE
CORS_ORIGIN_WHITELIST.append("http://apps.lms.biolnks.io:2000")
LOGIN_REDIRECT_WHITELIST.append("apps.lms.biolnks.io:2000")
CSRF_TRUSTED_ORIGINS.append("http://apps.lms.biolnks.io:2000")

# ora-grading MFE
CORS_ORIGIN_WHITELIST.append("http://apps.lms.biolnks.io:1993")
LOGIN_REDIRECT_WHITELIST.append("apps.lms.biolnks.io:1993")
CSRF_TRUSTED_ORIGINS.append("http://apps.lms.biolnks.io:1993")

# profile MFE
CORS_ORIGIN_WHITELIST.append("http://apps.lms.biolnks.io:1995")
LOGIN_REDIRECT_WHITELIST.append("apps.lms.biolnks.io:1995")
CSRF_TRUSTED_ORIGINS.append("http://apps.lms.biolnks.io:1995")





javascript_files = ['base_application', 'application', 'certificates_wv']
dark_theme_filepath = ['indigo/js/dark-theme.js']

for filename in javascript_files:
    if filename in PIPELINE['JAVASCRIPT']:
        PIPELINE['JAVASCRIPT'][filename]['source_filenames'] += dark_theme_filepath

MFE_CONFIG['INDIGO_ENABLE_DARK_TOGGLE'] = True
MFE_CONFIG['INDIGO_FOOTER_NAV_LINKS'] = [{'title': 'About Us', 'url': '/about'}, {'title': 'Blog', 'url': '/blog'}, {'title': 'Donate', 'url': '/donate'}, {'title': 'Terms of Service', 'url': '/tos'}, {'title': 'Privacy Policy', 'url': '/privacy'}, {'title': 'Help', 'url': '/help'}, {'title': 'Contact Us', 'url': '/contact'}]