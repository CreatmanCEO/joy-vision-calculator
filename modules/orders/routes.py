# modules/orders/routes.py
"""
API эндпоинты для работы с заказами
"""

from flask import Blueprint, request, jsonify
from extensions import db
from models.order import Order, OrderSystem

orders_bp = Blueprint('orders', __name__)


@orders_bp.route('/orders', methods=['GET'])
def list_orders():
    """Получить список заказов"""
    status = request.args.get('status')
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)

    query = Order.query

    if status:
        query = query.filter(Order.status == status)

    total = query.count()
    orders = query.order_by(Order.created_at.desc()).offset(offset).limit(limit).all()

    return jsonify({
        'success': True,
        'data': [o.to_dict() for o in orders],
        'total': total,
        'limit': limit,
        'offset': offset
    })


@orders_bp.route('/orders', methods=['POST'])
def create_order():
    """Создать новый заказ"""
    data = request.get_json()

    if not data.get('customer_name'):
        return jsonify({'success': False, 'error': 'customer_name обязателен'}), 400

    order = Order(
        customer_name=data['customer_name'],
        city=data.get('city'),
        ral_color=data.get('ral_color', 'RAL 9016'),
        discount_percent=data.get('discount_percent', 0),
        with_glass=data.get('with_glass', True),
        with_assembly=data.get('with_assembly', False),
        with_install=data.get('with_install', False),
        notes=data.get('notes')
    )

    db.session.add(order)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': order.to_dict()
    }), 201


@orders_bp.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Получить заказ по ID"""
    order = Order.query.get(order_id)

    if not order:
        return jsonify({'success': False, 'error': 'Заказ не найден'}), 404

    return jsonify({
        'success': True,
        'data': order.to_dict(include_systems=True)
    })


@orders_bp.route('/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    """Обновить заказ"""
    order = Order.query.get(order_id)

    if not order:
        return jsonify({'success': False, 'error': 'Заказ не найден'}), 404

    data = request.get_json()

    # Обновляем только переданные поля
    for field in ['customer_name', 'city', 'ral_color', 'discount_percent',
                  'with_glass', 'with_assembly', 'with_install', 'status', 'notes']:
        if field in data:
            setattr(order, field, data[field])

    # Пересчитываем сумму если изменилась скидка
    if 'discount_percent' in data:
        order.recalculate_total()

    db.session.commit()

    return jsonify({
        'success': True,
        'data': order.to_dict()
    })


@orders_bp.route('/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    """Удалить заказ"""
    order = Order.query.get(order_id)

    if not order:
        return jsonify({'success': False, 'error': 'Заказ не найден'}), 404

    db.session.delete(order)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Заказ #{order_id} удалён'
    })


# === Системы в заказе ===

@orders_bp.route('/orders/<int:order_id>/systems', methods=['POST'])
def add_system(order_id):
    """Добавить систему в заказ"""
    order = Order.query.get(order_id)

    if not order:
        return jsonify({'success': False, 'error': 'Заказ не найден'}), 404

    data = request.get_json()

    # Валидация
    required = ['system_type', 'width', 'height', 'panels']
    for field in required:
        if field not in data:
            return jsonify({'success': False, 'error': f'{field} обязателен'}), 400

    # Определяем следующую позицию
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
        handle_type=data.get('handle_type', 'круглая'),
        handle_count=data.get('handle_count', 2),
        latch_count=data.get('latch_count', 2),
        glass_thickness=data.get('glass_thickness', 10),
        seal_type=data.get('seal_type', 'светопрозрачный'),
        handle_height=data.get('handle_height', 1000),
        floor_lock=data.get('floor_lock', False),
        closer=data.get('closer', False),
        painting=data.get('painting', False),
        custom_ral_color=data.get('custom_ral_color')
    )

    # TODO: Вызвать калькулятор и заполнить calculated_data, price
    # from modules.calculator import calculate_system
    # result = calculate_system(system)
    # system.calculated_data = result
    # system.price = calculate_price(result)

    db.session.add(system)
    order.recalculate_total()
    db.session.commit()

    return jsonify({
        'success': True,
        'data': system.to_dict()
    }), 201


@orders_bp.route('/orders/<int:order_id>/systems/<int:position>', methods=['DELETE'])
def delete_system(order_id, position):
    """Удалить систему из заказа"""
    system = OrderSystem.query.filter_by(order_id=order_id, position=position).first()

    if not system:
        return jsonify({'success': False, 'error': 'Система не найдена'}), 404

    order = system.order
    db.session.delete(system)
    order.recalculate_total()
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Система на позиции {position} удалена'
    })
