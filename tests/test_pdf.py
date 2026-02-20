# tests/test_pdf.py
import json
import os

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
    assert len(response.data) > 0  # Проверяем, что PDF не пустой


def test_download_commercial(client, db):
    # Создаём заказ с двумя системами и скидкой
    response = client.post('/api/orders',
        data=json.dumps({
            'customer_name': 'Тест Компания',
            'city': 'Москва',
            'ral_color': 'RAL 9016',
            'discount_percent': 10
        }),
        content_type='application/json')
    order_id = json.loads(response.data)['data']['id']

    # Добавляем две системы
    client.post(f'/api/orders/{order_id}/systems',
        data=json.dumps({
            'system_type': 'Slider L',
            'width': 3000, 'height': 2500, 'panels': 3
        }),
        content_type='application/json')

    client.post(f'/api/orders/{order_id}/systems',
        data=json.dumps({
            'system_type': 'JV Line',
            'width': 2500, 'height': 2200, 'panels': 4
        }),
        content_type='application/json')

    # Скачиваем PDF КП
    response = client.get(f'/api/orders/{order_id}/pdf/kp')

    assert response.status_code == 200
    assert response.content_type == 'application/pdf'
    assert len(response.data) > 0
