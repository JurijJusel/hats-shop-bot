from config import LOGS_FILE_PATH, LOGS_WARNINGS_FILE_PATH


LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': (
                '%(asctime)s - %(name)s - %(levelname)s - '
                '[%(filename)s:%(lineno)d] - %(message)s'
            ),
            'datefmt': '%Y-%m-%d %H:%M',
        },
        'detailed': {
            'format': (
                '%(asctime)s - %(name)s - %(levelname)s - '
                '[%(filename)s:%(lineno)d] - %(funcName)s - %(message)s'
            ),
            'datefmt': '%Y-%m-%d %H:%M',
        },
    },
    'handlers': {
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'file_all': {
            'level': 'INFO',  # INFO vietoj DEBUG
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'detailed',
            'filename': LOGS_FILE_PATH,
            'mode': 'a',
            'encoding': 'utf-8',
            "maxBytes": 3_145_728,  # 3MB
            "backupCount": 3,
        },
        'file_warning': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'detailed',
            'filename': LOGS_WARNINGS_FILE_PATH,
            'mode': 'a',
            'encoding': 'utf-8',
            "maxBytes": 1_048_576,  # 1MB
            "backupCount": 3,
        },
    },
    'loggers': {
        '': {  # Root logger - visiems moduliams (telegram, httpx, asyncio)
            'handlers': ['console', 'file_all', 'file_warning'],
            'level': 'WARNING',  # ← TIK WARNING+ kitiems moduliams
            'propagate': True
        },
        'handlers': {  # Jūsų handler'iai
            'handlers': ['console', 'file_all', 'file_warning'],
            'level': 'INFO',  # ← INFO jūsų kodui
            'propagate': False
        },
        'admin': {  # admin/admin_*.py failai
            'handlers': ['console', 'file_all', 'file_warning'],
            'level': 'INFO',
            'propagate': False
        },
        'users': {  # users/user_*.py failai
            'handlers': ['console', 'file_all', 'file_warning'],
            'level': 'INFO',
            'propagate': False
        },
        '__main__': {  # bot.py failas (kai paleidžiate python bot.py)
            'handlers': ['console', 'file_all', 'file_warning'],
            'level': 'INFO',
            'propagate': False
        },
         # Telegram/httpx/asyncio - tik WARNING
        'telegram': {
            'level': 'WARNING',
            'propagate': True
        },
        'httpx': {  
            'level': 'WARNING',
            'propagate': True
        },
        'httpcore': {
            'level': 'WARNING',
            'propagate': True
        },
        'asyncio': {
            'level': 'WARNING',
            'propagate': True
        },
    }
}


# 1 MB - 1_048_576 Bytes
# 2 MB - 2_097_152 Bytes
# 3 MB - 3_145_728 Bytes
# 4 MB - 4_194_304 Bytes
# 5 MB - 5_242_880 Bytes
# 6 MB - 6_291_456 Bytes
# 7 MB - 7_340_032 Bytes
# 8 MB - 8_388_608 Bytes
# 9 MB - 9_437_184 Bytes
# 10 MB - 10_485_760 Bytes
