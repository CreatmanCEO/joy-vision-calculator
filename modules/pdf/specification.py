# modules/pdf/specification.py
"""
Генерация PDF разблюдовки (спецификации комплектующих)
Формат как в оригинальной разблюдовке заказчика
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from .fonts import register_fonts


def generate_specification_pdf(order, output_path):
    """Генерация разблюдовки в формате оригинала"""

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        topMargin=12*mm,
        bottomMargin=12*mm,
        leftMargin=10*mm,
        rightMargin=10*mm
    )

    elements = []
    styles = getSampleStyleSheet()
    font_name, font_bold = register_fonts()

    # Цветовая схема (как в оригинале)
    color_profiles = colors.HexColor('#cce5ff')      # Голубой для профилей
    color_hardware = colors.HexColor('#ccffcc')      # Зеленый для фурнитуры
    color_seals = colors.HexColor('#ffffcc')         # Желтый для уплотнителей
    color_header = colors.HexColor('#e0e0e0')        # Серый для заголовков

    # ========== ЗАГОЛОВОК ==========
    title_style = ParagraphStyle(
        'Title',
        fontSize=16,
        fontName=font_bold,
        alignment=TA_CENTER,
        spaceAfter=8
    )
    elements.append(Paragraph(f"ЗАКАЗ № {str(order.id).zfill(3)}", title_style))
    elements.append(Spacer(1, 5*mm))

    # ========== ИНФОРМАЦИЯ О ЗАКАЗЕ ==========
    info_style = ParagraphStyle('Info', fontSize=9, fontName=font_name, leading=12)

    elements.append(Paragraph(f"Цвет RAL: {order.ral_color or 'RAL 9016'}", info_style))
    elements.append(Paragraph(f"Дата запуска: {datetime.now().strftime('%d.%m.%Y')}", info_style))
    elements.append(Paragraph(f"Город: {order.city or '—'}", info_style))
    elements.append(Paragraph(f"Заказчик: {order.customer_name}", info_style))
    elements.append(Spacer(1, 8*mm))

    # ========== ДОПОЛНИТЕЛЬНЫЕ РАБОТЫ (справа в оригинале) ==========
    services_data = [['ДОПОЛНИТЕЛЬНЫЕ РАБОТЫ:']]
    services_data.append([f"• Остекление: {'Нет' if not order.with_glass else 'Да'}"])
    services_data.append([f"• Монтаж: {'Нет' if not order.with_install else 'Да'}"])
    services_data.append([f"• Доставка: Нет"])
    services_data.append([f"• Продеть щетку: Нет"])
    services_data.append([f"• Фрезеровка: Нет"])
    services_data.append([f"• Подготовка к монтажу: Нет"])

    services_table = Table(services_data, colWidths=[190*mm])
    services_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, 0), font_bold),
        ('FONTNAME', (0, 1), (0, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BACKGROUND', (0, 0), (-1, -1), color_header),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(services_table)
    elements.append(Spacer(1, 8*mm))

    # ========== ТАБЛИЦА КОМПЛЕКТУЮЩИХ ==========
    # Заголовок таблицы
    main_table_data = [['Наименование', 'Ед', 'СП', 'Итого']]

    # Обрабатываем каждую систему
    for system in order.systems:
        calc_data = system.calculated_data or {}

        # Категории с цветовым кодированием (как в оригинале)
        categories_with_colors = [
            ('profiles', color_profiles),
            ('seals', color_seals),
            ('interpanel_seals', color_seals),
            ('hardware', color_hardware),
            ('consumables', color_profiles),
            ('fasteners', color_profiles),
        ]

        for cat_key, cat_color in categories_with_colors:
            items = calc_data.get(cat_key, [])
            if not items:
                continue

            for item in items:
                name = item.get('name', '—')

                # Определяем единицу и количество
                if cat_key in ['profiles', 'seals', 'interpanel_seals']:
                    qty = item.get('total_m', 0)
                    unit = 'п.м'
                else:
                    qty = item.get('qty', item.get('pieces', 0))
                    unit = item.get('unit', 'шт')

                # Примечание
                note = item.get('note', '')
                if note:
                    name = f"{name} - {note}"

                # Добавляем строку с цветом категории
                main_table_data.append([
                    name,
                    unit,
                    f"{qty:.3f}" if isinstance(qty, float) else str(qty),
                    f"{qty:.3f}" if isinstance(qty, float) else str(qty)
                ])

    # Создаем основную таблицу
    main_table = Table(main_table_data, colWidths=[130*mm, 20*mm, 20*mm, 20*mm])

    # Стили для таблицы
    table_styles = [
        # Заголовок
        ('BACKGROUND', (0, 0), (-1, 0), color_header),
        ('FONTNAME', (0, 0), (-1, 0), font_bold),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (-1, 0), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),

        # Общие стили
        ('FONTNAME', (0, 1), (-1, -1), font_name),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 1), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
    ]

    # Применяем цвета к строкам (нужно определить диапазоны по категориям)
    # Это упрощенная версия - в оригинале цвета зависят от типа комплектующих
    row_idx = 1
    for system in order.systems:
        calc_data = system.calculated_data or {}

        categories_with_colors = [
            ('profiles', color_profiles),
            ('seals', color_seals),
            ('interpanel_seals', color_seals),
            ('hardware', color_hardware),
            ('consumables', color_profiles),
            ('fasteners', color_profiles),
        ]

        for cat_key, cat_color in categories_with_colors:
            items = calc_data.get(cat_key, [])
            if not items:
                continue

            for item in items:
                table_styles.append(('BACKGROUND', (0, row_idx), (-1, row_idx), cat_color))
                row_idx += 1

    main_table.setStyle(TableStyle(table_styles))
    elements.append(main_table)
    elements.append(Spacer(1, 10*mm))

    # ========== ПАРАМЕТРЫ СИСТЕМ (внизу) ==========
    elements.append(Paragraph('Параметры систем: Slider', ParagraphStyle(
        'SectionHeader',
        fontSize=11,
        fontName=font_bold,
        spaceAfter=5
    )))

    for system in order.systems:
        sys_info = system.calculated_data.get('system_info', {}) if system.calculated_data else {}

        params_text = f"""
<b>С1: {system.system_type} {int(system.panels)}-дор.</b><br/>
ШхВ: {system.width}x{system.height}<br/>
Ств.:{int(system.panels)}<br/>
Размер стекла:<br/>
ширина: {sys_info.get('glass_width_mm', 0):.0f}<br/>
высота: {sys_info.get('glass_height_mm', 0):.0f}<br/>
<br/>
Створки:<br/>
крайняя слева: 1011<br/>
средняя слева: 1001
"""

        # Обернуть в Paragraph для поддержки HTML разметки
        params_style = ParagraphStyle(
            'ParamsBox',
            fontSize=8,
            fontName=font_name,
            leading=10
        )
        params_paragraph = Paragraph(params_text, params_style)

        params_box = Table([[params_paragraph]], colWidths=[190*mm])
        params_box.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(params_box)
        elements.append(Spacer(1, 5*mm))

    # Генерируем PDF
    doc.build(elements)
    return output_path
