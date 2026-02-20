# modules/calculator/__init__.py
"""
Модуль расчёта комплектующих

Содержит функции расчёта для всех типов систем:
- Slider L (параллельно-сдвижная)
- Slider X (усиленная параллельно-сдвижная)
- JV Line (с парковкой)
- JV Zig-Zag (гармошка)

Код адаптирован из C:/Hans/calculator.py
"""

from .core import (
    calculate_slider_l,
    calculate_slider_x,
    calculate_jv_line,
    calculate_jv_zigzag
)


def calculate_system(system_data: dict) -> dict:
    """
    Рассчитать комплектующие для системы

    Args:
        system_data: dict с параметрами системы
            - system_type: str ("Slider L", "Slider X", "JV Line", "JV Zig-Zag")
            - width: int (мм)
            - height: int (мм)
            - panels: float
            - opening: str
            - left_edge: str
            - right_edge: str
            - ... остальные параметры

    Returns:
        dict с результатом расчёта:
            - system_info: dict
            - profiles: list
            - hardware: list
            - seals: list
            - consumables: list
            - fasteners: list
            - summary: dict
    """
    system_type = system_data.get('system_type')

    calculators = {
        'Slider L': calculate_slider_l,
        'Slider X': calculate_slider_x,
        'JV Line': calculate_jv_line,
        'JV Zig-Zag': calculate_jv_zigzag
    }

    calculator = calculators.get(system_type)
    if not calculator:
        raise ValueError(f'Неизвестный тип системы: {system_type}')

    # Исключаем system_type из параметров, т.к. функции калькулятора его не принимают
    calc_params = {k: v for k, v in system_data.items() if k != 'system_type'}
    return calculator(**calc_params)
