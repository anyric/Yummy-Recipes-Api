"""module for app configurations"""
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    """Parent configuration class."""
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET = 'this string represents scret key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL','postgresql://postgres:1234@localhost/yummy_api')

class DevelopmentConfig(Config):
    """Configurations for Development."""
    DEBUG = False

class TestingConfig(Config):
    """Configurations for test database."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL','postgresql://postgres:1234@localhost/test_db')
    DEBUG = False

class StagingConfig(Config):
    """Configurations for Staging."""
    DEBUG = False

class ProductionConfig(Config):
    """Configurations for Production."""
    DEBUG = False
    TESTING = False

app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
}
