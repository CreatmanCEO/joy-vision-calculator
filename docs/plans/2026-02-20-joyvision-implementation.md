# Joy Vision Calculator - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Реализовать веб-приложение для расчёта комплектующих безрамного остекления с генерацией PDF и интеграцией с Битрикс24.

**Architecture:** Flask + SQLAlchemy + Blueprint модули. Калькулятор адаптируется из существующего `calculator.py`. PDF генерируется через ReportLab. API REST для интеграции.

**Tech Stack:** Python 3.10+, Flask 3.x, SQLAlchemy 2.x, SQLite/PostgreSQL, ReportLab, Bootstrap 5, HTMX

---

## Phase 1: Базовая инфраструктура (MVP)

### Task 1: Исправить циклический импорт в app.py

**Files:**
- Modify: `C:/Hans/app/app.py`
- Modify: `C:/Hans/app/models/__init__.py`

**Step 1: Проверить текущее состояние**

Run: `cd C:/Hans/app && python -c "from app import create_app; app = create_app(); print('OK')"`
Expected: ImportError (циклический импорт models → app → db)

**Step 2: Вынести db в отдельный файл**

Create: `C:/Hans/app/extensions.py`
```python
# extensions.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
```

**Step 3: Обновить app.py**

```python
# app.py
from flask import Flask, render_template, jsonify
from extensions import db
from config import get_config

def create_app(config_class=None):
    app = Flask(__name__)

    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)

    db.init_app(app)

    # Импорт blueprints внутри функции
    from modules.orders.routes import orders_bp
    from modules.pricing.routes import pricing_bp

    app.register_blueprint(orders_bp, url_prefix='/api')
    app.register_blueprint(pricing_bp, url_prefix='/api')

    with app.app_context():
        from models import Order, OrderSystem, PriceItem
        db.create_all()

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/health')
    def health():
        return jsonify({'status': 'ok', 'app': 'Joy Vision Calculator'})

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'success': False, 'error': 'Not found'}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
```

**Step 4: Обновить models/__init__.py**

```python
# models/__init__.py
from extensions import db
from .order import Order, OrderSystem
from .price import PriceItem

__all__ = ['db', 'Order', 'OrderSystem', 'PriceItem']
```

**Step 5: Обновить models/order.py (импорт db)**

Заменить `from app import db` на `from extensions import db`

**Step 6: Обновить models/price.py (импорт db)**

Заменить `from app import db` на `from extensions import db`

**Step 7: Обновить modules/orders/routes.py**

Заменить `from app import db` на `from extensions import db`

**Step 8: Обновить modules/pricing/routes.py**

Заменить `from app import db` на `from extensions import db`

**Step 9: Проверить запуск**

Run: `cd C:/Hans/app && python -c "from app import create_app; app = create_app(); print('OK')"`
Expected: `OK`

**Step 10: Commit**

```bash
git add -A
git commit -m "fix: resolve circular import with extensions.py"
```

---

### Task 2: Создать тесты для моделей

**Files:**
- Create: `C:/Hans/app/tests/__init__.py`
- Create: `C:/Hans/app/tests/conftest.py`
- Create: `C:/Hans/app/tests/test_models.py`

**Step 1: Создать conftest.py с фикстурами**

```python
# tests/conftest.py
import pytest
from app import create_app
from extensions import db as _db
from config import TestingConfig

@pytest.fixture(scope='session')
def app():
    app = create_app(TestingConfig)
    return app

@pytest.fixture(scope='function')
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()
```

**Step 2: Написать тест создания заказа**

