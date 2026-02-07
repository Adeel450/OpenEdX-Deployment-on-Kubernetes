# -*- coding: utf-8 -*-
import os
from cms.envs.production import *

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

######## Common CMS settings
STUDIO_NAME = "Adeel OpenEdX - Studio"

CACHES["staticfiles"] = {
    "KEY_PREFIX": "staticfiles_cms",
    "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    "LOCATION": "staticfiles_cms",
}

# Authentication
SOCIAL_AUTH_EDX_OAUTH2_SECRET = "uDdWEmndDC9zhhhPsWtpl92M"
SOCIAL_AUTH_EDX_OAUTH2_URL_ROOT = "http://lms:8000"
SOCIAL_AUTH_REDIRECT_IS_HTTPS = False  # scheme is correctly included in redirect_uri
SESSION_COOKIE_NAME = "studio_session_id"

MAX_ASSET_UPLOAD_FILE_SIZE_IN_MB = 100

FRONTEND_LOGIN_URL = LMS_ROOT_URL + '/login'
FRONTEND_REGISTER_URL = LMS_ROOT_URL + '/register'

# Enable "reindex" button
FEATURES["ENABLE_COURSEWARE_INDEX"] = True

# Create folders if necessary
for folder in [LOG_DIR, MEDIA_ROOT, STATIC_ROOT, ORA2_FILEUPLOAD_ROOT]:
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)



######## End of common CMS settings

ALLOWED_HOSTS = [
    ENV_TOKENS.get("CMS_BASE"),
    "cms",
]
CORS_ORIGIN_WHITELIST.append("https://cms.biolnks.io")

# Authentication
SOCIAL_AUTH_EDX_OAUTH2_KEY = "cms-sso"
SOCIAL_AUTH_EDX_OAUTH2_PUBLIC_URL_ROOT = "https://lms.biolnks.io"

# MFE-specific settings

COURSE_AUTHORING_MICROFRONTEND_URL = "https://apps.lms.biolnks.io/authoring"


LOGIN_REDIRECT_WHITELIST.append("apps.lms.biolnks.io")
CORS_ORIGIN_WHITELIST.append("https://apps.lms.biolnks.io")
CSRF_TRUSTED_ORIGINS.append("https://apps.lms.biolnks.io")