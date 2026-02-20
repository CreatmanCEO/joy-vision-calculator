# modules/pdf/fonts.py
"""
Управление шрифтами для PDF генерации
"""

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# Глобальные переменные для кэширования
_fonts_registered = False
_default_font = None
_bold_font = None


def register_fonts():
    """
    Регистрация шрифтов с поддержкой кириллицы
    Вызывается один раз при первой генерации PDF
    """
    global _fonts_registered, _default_font, _bold_font

    if _fonts_registered:
        return _default_font, _bold_font

    # Пути к шрифтам
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    fonts_dir = os.path.join(base_dir, 'static', 'fonts')

    regular_font_path = os.path.join(fonts_dir, 'DejaVuSans.ttf')
    bold_font_path = os.path.join(fonts_dir, 'DejaVuSans-Bold.ttf')

    try:
        # Проверяем наличие шрифтов
        if os.path.exists(regular_font_path):
            pdfmetrics.registerFont(TTFont('DejaVuSans', regular_font_path))
            _default_font = 'DejaVuSans'
        else:
            _default_font = 'Helvetica'

        if os.path.exists(bold_font_path):
            pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', bold_font_path))
            _bold_font = 'DejaVuSans-Bold'
        else:
            _bold_font = 'Helvetica-Bold'

        _fonts_registered = True

    except Exception as e:
        _default_font = 'Helvetica'
        _bold_font = 'Helvetica-Bold'
        _fonts_registered = True

    return _default_font, _bold_font


def get_font_name():
    """Получить имя основного шрифта"""
    if not _fonts_registered:
        register_fonts()
    return _default_font


def get_bold_font_name():
    """Получить имя жирного шрифта"""
    if not _fonts_registered:
        register_fonts()
    return _bold_font
