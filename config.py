# config.py
"""
Конфигурация приложения Joy Vision Calculator
"""

import os
from pathlib import Path

# Базовая директория приложения
BASE_DIR = Path(__file__).parent

# Директория для данных
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)

# Директория для экспорта PDF
EXPORTS_DIR = DATA_DIR / 'exports'
EXPORTS_DIR.mkdir(exist_ok=True)


class Config:
    """Базовая конфигурация"""

    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f'sqlite:///{DATA_DIR / "joyvision.db"}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Битрикс24
    BITRIX_WEBHOOK_URL = os.environ.get(
        'BITRIX_WEBHOOK_URL',
        'https://joyvision.bitrix24.ru/rest/1/op5tzx11ardvgibz/'
    )
    BITRIX_FOLDER_ID = int(os.environ.get('BITRIX_FOLDER_ID', '3313'))

    # PDF
    PDF_EXPORTS_DIR = str(EXPORTS_DIR)
    PDF_FONT_PATH = str(BASE_DIR / 'static' / 'fonts' / 'DejaVuSans.ttf')

    # JSON
    JSON_AS_ASCII = False


class DevelopmentConfig(Config):
    """Конфигурация для разработки"""
    DEBUG = True


class ProductionConfig(Config):
    """Конфигурация для продакшена"""
    DEBUG = False

    # В продакшене использовать PostgreSQL
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class TestingConfig(Config):
    """Конфигурация для тестов"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Выбор конфигурации по окружению
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Получить конфигурацию по переменной окружения FLASK_ENV"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
