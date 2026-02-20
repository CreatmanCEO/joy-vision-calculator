# modules/pdf/specification.py
"""
Генерация PDF разблюдовки (спецификации комплектующих)
Адаптировано из C:/Hans/Разблюдовка_KP/reader_0.2.py
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
    """
    Генерация PDF разблюдовки (спецификации комплектующих) для заказа

    Args:
        order: объект Order с системами
        output_path: путь для сохранения PDF

    Returns:
        путь к сгенерированному файлу
    """

    # Создаем PDF документ
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        topMargin=15*mm,
        bottomMargin=15*mm,
        leftMargin=12*mm,
        rightMargin=12*mm
    )

    elements = []
    styles = getSampleStyleSheet()

    # Регистрация шрифтов с поддержкой кириллицы
    font_name, font_bold = register_fonts()

    # Заголовок
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName=font_bold
    )

    title = Paragraph(f"СПЕЦИФИКАЦИЯ №{order.id}", title_style)
    elements.append(title)
    elements.append(Spacer(1, 5*mm))

    # Информация о заказе
    info_style = ParagraphStyle(
        'Info',
        parent=styles['Normal'],
        fontSize=10,
        fontName=font_name,
        leading=14
    )

    info_data = [
        ['Заказчик:', order.customer_name],
        ['Город:', order.city or '—'],
        ['Цвет RAL:', order.ral_color or '—'],
        ['Дата:', datetime.now().strftime('%d.%m.%Y')]
    ]

    info_table = Table(info_data, colWidths=[30*mm, 150*mm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), font_bold),
        ('FONTNAME', (1, 0), (1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 10*mm))

    # Обрабатываем каждую систему
    for sys_idx, system in enumerate(order.systems):
        if sys_idx > 0:
            elements.append(PageBreak())

        # Заголовок системы
        system_header_style = ParagraphStyle(
            'SystemHeader',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=10,
            fontName=font_bold
        )

        system_header = Paragraph(
            f"Позиция {system.position}: {system.system_type}",
            system_header_style
        )
        elements.append(system_header)

        # Параметры системы
        sys_info = system.calculated_data.get('system_info', {}) if system.calculated_data else {}
        params_data = [
            ['Размер проема:', f"{system.width} × {system.height} мм"],
            ['Количество створок:', f"{int(system.panels)}"],
            ['Направление открывания:', system.opening or 'влево'],
        ]

        if sys_info.get('track_type'):
            params_data.append(['Тип направляющих:', sys_info['track_type']])

        params_table = Table(params_data, colWidths=[45*mm, 140*mm])
        params_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), font_bold),
            ('FONTNAME', (1, 0), (1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ]))
        elements.append(params_table)
        elements.append(Spacer(1, 8*mm))

        # Получаем данные расчёта
        calc_data = system.calculated_data or {}

        # Генерируем таблицу для каждой категории
        categories = [
            ('ПРОФИЛИ', 'profiles'),
            ('ФУРНИТУРА', 'hardware'),
            ('УПЛОТНИТЕЛИ', 'seals'),
            ('МЕЖСТВОРОЧНЫЕ УПЛОТНИТЕЛИ', 'interpanel_seals'),
            ('РАСХОДНЫЕ МАТЕРИАЛЫ', 'consumables'),
            ('КРЕПЁЖ', 'fasteners'),
        ]

        for cat_name, cat_key in categories:
            items = calc_data.get(cat_key, [])
            if not items:
                continue

            # Заголовок категории
            cat_style = ParagraphStyle(
                'Category',
                parent=styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#1f4788'),
                fontName=font_bold,
                spaceBefore=5,
                spaceAfter=3
            )
            cat_header = Paragraph(cat_name, cat_style)
            elements.append(cat_header)

            # Таблица комплектующих
            table_data = [['№', 'Артикул', 'Наименование', 'Ед.изм.', 'Кол-во']]

            for idx, item in enumerate(items, 1):
                code = item.get('code', '—')
                name = item.get('name', '—')

                # Определяем единицу измерения и количество
                if cat_key in ['profiles', 'seals', 'interpanel_seals']:
                    # Для профилей и уплотнителей - метры
                    qty = item.get('total_m', 0)
                    unit = 'п.м.'
                else:
                    # Для остального - штуки
                    qty = item.get('qty', item.get('pieces', 0))
                    unit = item.get('unit', 'шт')

                # Добавляем примечание если есть
                note = item.get('note', '')
                if note:
                    name = f"{name} ({note})"

                table_data.append([
                    str(idx),
                    code,
                    name,
                    unit,
                    f"{qty:.2f}" if isinstance(qty, float) else str(qty)
                ])

            # Создаем таблицу
            table = Table(table_data, colWidths=[8*mm, 22*mm, 95*mm, 20*mm, 20*mm])
            table.setStyle(TableStyle([
                # Заголовок
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), font_bold),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),

                # Тело таблицы
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # № по центру
                ('ALIGN', (1, 1), (2, -1), 'LEFT'),    # Артикул и название слева
                ('ALIGN', (3, 1), (3, -1), 'CENTER'),  # Ед.изм. по центру
                ('ALIGN', (4, 1), (4, -1), 'RIGHT'),   # Кол-во справа
                ('FONTNAME', (0, 1), (-1, -1), font_name),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 1), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            ]))

            elements.append(table)
            elements.append(Spacer(1, 5*mm))

    # Генерируем PDF
    doc.build(elements)

    return output_path
