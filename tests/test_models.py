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
