# modules/pdf/commercial.py
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os

def generate_commercial_pdf(order, output_path):
    """Генерация коммерческого предложения"""
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                           topMargin=20*mm, bottomMargin=20*mm,
                           leftMargin=20*mm, rightMargin=20*mm)
    elements = []
    styles = getSampleStyleSheet()
    
    # Регистрация русского шрифта (если доступен)
    try:
        font_path = 'static/fonts/DejaVuSans.ttf'
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
            font_name = 'DejaVuSans'
        else:
            font_name = 'Helvetica'
    except:
        font_name = 'Helvetica'

    # Заголовок
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName=font_name
    )
    title = Paragraph(f"<b>КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ №{order.id}</b>", title_style)
    elements.append(title)
    elements.append(Spacer(1, 10*mm))

    # Информация о заказчике
    info_style = ParagraphStyle(
        'Info',
        parent=styles['Normal'],
        fontSize=11,
        fontName=font_name
    )
    elements.append(Paragraph(f"<b>Заказчик:</b> {order.customer_name}", info_style))
    if order.city:
        elements.append(Paragraph(f"<b>Город:</b> {order.city}", info_style))
    elements.append(Paragraph(f"<b>Дата:</b> {datetime.now().strftime('%d.%m.%Y')}", info_style))
    if order.ral_color:
        elements.append(Paragraph(f"<b>Цвет RAL:</b> {order.ral_color}", info_style))
    elements.append(Spacer(1, 10*mm))

    # Таблица систем
    table_data = [['№', 'Система', 'Размер (мм)', 'Створок', 'Сумма (руб.)']]
    
    for system in order.systems:
        table_data.append([
            str(system.position),
            system.system_type,
            f'{system.width}×{system.height}',
            str(int(system.panels)),
            f'{system.price:,.2f}' if system.price else '-'
        ])

    # Подытог
    subtotal = sum(s.price or 0 for s in order.systems)
    table_data.append(['', '', '', '<b>Итого:</b>', f'<b>{subtotal:,.2f}</b>'])

    # Скидка (если есть)
    if order.discount_percent > 0:
        discount_amount = subtotal * order.discount_percent / 100
        table_data.append(['', '', '', f'Скидка {order.discount_percent}%:', f'-{discount_amount:,.2f}'])
        table_data.append(['', '', '', '<b>ИТОГО К ОПЛАТЕ:</b>', f'<b>{order.total_price:,.2f}</b>'])

    # Создаем таблицу
    table = Table(table_data, colWidths=[15*mm, 55*mm, 35*mm, 35*mm, 35*mm])
    table.setStyle(TableStyle([
        # Заголовок
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), font_name),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        
        # Тело таблицы
        ('BACKGROUND', (0, 1), (-1, -4), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ('ALIGN', (1, 1), (3, -1), 'LEFT'),
        ('ALIGN', (4, 1), (4, -1), 'RIGHT'),
        ('FONTNAME', (0, 1), (-1, -1), font_name),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -4), 1, colors.grey),
        
        # Итоговые строки
        ('BACKGROUND', (0, -3), (-1, -1), colors.HexColor('#f0f0f0')),
        ('ALIGN', (3, -3), (3, -1), 'RIGHT'),
        ('ALIGN', (4, -3), (4, -1), 'RIGHT'),
        ('LINEABOVE', (0, -3), (-1, -3), 2, colors.grey),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#1f4788')),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
    ]))
    elements.append(table)

    # Дополнительные услуги
    elements.append(Spacer(1, 10*mm))
    if order.with_glass or order.with_assembly or order.with_install:
        services = []
        if order.with_glass:
            services.append("Остекление")
        if order.with_assembly:
            services.append("Сборка")
        if order.with_install:
            services.append("Монтаж")
        
        elements.append(Paragraph(f"<b>Дополнительные услуги:</b> {', '.join(services)}", info_style))
        elements.append(Spacer(1, 5*mm))

    # Примечания
    if order.notes:
        elements.append(Paragraph(f"<b>Примечания:</b>", info_style))
        elements.append(Paragraph(order.notes, info_style))
        elements.append(Spacer(1, 5*mm))

    # Срок действия
    elements.append(Spacer(1, 15*mm))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        fontName=font_name
    )
    elements.append(Paragraph("Предложение действительно 14 дней с даты формирования.", footer_style))
    elements.append(Paragraph("Цены указаны без учёта доставки и монтажа (если не указано иное).", footer_style))

    # Генерируем PDF
    doc.build(elements)
    return output_path
