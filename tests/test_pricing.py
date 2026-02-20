# tests/test_pricing.py
import json
import pandas as pd
from io import BytesIO

def test_import_prices(client, db):
    # Создаём тестовый Excel файл
    data = {
        'Артикул': ['S-010', 'S-020', 'H-001'],
        'Наименование': ['Профиль верхний 3 дорожки', 'Профиль верхний 5 дорожек', 'Ручка круглая'],
        'Ед.изм.': ['п.м.', 'п.м.', 'шт'],
        'Цена': [1500, 2000, 500],
        'Категория': ['Профили', 'Профили', 'Фурнитура']
    }
    df = pd.DataFrame(data)
    
    # Сохраняем в BytesIO
    excel_file = BytesIO()
    df.to_excel(excel_file, index=False, engine='openpyxl')
    excel_file.seek(0)
    
    # Загружаем файл
    response = client.post('/api/prices/import',
        data={'file': (excel_file, 'prices.xlsx')},
        content_type='multipart/form-data')
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['success'] == True
    assert data['created'] == 3
    assert data['updated'] == 0
    
    # Проверяем, что данные импортировались
    response = client.get('/api/prices')
    prices = json.loads(response.data)['data']
    
    assert len(prices) == 3
    assert any(p['article'] == 'S-010' for p in prices)


def test_import_prices_update(client, db):
    # Создаём начальную позицию
    response = client.post('/api/prices',
        data=json.dumps({
            'article': 'TEST-001',
            'name': 'Старое название',
            'price': 100,
            'category': 'Тест'
        }),
        content_type='application/json')
    
    assert response.status_code == 201
    
    # Создаём Excel с обновлённой ценой
    data = {
        'Артикул': ['TEST-001'],
        'Наименование': ['Новое название'],
        'Ед.изм.': ['шт'],
        'Цена': [200],
        'Категория': ['Тест']
    }
    df = pd.DataFrame(data)
    
    excel_file = BytesIO()
    df.to_excel(excel_file, index=False, engine='openpyxl')
    excel_file.seek(0)
    
    # Импортируем
    response = client.post('/api/prices/import',
        data={'file': (excel_file, 'prices.xlsx')},
        content_type='multipart/form-data')
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['created'] == 0
    assert data['updated'] == 1
    
    # Проверяем обновление
    response = client.get('/api/prices')
    prices = json.loads(response.data)['data']
    test_item = [p for p in prices if p['article'] == 'TEST-001'][0]
    
    assert test_item['name'] == 'Новое название'
    assert test_item['price'] == 200
