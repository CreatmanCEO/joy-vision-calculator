# modules/pdf/commercial.py
"""
Генерация коммерческого предложения в стиле JOY VISION
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from .fonts import register_fonts


def generate_commercial_pdf(order, output_path):
    """Генерация коммерческого предложения в стиле JOY VISION"""

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        topMargin=10*mm,
        bottomMargin=15*mm,
        leftMargin=15*mm,
        rightMargin=15*mm
    )

    elements = []
    styles = getSampleStyleSheet()
    font_name, font_bold = register_fonts()

    # Цвета JOY VISION
    joy_blue = colors.HexColor('#00b0e8')  # Яркий голубой
    joy_dark = colors.HexColor('#1a4d7a')  # Темно-синий

    # ========== ШАПКА ==========
    header_data = [[
        Paragraph('<b>Коммерческое предложение</b>', ParagraphStyle(
            'HeaderText',
            fontSize=16,
            textColor=colors.white,
            fontName=font_bold
        )),
        Paragraph('<b>JOY VISION</b><br/><font size=8>СИСТЕМЫ БЕЗРАМНОГО ОСТЕКЛЕНИЯ</font>', ParagraphStyle(
            'Logo',
            fontSize=18,
            alignment=TA_RIGHT,
            textColor=joy_dark,
            fontName=font_bold
        ))
    ]]

    header_table = Table(header_data, colWidths=[100*mm, 80*mm])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), joy_blue),
        ('BACKGROUND', (1, 0), (1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 8*mm))

    # ========== ИНФОРМАЦИЯ О ЗАКАЗЕ ==========
    info_left = [
        ['Заказчик:', order.customer_name],
        ['Контактное лицо:', order.notes.split('\n')[0] if order.notes else '—'],
        ['Телефон:', '—'],
        ['Адрес:', order.city or '—'],
    ]

    info_right = [
        ['Дата оформления:', datetime.now().strftime('%d.%m.%Y')],
        ['Номер заявки:', f'№ {order.id}'],
        ['Цвет RAL:', order.ral_color or 'RAL 9016'],
        ['Срок изготовления:', 'до 30 рабочих дней'],
    ]

    info_table_data = []
    for i in range(max(len(info_left), len(info_right))):
        row = []
        if i < len(info_left):
            row.extend(info_left[i])
        else:
            row.extend(['', ''])
        if i < len(info_right):
            row.extend(info_right[i])
        else:
            row.extend(['', ''])
        info_table_data.append(row)

    info_table = Table(info_table_data, colWidths=[35*mm, 55*mm, 35*mm, 55*mm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), font_bold),
        ('FONTNAME', (2, 0), (2, -1), font_bold),
        ('FONTNAME', (1, 0), (1, -1), font_name),
        ('FONTNAME', (3, 0), (3, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'LEFT'),
        ('LINEBELOW', (0, -1), (-1, -1), 1, joy_blue),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 8*mm))

    # ========== СОСТАВ ЗАКАЗА ==========
    section_style = ParagraphStyle(
        'Section',
        fontSize=12,
        textColor=joy_blue,
        fontName=font_bold,
        spaceAfter=5
    )
    elements.append(Paragraph('Состав заказа', section_style))

    # Таблица систем
    systems_data = [['№', 'Тип системы', 'Габариты, мм', 'Цвет', 'Створок', 'Стоимость, руб', 'Кол-во', 'Итого']]

    for system in order.systems:
        sys_info = system.calculated_data.get('system_info', {}) if system.calculated_data else {}

        # Основная строка системы
        systems_data.append([
            str(system.position),
            system.system_type,
            f'{system.width}×{system.height}',
            order.ral_color or 'RAL',
            str(int(system.panels)),
            f'{system.price:,.2f}' if system.price else '—',
            '1',
            f'{system.price:,.2f}' if system.price else '—'
        ])

        # Детали системы (объединенная строка)
        details = []
        details.append(f"тип системы: {sys_info.get('track_type', '—')}")
        details.append(f"ширина: {system.width} мм")
        details.append(f"высота: {system.height} мм")
        details.append(f"открывание: {system.opening or 'влево'}")
        details.append(f"количество створок: {int(system.panels)}")
        details.append(f"покраска: {'RAL' if order.ral_color else 'без окраски'}")
        details.append(f"стекло: {sys_info.get('glass_thickness_mm', 10)} мм")

        details_text = ', '.join(details)
        systems_data.append(['', details_text, '', '', '', '', '', ''])

    # Итоги
    subtotal = sum(s.price or 0 for s in order.systems)
    systems_data.append(['', '', '', '', '', '', 'Всего:', f'{subtotal:,.2f}'])

    if order.discount_percent > 0:
        systems_data.append(['', '', '', '', '', '', 'Скидка:', f'{order.discount_percent}%'])
        systems_data.append(['', '', '', '', '', '', 'Итого за фурнитуру:', f'{order.total_price:,.2f}'])

    systems_table = Table(systems_data, colWidths=[10*mm, 45*mm, 30*mm, 20*mm, 15*mm, 25*mm, 25*mm, 25*mm])
    systems_table.setStyle(TableStyle([
        # Заголовок
        ('BACKGROUND', (0, 0), (-1, 0), joy_blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), font_bold),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),

        # Основные строки систем
        ('FONTNAME', (0, 1), (-1, -4), font_name),
        ('FONTSIZE', (0, 1), (-1, -4), 9),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ('ALIGN', (5, 1), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -4), 0.5, colors.grey),

        # Строки деталей (каждая вторая, начиная с 2)
        ('SPAN', (1, 2), (4, 2)),  # Детали 1-й системы
        ('FONTSIZE', (1, 2), (1, 2), 7),
        ('TEXTCOLOR', (1, 2), (1, 2), colors.grey),

        # Итоговые строки
        ('FONTNAME', (6, -3), (-1, -1), font_bold),
        ('FONTSIZE', (6, -1), (-1, -1), 11),
        ('LINEABOVE', (6, -3), (-1, -3), 1, colors.grey),
        ('LINEABOVE', (6, -1), (-1, -1), 2, joy_blue),
        ('BACKGROUND', (6, -3), (-1, -1), colors.HexColor('#f0f8ff')),

        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
    ]))
    elements.append(systems_table)
    elements.append(Spacer(1, 10*mm))

    # ========== ДОПОЛНИТЕЛЬНО ==========
    if order.with_glass or order.with_assembly or order.with_install:
        elements.append(Paragraph('Дополнительно', section_style))

        additional_data = [['№', 'Услуга', 'Параметр', 'Стоимость, руб']]
        idx = 1
        additional_total = 0

        if order.with_glass:
            additional_data.append([str(idx), 'Остекление', 'включено в стоимость', '—'])
            idx += 1

        if order.with_assembly:
            assembly_cost = subtotal * 0.05  # 5% от стоимости
            additional_data.append([str(idx), 'Сборка', f'{order.systems_count} систем', f'{assembly_cost:,.2f}'])
            additional_total += assembly_cost
            idx += 1

        if order.with_install:
            install_cost = subtotal * 0.15  # 15% от стоимости
            additional_data.append([str(idx), 'Монтаж', f'{order.systems_count} систем', f'{install_cost:,.2f}'])
            additional_total += install_cost
            idx += 1

        if additional_total > 0:
            additional_data.append(['', '', 'Итого дополнительно:', f'{additional_total:,.2f}'])

        additional_table = Table(additional_data, colWidths=[15*mm, 50*mm, 75*mm, 40*mm])
        additional_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), joy_blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), font_bold),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
            ('FONTNAME', (0, 1), (-1, -1), font_name),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('FONTNAME', (2, -1), (3, -1), font_bold),
            ('LINEABOVE', (2, -1), (3, -1), 2, joy_blue),
            ('BACKGROUND', (2, -1), (3, -1), colors.HexColor('#f0f8ff')),
        ]))
        elements.append(additional_table)
        elements.append(Spacer(1, 10*mm))

        # Общий итог
        grand_total = order.total_price + additional_total
        total_style = ParagraphStyle('GrandTotal', fontSize=14, fontName=font_bold, alignment=TA_RIGHT)
        elements.append(Paragraph(f'Итого без НДС: {grand_total:,.2f} ₽', total_style))

    # ========== ФУТЕР ==========
    elements.append(Spacer(1, 15*mm))
    footer_style = ParagraphStyle(
        'Footer',
        fontSize=9,
        textColor=colors.grey,
        fontName=font_name,
        alignment=TA_CENTER
    )
    elements.append(Paragraph('Предложение действительно 14 дней с даты формирования', footer_style))
    elements.append(Spacer(1, 3*mm))

    contact_style = ParagraphStyle('Contact', fontSize=9, textColor=joy_blue, fontName=font_name, alignment=TA_RIGHT)
    elements.append(Paragraph('info@joyvision.com', contact_style))

    # Генерируем PDF
    doc.build(elements)
    return output_path
