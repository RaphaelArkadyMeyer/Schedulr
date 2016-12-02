
import logging

# Flask specific options
class FlaskConfig(object):
    WTF_CSRF_ENABLED = True
    SECRET_KEY = 'XJE4RuEKdDknx7lEGHgnW1xW0IDTsa9IW68otLNC9Dtdn86jcp48rCRqZuzHmraMywMaxcPv9LSkQqWNZtyNIjhSkoBqH8FkEAtGC0CdrSGd5ow1E5qmZOl4DeXdqzVA'
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True

# Our options
LOGGING_MODE = logging.BASIC_FORMAT
DO_SAMPLE_QUERY = False
