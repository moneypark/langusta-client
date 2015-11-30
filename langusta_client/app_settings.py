from django.conf import settings
_LANGUSTA = {
    'SOURCE_PATH': settings.LOCALE_PATHS[0],
    'LANGUAGES': ['en', 'de'],
    'HOST': 'http://localhost:8009',
    'PROJECT_SLUG': 'ln',
    'PROJECT_TOKEN': '11736a9941964637a503024b3b26a501',
    'AUTH_TOKEN': '0e1720b0ee63d8fc86b8e01b5cf35685f03a34c7',
    'TAGS': ['beta',]
}

LANGUSTA  = getattr(settings, 'LANGUSTA', _LANGUSTA)
_LANGUSTA.update(LANGUSTA)
LANGUSTA = _LANGUSTA
