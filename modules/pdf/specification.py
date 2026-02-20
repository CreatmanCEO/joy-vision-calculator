# modules/pdf/specification.py
"""
Генерация PDF разблюдовки (спецификации комплектующих)
Адаптировано из C:/Hans/Разблюдовка_KP/reader_0.2.py
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os


def generate_specification_pdf(order, output_path):
    """
    Генерация разблюдовки (спецификации комплектующих) для заказа
    
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
        leftMargin=15*mm,
        rightMargin=15*mm
    )
    
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
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName=font_name
    )
    
    title = Paragraph(f"РАЗБЛЮДОВКА №{order.id}", title_style)
    elements.append(title)
    
    # Информация о заказе
    info_style = ParagraphStyle(
        'Info',
        parent=styles['Normal'],
        fontSize=10,
        fontName=font_name
    )
    
    elements.append(Paragraph(f"<b>Заказчик:</b> {order.customer_name}", info_style))
    if order.city:
        elements.append(Paragraph(f"<b>Город:</b> {order.city}", info_style))
    elements.append(Paragraph(f"<b>Цвет RAL:</b> {order.ral_color}", info_style))
    elements.append(Spacer(1, 10*mm))
    
    # Обрабатываем каждую систему
    for system in order.systems:
        # Заголовок системы
        system_title = Paragraph(
            f"<b>Позиция {system.position}: {system.system_type} "
            f"({system.width}x{system.height} мм, {int(system.panels)} створок)</b>",
            info_style
        )
        elements.append(system_title)
        elements.append(Spacer(1, 5*mm))
        
        # Получаем данные расчёта
        calc_data = system.calculated_data or {}
        
        # Генерируем таблицу для каждой категории
        categories = [
            ('Профили', 'profiles'),
            ('Фурнитура', 'hardware'),
            ('Уплотнители', 'seals'),
            ('Расходники', 'consumables'),
            ('Крепёж', 'fasteners')
        ]
        
        for cat_name, cat_key in categories:
            items = calc_data.get(cat_key, [])
            if not items:
                continue
            
            # Заголовок категории
            cat_header = Paragraph(f"<b>{cat_name}</b>", info_style)
            elements.append(cat_header)
            elements.append(Spacer(1, 2*mm))
            
            # Таблица комплектующих
            table_data = [['Артикул', 'Наименование', 'Ед.изм.', 'Кол-во', 'Цена', 'Сумма']]
            
            for item in items:
                article = item.get('article', '-')
                name = item.get('name', '-')
                unit = item.get('unit', 'шт')
                quantity = item.get('quantity', 0)
                price = item.get('price', 0)
                total = quantity * price
                
                table_data.append([
                    article,
                    name,
                    unit,
                    f"{quantity:.2f}",
                    f"{price:.2f}",
                    f"{total:.2f}"
                ])
            
            # Создаем таблицу
            table = Table(table_data, colWidths=[20*mm, 60*mm, 15*mm, 20*mm, 20*mm, 20*mm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e0e0e0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), font_name),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTNAME', (0, 1), (-1, -1), font_name),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 5*mm))
        
        # Итоговая стоимость системы
        if system.price:
            price_text = Paragraph(
                f"<b>Итого по позиции {system.position}: {system.price:,.2f} руб.</b>",
                info_style
            )
            elements.append(price_text)
        
        elements.append(Spacer(1, 10*mm))
    
    # Общая стоимость заказа
    if order.total_price:
        total_style = ParagraphStyle(
            'Total',
            parent=info_style,
            fontSize=12,
            textColor=colors.HexColor('#1f4788')
        )
        total_text = Paragraph(
            f"<b>ИТОГО ПО ЗАКАЗУ: {order.total_price:,.2f} руб.</b>",
            total_style
        )
        elements.append(total_text)
    
    # Генерируем PDF
    doc.build(elements)
    
    return output_path
