# Frontend Optimization Configuration
# Add to myproject/settings.py

# ==================== STATIC FILES & CACHING ====================
# Enable compression for served files
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True

# Cache static files (set to 1 year for immutable assets)
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Browser caching headers for static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# ==================== HTTP CACHE HEADERS ====================
# Django middleware for cache control headers
MIDDLEWARE.insert(0, 'django.middleware.http.ConditionalGetMiddleware')

# Cache configuration (use Redis in production)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        # In production, use Redis:
        # 'BACKEND': 'django_redis.cache.RedisCache',
        # 'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'TIMEOUT': 3600,  # 1 hour default cache
    }
}

# ==================== SESSION CACHING ====================
# Use cache for sessions (improved performance)
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# ==================== LOGGING OPTIMIZATION ====================
# Reduce logging overhead in production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'level': 'WARNING',  # Reduce log noise
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
            'level': 'WARNING',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'WARNING',
    },
}

# ==================== TEMPLATE OPTIMIZATION ====================
# Template caching
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'myapp.admin_context_processors.admin_context',
            ],
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ],
        },
    },
]

# ==================== DATABASE CONNECTION POOLING ====================
# Add to DATABASES configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        # For PostgreSQL with connection pooling:
        # 'ENGINE': 'django.db.backends.postgresql',
        # 'NAME': 'dost_taskpro',
        # 'USER': 'postgres',
        # 'PASSWORD': 'password',
        # 'HOST': 'localhost',
        # 'PORT': '5432',
        # 'CONN_MAX_AGE': 600,  # Connection pooling timeout
        # 'OPTIONS': {
        #     'connect_timeout': 10,
        # }
    }
}
