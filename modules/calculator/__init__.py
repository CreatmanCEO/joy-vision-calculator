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

# TODO: Перенести функции из calculator.py
# from .slider_l import calculate_slider_l
# from .slider_x import calculate_slider_x
# from .line import calculate_jv_line
# from .zigzag import calculate_jv_zigzag


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

    # TODO: Подключить калькуляторы
    # if system_type == 'Slider L':
    #     return calculate_slider_l(**system_data)
    # elif system_type == 'Slider X':
    #     return calculate_slider_x(**system_data)
    # elif system_type == 'JV Line':
    #     return calculate_jv_line(**system_data)
    # elif system_type == 'JV Zig-Zag':
    #     return calculate_jv_zigzag(**system_data)

    # Заглушка
    return {
        'system_info': {
            'type': system_type,
            'width_mm': system_data.get('width'),
            'height_mm': system_data.get('height'),
            'panels': system_data.get('panels')
        },
        'profiles': [],
        'hardware': [],
        'seals': [],
        'consumables': [],
        'fasteners': [],
        'summary': {
            'message': 'Калькулятор в разработке'
        }
    }
