import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-(8q@2)+3(76hqq1tg^8xpeeu_gzkv2(@qn%is2@ed)fs2^89vo'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'normal': {
            'format': '[%(asctime)s][%(levelname)s] %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': None,
            'class': 'logging.StreamHandler',
            'formatter': 'normal',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.environ.get("DJANGO_LOG_LEVEL", "INFO"),
        },
    },
}
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]
# STATIC_ROOT = os.path.join(BASE_DIR, 'all_static')
ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    'simpleui',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'supply',
    'inventory',
    'purchase',
    'supply.templatetags',
    'account',
    'excel',
    'spider'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'supply.middleware.middleware.AuthMW',
    'supply.middlewares.IPmiddleware',
]

ROOT_URLCONF = 'newMM.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': []
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'newMM.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mmnew1',
        'USER': 'root',
        'PASSWORD': '201221',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'
USE_TZ = False
USE_I18N = True

USE_L10N = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# session 设置
SESSION_COOKIE_AGE = 60 * 60 * 2  # 设置过期时间2小时，默认为两周
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # 设置关闭浏览器时失效

# 配置django-excel
FILE_UPLOAD_HANDLERS = (
    "django_excel.ExcelMemoryFileUploadHandler",
    "django_excel.TemporaryExcelFileUploadHandler",
)

#缓存
CACHES = {
    'default':{
        'BACKEND':'django.core.cache.backends.db.DatabaseCache',
        #数据库缓存 引擎
        'LOCATION':'my_cache_table', #数据库缓存表 名称
        'TIMEOUT':300, #最大缓存事件 300s
        'OPTIONS':{
            'MAX_ENTRIES':300, #最大缓存数量 300
            'CULL_FREQUENCY':2, #到达最大缓存时 删除1/2 的数据
        }
    }
}

SIMPLEUI_HOME_INFO = False
SIMPLEUI_LOGO = "/static/images/logo_w.png"

SIMPLEUI_CONFIG = {
    # 是否使用系统默认菜单，自定义菜单时建议关闭。
    'system_keep': False,

    # 用于菜单排序和过滤, 不填此字段为默认排序和全部显示。空列表[] 为全部不显示.
    'menu_display': ['基本信息设置'],

    # 设置是否开启动态菜单, 默认为False. 如果开启, 则会在每次用户登陆时刷新展示菜单内容。
    # 一般建议关闭。
    'dynamic': False,
    'menus': [

        {
            'name': '基本信息设置',
            'icon': 'fa fa-th-list',
            'models': [
                {
                    'name': '公司',
                    # 注意url按'/admin/应用名小写/模型名小写/'命名。
                    'url': '/admin/supply/gongsi/',
                    'icon': 'fa fa-building'
                },
                {
                    'name': '物料',
                    # 注意url按'/admin/应用名小写/模型名小写/'命名。
                    'url': '/admin/supply/wuliao/',
                    'icon': 'fa fa-truck'
                },
                {
                    'name': '保密问题',
                    # 注意url按'/admin/应用名小写/模型名小写/'命名。
                    'url': '/admin/supply/securityquestion/',
                    'icon': 'fa fa-question'
                },
                {
                    'name': '消息',
                    # 注意url按'/admin/应用名小写/模型名小写/'命名。
                    'url': '/admin/supply/xiaoxi/',
                    'icon': 'fa fa-comments'
                },
                {
                    'name': '员工',
                    # 注意url按'/admin/应用名小写/模型名小写/'命名。
                    'url': '/admin/supply/yuangong/',
                    'icon': 'fa fa-users'
                },
                {
                    'name': '工厂',
                    # 注意url按'/admin/应用名小写/模型名小写/'命名。
                    'url': '/admin/supply/gongchang/',
                    'icon': 'fa fa-industry'
                },
                {
                    'name': '供应商',
                    # 注意url按'/admin/应用名小写/模型名小写/'命名。
                    'url': '/admin/supply/gongyingshang/',
                    'icon': 'fa fa-briefcase'
                },
                {
                    'name': '供应关系',
                    # 注意url按'/admin/应用名小写/模型名小写/'命名。
                    'url': '/admin/supply/gongyingguanxi/',
                    'icon': 'fa fa-podcast'
                },
                {
                    'name': '工厂库存',
                    # 注意url按'/admin/应用名小写/模型名小写/'命名。
                    'url': '/admin/supply/gongchangkucun/',
                    'icon': 'fa fa-tint'
                },
                {
                    'name': '采购需求',
                    # 注意url按'/admin/应用名小写/模型名小写/'命名。
                    'url': '/admin/supply/caigouxuqiu/',
                    'icon': 'fa fa-laptop'
                },
                {
                    'name': '询价单',
                    # 注意url按'/admin/应用名小写/模型名小写/'命名。
                    'url': '/admin/supply/xunjiadan/',
                    'icon': 'fa fa-window-restore'
                },
                {
                    'name': '报价单',
                    # 注意url按'/admin/应用名小写/模型名小写/'命名。
                    'url': '/admin/supply/baojiadan/',
                    'icon': 'fa fa-archive'
                },
                {
                    'name': '询价单',
                    # 注意url按'/admin/应用名小写/模型名小写/'命名。
                    'url': '/admin/supply/xunjiadan/',
                    'icon': 'fa fa-balance-scale'
                },
                {
                    'name': '采购单',
                    # 注意url按'/admin/应用名小写/模型名小写/'命名。
                    'url': '/admin/supply/caigoudan/',
                    'icon': 'fa fa-address-card'
                },
                {
                    'name': '暂售单',
                    # 注意url按'/admin/应用名小写/模型名小写/'命名。
                    'url': '/admin/supply/zanshoudan/',
                    'icon': 'fa fa-bookmark'
                },
                {
                    'name': '入库单',
                    # 注意url按'/admin/应用名小写/模型名小写/'命名。
                    'url': '/admin/supply/rukudan/',
                    'icon': 'fa fa-american-sign-language-interpreting'
                },
                {
                    'name': '发票',
                    # 注意url按'/admin/应用名小写/模型名小写/'命名。
                    'url': '/admin/supply/fapiao/',
                    'icon': 'fa fa-university'
                },
            ]
        },
    ]
}
