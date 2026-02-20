# models/order.py
"""
Модели заказа и систем в заказе
"""

from datetime import datetime
from app import db


class Order(db.Model):
    """Заказ"""
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    bitrix_deal_id = db.Column(db.Integer, nullable=True, index=True)
    customer_name = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=True)
    ral_color = db.Column(db.String(50), default='RAL 9016')
    discount_percent = db.Column(db.Float, default=0)
    with_glass = db.Column(db.Boolean, default=True)
    with_assembly = db.Column(db.Boolean, default=False)
    with_install = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='draft', index=True)
    total_price = db.Column(db.Float, default=0)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Связь с системами
    systems = db.relationship('OrderSystem', backref='order', lazy='dynamic',
                              cascade='all, delete-orphan', order_by='OrderSystem.position')

    def to_dict(self, include_systems=False):
        """Сериализация в словарь"""
        data = {
            'id': self.id,
            'bitrix_deal_id': self.bitrix_deal_id,
            'customer_name': self.customer_name,
            'city': self.city,
            'ral_color': self.ral_color,
            'discount_percent': self.discount_percent,
            'with_glass': self.with_glass,
            'with_assembly': self.with_assembly,
            'with_install': self.with_install,
            'status': self.status,
            'total_price': self.total_price,
            'notes': self.notes,
            'systems_count': self.systems.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_systems:
            data['systems'] = [s.to_dict() for s in self.systems]
        return data

    def recalculate_total(self):
        """Пересчитать итоговую сумму заказа"""
        subtotal = sum(s.price or 0 for s in self.systems)
        self.total_price = subtotal * (1 - self.discount_percent / 100)

    def __repr__(self):
        return f'<Order #{self.id} "{self.customer_name}">'


class OrderSystem(db.Model):
    """Система в заказе"""
    __tablename__ = 'order_systems'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, index=True)
    position = db.Column(db.Integer, nullable=False)

    # Параметры системы
    system_type = db.Column(db.String(50), nullable=False)
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    panels = db.Column(db.Float, nullable=False)
    opening = db.Column(db.String(20), default='влево')
    left_edge = db.Column(db.String(50), default='боковой профиль')
    right_edge = db.Column(db.String(50), default='боковой профиль')

    # Дополнительные параметры
    handle_type = db.Column(db.String(30), default='круглая')
    handle_count = db.Column(db.Integer, default=2)
    latch_count = db.Column(db.Integer, default=2)
    glass_thickness = db.Column(db.Integer, default=10)
    seal_type = db.Column(db.String(30), default='светопрозрачный')
    handle_height = db.Column(db.Integer, default=1000)
    floor_lock = db.Column(db.Boolean, default=False)
    closer = db.Column(db.Boolean, default=False)
    painting = db.Column(db.Boolean, default=False)
    custom_ral_color = db.Column(db.String(50), nullable=True)

    # Результат расчёта (JSON)
    calculated_data = db.Column(db.JSON, nullable=True)

    # Стоимость
    price = db.Column(db.Float, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('order_id', 'position', name='uix_order_position'),
    )

    def to_dict(self):
        """Сериализация в словарь"""
        return {
            'position': self.position,
            'system_type': self.system_type,
            'width': self.width,
            'height': self.height,
            'panels': self.panels,
            'opening': self.opening,
            'left_edge': self.left_edge,
            'right_edge': self.right_edge,
            'handle_type': self.handle_type,
            'handle_count': self.handle_count,
            'latch_count': self.latch_count,
            'glass_thickness': self.glass_thickness,
            'seal_type': self.seal_type,
            'handle_height': self.handle_height,
            'floor_lock': self.floor_lock,
            'closer': self.closer,
            'painting': self.painting,
            'custom_ral_color': self.custom_ral_color,
            'calculated_data': self.calculated_data,
            'price': self.price
        }

    def __repr__(self):
        return f'<OrderSystem #{self.position} {self.system_type}>'
