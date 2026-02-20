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