```python
# tests/test_models.py
import pytest
from models import Order, OrderSystem, PriceItem

def test_create_order(db):
    order = Order(customer_name='Тест Компания', city='Москва')
    db.session.add(order)
    db.session.commit()

    assert order.id is not None
    assert order.customer_name == 'Тест Компания'
    assert order.status == 'draft'

def test_order_with_systems(db):
    order = Order(customer_name='Тест')
    db.session.add(order)
    db.session.commit()

    system = OrderSystem(
        order_id=order.id,
        position=1,
        system_type='Slider L',
        width=3000,
        height=2500,
        panels=3
    )
    db.session.add(system)
    db.session.commit()

    assert order.systems.count() == 1
    assert system.system_type == 'Slider L'

def test_order_recalculate_total(db):
    order = Order(customer_name='Тест', discount_percent=10)
    db.session.add(order)
    db.session.commit()

    system1 = OrderSystem(order_id=order.id, position=1,
                          system_type='Slider L', width=3000, height=2500,
                          panels=3, price=50000)
    system2 = OrderSystem(order_id=order.id, position=2,
                          system_type='JV Line', width=2500, height=2200,
                          panels=4, price=60000)
    db.session.add_all([system1, system2])
    db.session.commit()

    order.recalculate_total()

    # 110000 * 0.9 = 99000
    assert order.total_price == 99000

def test_price_item(db):
    item = PriceItem(
        article='S-010',
        name='Верхний профиль 3 дорожки',
        unit='п.м.',
        price=1500,
        category='Профили'
    )
    db.session.add(item)
    db.session.commit()

    assert item.id is not None
    assert item.article == 'S-010'
```

**Step 3: Запустить тесты**

Run: `cd C:/Hans/app && pip install pytest pytest-flask && pytest tests/ -v`
Expected: 4 tests PASSED

**Step 4: Commit**

```bash
git add tests/
git commit -m "test: add model tests"
```

---

### Task 3: Тесты API заказов

**Files:**
- Create: `C:/Hans/app/tests/test_orders_api.py`

**Step 1: Написать тесты API**

```python
# tests/test_orders_api.py
import pytest
import json

def test_list_orders_empty(client, db):
    response = client.get('/api/orders')
    data = json.loads(response.data)

    assert response.status_code == 200
    assert data['success'] == True
    assert data['data'] == []

def test_create_order(client, db):
    response = client.post('/api/orders',
        data=json.dumps({'customer_name': 'Тест'}),
        content_type='application/json')
    data = json.loads(response.data)

    assert response.status_code == 201
    assert data['success'] == True
    assert data['data']['customer_name'] == 'Тест'
    assert data['data']['id'] is not None

def test_create_order_validation(client, db):
    response = client.post('/api/orders',
        data=json.dumps({}),
        content_type='application/json')
    data = json.loads(response.data)

    assert response.status_code == 400
    assert data['success'] == False

def test_get_order(client, db):
    # Создаём заказ
    response = client.post('/api/orders',
        data=json.dumps({'customer_name': 'Тест'}),
        content_type='application/json')
    order_id = json.loads(response.data)['data']['id']

    # Получаем заказ
    response = client.get(f'/api/orders/{order_id}')
    data = json.loads(response.data)

    assert response.status_code == 200
    assert data['data']['id'] == order_id

def test_get_order_not_found(client, db):
    response = client.get('/api/orders/999')
    assert response.status_code == 404

def test_update_order(client, db):
    # Создаём
    response = client.post('/api/orders',
        data=json.dumps({'customer_name': 'Тест'}),
        content_type='application/json')
    order_id = json.loads(response.data)['data']['id']

    # Обновляем
    response = client.put(f'/api/orders/{order_id}',
        data=json.dumps({'customer_name': 'Новое имя', 'status': 'confirmed'}),
        content_type='application/json')
    data = json.loads(response.data)

    assert response.status_code == 200
    assert data['data']['customer_name'] == 'Новое имя'
    assert data['data']['status'] == 'confirmed'

def test_delete_order(client, db):
    # Создаём
    response = client.post('/api/orders',
        data=json.dumps({'customer_name': 'Тест'}),
        content_type='application/json')
    order_id = json.loads(response.data)['data']['id']

    # Удаляем
    response = client.delete(f'/api/orders/{order_id}')
    assert response.status_code == 200

    # Проверяем
    response = client.get(f'/api/orders/{order_id}')
    assert response.status_code == 404

def test_add_system_to_order(client, db):
    # Создаём заказ
    response = client.post('/api/orders',
        data=json.dumps({'customer_name': 'Тест'}),
        content_type='application/json')
    order_id = json.loads(response.data)['data']['id']

    # Добавляем систему
    response = client.post(f'/api/orders/{order_id}/systems',
        data=json.dumps({
            'system_type': 'Slider L',
            'width': 3000,
            'height': 2500,
            'panels': 3
        }),
        content_type='application/json')
    data = json.loads(response.data)

    assert response.status_code == 201
    assert data['data']['position'] == 1
    assert data['data']['system_type'] == 'Slider L'
```

