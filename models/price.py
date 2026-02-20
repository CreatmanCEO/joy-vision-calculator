# models/price.py
"""
Модель прайс-листа
"""

from datetime import datetime
from extensions import db


class PriceItem(db.Model):
    """Позиция прайс-листа"""
    __tablename__ = 'price_items'

    id = db.Column(db.Integer, primary_key=True)
    article = db.Column(db.String(30), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    unit = db.Column(db.String(20), default='шт')
    price = db.Column(db.Float, default=0)
    category = db.Column(db.String(50), nullable=False, index=True)
    system_types = db.Column(db.JSON, nullable=True)  # ["Slider L", "Slider X"]
    is_active = db.Column(db.Boolean, default=True, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Сериализация в словарь"""
        return {
            'id': self.id,
            'article': self.article,
            'name': self.name,
            'unit': self.unit,
            'price': self.price,
            'category': self.category,
            'system_types': self.system_types,
            'is_active': self.is_active,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<PriceItem {self.article} "{self.name}">'
