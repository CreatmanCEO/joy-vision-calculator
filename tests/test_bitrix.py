# tests/test_bitrix.py
import json
import os
from unittest.mock import patch, MagicMock

def test_sync_order_creates_deal(client, db):
    """Тест создания сделки в Битрикс24"""
    # Создаём заказ с системой
    response = client.post('/api/orders',
        data=json.dumps({'customer_name': 'Тест Компания', 'city': 'Москва'}),
        content_type='application/json')
    order_id = json.loads(response.data)['data']['id']

    client.post(f'/api/orders/{order_id}/systems',
        data=json.dumps({
            'system_type': 'Slider L',
            'width': 3000, 'height': 2500, 'panels': 3
        }),
        content_type='application/json')

    # Мокируем API Битрикс24
    with patch('modules.bitrix.routes.create_deal') as mock_create, \
         patch('modules.bitrix.routes.upload_file_to_bitrix') as mock_upload:

        mock_create.return_value = 12345
        mock_upload.return_value = 67890
        
        # Синхронизируем с Битрикс24
        response = client.post(f'/api/bitrix/sync/{order_id}')
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] == True
        assert data['data']['action'] == 'created'
        assert data['data']['bitrix_deal_id'] == 12345
        assert len(data['data']['files_uploaded']) == 2


def test_sync_order_updates_deal(client, db):
    """Тест обновления существующей сделки"""
    # Создаём заказ с уже установленным bitrix_deal_id
    response = client.post('/api/orders',
        data=json.dumps({'customer_name': 'Тест', 'city': 'СПб'}),
        content_type='application/json')
    order_id = json.loads(response.data)['data']['id']

    # Устанавливаем bitrix_deal_id вручную
    from models import Order
    order = Order.query.get(order_id)
    order.bitrix_deal_id = 99999
    db.session.commit()

    client.post(f'/api/orders/{order_id}/systems',
        data=json.dumps({
            'system_type': 'JV Line',
            'width': 2500, 'height': 2200, 'panels': 4
        }),
        content_type='application/json')

    # Мокируем API
    with patch('modules.bitrix.routes.update_deal') as mock_update, \
         patch('modules.bitrix.routes.upload_file_to_bitrix') as mock_upload:

        mock_update.return_value = True
        mock_upload.return_value = 11111
        
        response = client.post(f'/api/bitrix/sync/{order_id}')
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] == True
        assert data['data']['action'] == 'updated'
        assert data['data']['bitrix_deal_id'] == 99999