**Step 2: Запустить тесты**

Run: `cd C:/Hans/app && pytest tests/test_orders_api.py -v`
Expected: All tests PASSED

**Step 3: Commit**

```bash
git add tests/test_orders_api.py
git commit -m "test: add orders API tests"
```

---

## Phase 2: Интеграция калькулятора

### Task 4: Адаптировать calculator.py

**Files:**
- Copy: `C:/Hans/calculator.py` → `C:/Hans/app/modules/calculator/core.py`
- Modify: `C:/Hans/app/modules/calculator/__init__.py`

**Step 1: Скопировать и адаптировать калькулятор**

Скопировать `C:/Hans/calculator.py` в `C:/Hans/app/modules/calculator/core.py`.

Убрать tkinter-зависимости (если есть). Оставить только функции расчёта.

**Step 2: Создать wrapper для calculate_system**

```python
# modules/calculator/__init__.py
from .core import (
    calculate_slider_l,
    calculate_slider_x,
    calculate_jv_line,
    calculate_jv_zigzag
)

def calculate_system(system_data: dict) -> dict:
    """
    Рассчитать комплектующие для системы
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

    return calculator(**system_data)
```

**Step 3: Написать тест калькулятора**

```python
# tests/test_calculator.py
import pytest
from modules.calculator import calculate_system

def test_calculate_slider_l():
    result = calculate_system({
        'system_type': 'Slider L',
        'width': 3000,
        'height': 2500,
        'panels': 3,
        'opening': 'влево',
        'left_edge': 'боковой профиль',
        'right_edge': 'боковой профиль'
    })

    assert 'system_info' in result
    assert 'profiles' in result
    assert 'hardware' in result
    assert result['system_info']['type'] == 'Slider L'
    assert len(result['profiles']) > 0

def test_calculate_unknown_system():
    with pytest.raises(ValueError):
        calculate_system({'system_type': 'Unknown'})
```

**Step 4: Запустить тесты**

Run: `cd C:/Hans/app && pytest tests/test_calculator.py -v`
Expected: PASSED

**Step 5: Commit**

```bash
git add modules/calculator/ tests/test_calculator.py
git commit -m "feat: integrate calculator from calculator.py"
```

---

### Task 5: Подключить калькулятор к API заказов

**Files:**
- Modify: `C:/Hans/app/modules/orders/routes.py:add_system()`

**Step 1: Обновить add_system**

```python
# В modules/orders/routes.py, функция add_system
from modules.calculator import calculate_system

@orders_bp.route('/orders/<int:order_id>/systems', methods=['POST'])
def add_system(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'success': False, 'error': 'Заказ не найден'}), 404

    data = request.get_json()

    # Валидация
    required = ['system_type', 'width', 'height', 'panels']
    for field in required:
        if field not in data:
            return jsonify({'success': False, 'error': f'{field} обязателен'}), 400

    # Расчёт
    try:
        calculated = calculate_system(data)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

    # Определяем позицию
    max_pos = db.session.query(db.func.max(OrderSystem.position)).filter(
        OrderSystem.order_id == order_id
    ).scalar() or 0

    system = OrderSystem(
        order_id=order_id,
        position=max_pos + 1,
        system_type=data['system_type'],
        width=data['width'],
        height=data['height'],
        panels=data['panels'],
        opening=data.get('opening', 'влево'),
        left_edge=data.get('left_edge', 'боковой профиль'),
        right_edge=data.get('right_edge', 'боковой профиль'),
        calculated_data=calculated,
        price=calculated.get('summary', {}).get('total_price', 0)
    )

    db.session.add(system)
    order.recalculate_total()
    db.session.commit()

    return jsonify({'success': True, 'data': system.to_dict()}), 201
```

**Step 2: Тест интеграции**

Run: `cd C:/Hans/app && pytest tests/test_orders_api.py::test_add_system_to_order -v`
Expected: PASSED с реальными расчётами

**Step 3: Commit**

```bash
git add modules/orders/routes.py
git commit -m "feat: connect calculator to orders API"
```

---

## Phase 3: Генерация PDF

### Task 6: Адаптировать PDF разблюдовки

**Files:**
- Copy from: `C:/Hans/Разблюдовка_KP/reader_0.2.py`
- Create: `C:/Hans/app/modules/pdf/specification.py`
- Create: `C:/Hans/app/modules/pdf/routes.py`

**Step 1: Извлечь функцию generate_specification_pdf**

Скопировать функцию `generate_specification_pdf` из `reader_0.2.py` в `specification.py`.
Убрать tkinter-зависимости. Адаптировать под данные из Order/OrderSystem.

**Step 2: Создать API эндпоинт**

```python
# modules/pdf/routes.py
from flask import Blueprint, send_file, jsonify, current_app
from models import Order
from .specification import generate_specification_pdf
import os

pdf_bp = Blueprint('pdf', __name__)

@pdf_bp.route('/orders/<int:order_id>/pdf/spec', methods=['GET'])
def download_specification(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'success': False, 'error': 'Заказ не найден'}), 404

    output_path = os.path.join(
        current_app.config['PDF_EXPORTS_DIR'],
        f'Spec_{order_id}.pdf'
    )

    generate_specification_pdf(order, output_path)

    return send_file(
        output_path,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'Разблюдовка_{order_id}.pdf'
    )
```

**Step 3: Зарегистрировать blueprint в app.py**

```python
from modules.pdf.routes import pdf_bp
app.register_blueprint(pdf_bp, url_prefix='/api')
```

**Step 4: Тест генерации**

```python
# tests/test_pdf.py
def test_download_specification(client, db):
    # Создаём заказ с системой
    response = client.post('/api/orders',
        data=json.dumps({'customer_name': 'Тест', 'ral_color': 'RAL 9016'}),
        content_type='application/json')
    order_id = json.loads(response.data)['data']['id']

    client.post(f'/api/orders/{order_id}/systems',
        data=json.dumps({
            'system_type': 'Slider L',
            'width': 3000, 'height': 2500, 'panels': 3
        }),
        content_type='application/json')

    # Скачиваем PDF
    response = client.get(f'/api/orders/{order_id}/pdf/spec')

    assert response.status_code == 200
    assert response.content_type == 'application/pdf'
```

**Step 5: Commit**

```bash
git add modules/pdf/ tests/test_pdf.py
git commit -m "feat: add PDF specification generation"
```

---

### Task 7: Создать PDF коммерческого предложения

**Files:**
- Create: `C:/Hans/app/modules/pdf/commercial.py`
- Modify: `C:/Hans/app/modules/pdf/routes.py`

**Step 1: Создать генератор КП**

```python
# modules/pdf/commercial.py
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from datetime import datetime

def generate_commercial_pdf(order, output_path):
    """Генерация коммерческого предложения"""
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # Заголовок
    title = Paragraph(f"<b>КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ №{order.id}</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 10*mm))

    # Информация о заказчике
    elements.append(Paragraph(f"<b>Заказчик:</b> {order.customer_name}", styles['Normal']))
    elements.append(Paragraph(f"<b>Город:</b> {order.city or '-'}", styles['Normal']))
    elements.append(Paragraph(f"<b>Дата:</b> {datetime.now().strftime('%d.%m.%Y')}", styles['Normal']))
    elements.append(Spacer(1, 10*mm))

    # Таблица систем
    table_data = [['№', 'Система', 'Размер', 'Створок', 'Сумма']]
    for system in order.systems:
        table_data.append([
            system.position,
            system.system_type,
            f'{system.width}x{system.height}',
            int(system.panels),
            f'{system.price:,.0f} руб.'
        ])

    # Итого
    subtotal = sum(s.price or 0 for s in order.systems)
    table_data.append(['', '', '', 'Итого:', f'{subtotal:,.0f} руб.'])

    if order.discount_percent > 0:
        table_data.append(['', '', '', f'Скидка {order.discount_percent}%:',
                         f'-{subtotal * order.discount_percent / 100:,.0f} руб.'])
        table_data.append(['', '', '', 'ИТОГО:', f'{order.total_price:,.0f} руб.'])

    table = Table(table_data, colWidths=[15*mm, 50*mm, 40*mm, 30*mm, 40*mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
    ]))
    elements.append(table)

    # Срок действия
    elements.append(Spacer(1, 20*mm))
    elements.append(Paragraph("Предложение действительно 14 дней.", styles['Normal']))

    doc.build(elements)
    return output_path
```

**Step 2: Добавить endpoint**

```python
# В modules/pdf/routes.py
from .commercial import generate_commercial_pdf

@pdf_bp.route('/orders/<int:order_id>/pdf/kp', methods=['GET'])
def download_commercial(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'success': False, 'error': 'Заказ не найден'}), 404

    output_path = os.path.join(
        current_app.config['PDF_EXPORTS_DIR'],
        f'KP_{order_id}.pdf'
    )

    generate_commercial_pdf(order, output_path)

    return send_file(
        output_path,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'КП_{order_id}.pdf'
    )
```

**Step 3: Тест**

Run: `pytest tests/test_pdf.py -v`

**Step 4: Commit**

```bash
git commit -am "feat: add commercial PDF generation"
```

---

## Phase 4: Управление ценами

### Task 8: Импорт цен из Excel

**Files:**
- Modify: `C:/Hans/app/modules/pricing/routes.py:import_prices()`

**Step 1: Реализовать импорт**

```python
# В modules/pricing/routes.py
import pandas as pd
from io import BytesIO

@pricing_bp.route('/prices/import', methods=['POST'])
def import_prices():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'Файл не передан'}), 400

    file = request.files['file']
    if not file.filename.endswith(('.xlsx', '.xlsm')):
        return jsonify({'success': False, 'error': 'Только .xlsx/.xlsm'}), 400

    try:
        df = pd.read_excel(BytesIO(file.read()))

        # Ожидаем колонки: Артикул, Наименование, Ед.изм., Цена, Категория
        required_cols = ['Артикул', 'Наименование', 'Цена', 'Категория']
        if not all(col in df.columns for col in required_cols):
            return jsonify({'success': False,
                          'error': f'Нужны колонки: {required_cols}'}), 400

        created = 0
        updated = 0
        errors = []

        for _, row in df.iterrows():
            article = str(row['Артикул']).strip()
            if not article:
                continue

            item = PriceItem.query.filter_by(article=article).first()

            if item:
                item.name = row['Наименование']
                item.price = float(row['Цена'])
                item.category = row['Категория']
                item.unit = row.get('Ед.изм.', 'шт')
                updated += 1
            else:
                item = PriceItem(
                    article=article,
                    name=row['Наименование'],
                    price=float(row['Цена']),
                    category=row['Категория'],
                    unit=row.get('Ед.изм.', 'шт')
                )
                db.session.add(item)
                created += 1

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Импортировано: создано {created}, обновлено {updated}',
            'created': created,
            'updated': updated,
            'errors': errors
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

**Step 2: Тест импорта**

Создать тестовый Excel и проверить импорт.

**Step 3: Commit**

```bash
git commit -am "feat: implement price import from Excel"
```

---

## Phase 5: Интеграция с Битрикс24

### Task 9: Адаптировать bitrix_api.py

**Files:**
- Copy from: `C:/Hans/old/core/bitrix_api.py`
- Create: `C:/Hans/app/modules/bitrix/api.py`
- Create: `C:/Hans/app/modules/bitrix/routes.py`

**Step 1: Извлечь функции API**

Скопировать функции: `create_deal`, `update_deal`, `get_deal_by_id`, `upload_file_to_bitrix`.
Убрать tkinter (messagebox → raise Exception).
Использовать config для WEBHOOK_URL.

**Step 2: Создать routes**

```python
# modules/bitrix/routes.py
from flask import Blueprint, jsonify, current_app
from models import Order
from .api import create_deal, update_deal, upload_file_to_bitrix
from modules.pdf.commercial import generate_commercial_pdf
from modules.pdf.specification import generate_specification_pdf
import os

bitrix_bp = Blueprint('bitrix', __name__)

@bitrix_bp.route('/sync/<int:order_id>', methods=['POST'])
def sync_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'success': False, 'error': 'Заказ не найден'}), 404

    try:
        # Создаём/обновляем сделку
        if order.bitrix_deal_id:
            update_deal(order.bitrix_deal_id, order.total_price)
            action = 'updated'
        else:
            deal_id = create_deal(order.customer_name, order.total_price)
            order.bitrix_deal_id = deal_id
            db.session.commit()
            action = 'created'

        # Генерируем и загружаем PDF
        exports_dir = current_app.config['PDF_EXPORTS_DIR']
        files_uploaded = []

        kp_path = os.path.join(exports_dir, f'KP_{order_id}.pdf')
        generate_commercial_pdf(order, kp_path)
        upload_file_to_bitrix(kp_path)
        files_uploaded.append(f'KP_{order_id}.pdf')

        spec_path = os.path.join(exports_dir, f'Spec_{order_id}.pdf')
        generate_specification_pdf(order, spec_path)
        upload_file_to_bitrix(spec_path)
        files_uploaded.append(f'Spec_{order_id}.pdf')

        return jsonify({
            'success': True,
            'data': {
                'bitrix_deal_id': order.bitrix_deal_id,
                'action': action,
                'files_uploaded': files_uploaded
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

**Step 3: Зарегистрировать blueprint**

**Step 4: Тест (mock Битрикс)**

**Step 5: Commit**

```bash
git commit -am "feat: add Bitrix24 integration"
```

---

## Phase 6: UI

### Task 10: Страница просмотра заказа

**Files:**
- Create: `C:/Hans/app/templates/order/detail.html`
- Add route in app.py

### Task 11: Форма добавления системы

**Files:**
- Create: `C:/Hans/app/templates/order/system_form.html`

### Task 12: Страница управления ценами

**Files:**
- Create: `C:/Hans/app/templates/prices/list.html`

---

## Summary

| Phase | Tasks | Описание |
|-------|-------|----------|
| 1 | 1-3 | Исправить импорты, тесты моделей и API |
| 2 | 4-5 | Интегрировать калькулятор |
| 3 | 6-7 | PDF генерация |
| 4 | 8 | Импорт цен |
| 5 | 9 | Битрикс интеграция |
| 6 | 10-12 | UI страницы |

---

**Estimated effort:** 12 tasks × ~30 min = ~6 hours active development
