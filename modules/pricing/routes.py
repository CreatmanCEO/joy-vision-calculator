# modules/pricing/routes.py
"""
API эндпоинты для работы с ценами
"""

from flask import Blueprint, request, jsonify
from extensions import db
from models.price import PriceItem
import pandas as pd
from io import BytesIO

pricing_bp = Blueprint('pricing', __name__)


@pricing_bp.route('/prices', methods=['GET'])
def list_prices():
    """Получить прайс-лист"""
    category = request.args.get('category')
    search = request.args.get('search')
    active_only = request.args.get('active', 'true').lower() == 'true'

    query = PriceItem.query

    if active_only:
        query = query.filter(PriceItem.is_active == True)

    if category:
        query = query.filter(PriceItem.category == category)

    if search:
        search_term = f'%{search}%'
        query = query.filter(
            db.or_(
                PriceItem.article.ilike(search_term),
                PriceItem.name.ilike(search_term)
            )
        )

    items = query.order_by(PriceItem.category, PriceItem.article).all()

    return jsonify({
        'success': True,
        'data': [item.to_dict() for item in items]
    })


@pricing_bp.route('/prices', methods=['POST'])
def create_price():
    """Добавить позицию в прайс"""
    data = request.get_json()

    required = ['article', 'name', 'category']
    for field in required:
        if not data.get(field):
            return jsonify({'success': False, 'error': f'{field} обязателен'}), 400

    # Проверка уникальности артикула
    existing = PriceItem.query.filter_by(article=data['article']).first()
    if existing:
        return jsonify({'success': False, 'error': 'Артикул уже существует'}), 400

    item = PriceItem(
        article=data['article'],
        name=data['name'],
        unit=data.get('unit', 'шт'),
        price=data.get('price', 0),
        category=data['category'],
        system_types=data.get('system_types')
    )

    db.session.add(item)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': item.to_dict()
    }), 201


@pricing_bp.route('/prices/<article>', methods=['PUT'])
def update_price(article):
    """Обновить цену по артикулу"""
    item = PriceItem.query.filter_by(article=article).first()

    if not item:
        return jsonify({'success': False, 'error': 'Артикул не найден'}), 404

    data = request.get_json()

    for field in ['name', 'unit', 'price', 'category', 'system_types', 'is_active']:
        if field in data:
            setattr(item, field, data[field])

    db.session.commit()

    return jsonify({
        'success': True,
        'data': item.to_dict()
    })


@pricing_bp.route('/prices/<article>', methods=['DELETE'])
def delete_price(article):
    """Деактивировать позицию прайса"""
    item = PriceItem.query.filter_by(article=article).first()

    if not item:
        return jsonify({'success': False, 'error': 'Артикул не найден'}), 404

    # Мягкое удаление
    item.is_active = False
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Артикул {article} деактивирован'
    })


@pricing_bp.route('/prices/import', methods=['POST'])
def import_prices():
    """Импорт цен из Excel"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'Файл не передан'}), 400

    file = request.files['file']

    if not file.filename.endswith(('.xlsx', '.xlsm')):
        return jsonify({'success': False, 'error': 'Только .xlsx/.xlsm файлы'}), 400

    try:
        # Читаем Excel файл
        df = pd.read_excel(BytesIO(file.read()))

        # Ожидаем колонки: Артикул, Наименование, Ед.изм., Цена, Категория
        required_cols = ['Артикул', 'Наименование', 'Цена', 'Категория']
        if not all(col in df.columns for col in required_cols):
            return jsonify({
                'success': False,
                'error': f'Нужны колонки: {", ".join(required_cols)}'
            }), 400

        created = 0
        updated = 0
        errors = []

        for idx, row in df.iterrows():
            article = str(row['Артикул']).strip()
            if not article or article == 'nan':
                continue

            try:
                item = PriceItem.query.filter_by(article=article).first()

                if item:
                    # Обновляем существующую позицию
                    item.name = row['Наименование']
                    item.price = float(row['Цена'])
                    item.category = row['Категория']
                    item.unit = row.get('Ед.изм.', 'шт')
                    updated += 1
                else:
                    # Создаём новую позицию
                    item = PriceItem(
                        article=article,
                        name=row['Наименование'],
                        price=float(row['Цена']),
                        category=row['Категория'],
                        unit=row.get('Ед.изм.', 'шт')
                    )
                    db.session.add(item)
                    created += 1

            except Exception as e:
                errors.append(f'Строка {idx + 2}: {str(e)}')

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


@pricing_bp.route('/prices/categories', methods=['GET'])
def list_categories():
    """Получить список категорий"""
    categories = db.session.query(PriceItem.category).distinct().all()
    return jsonify({
        'success': True,
        'data': [c[0] for c in categories]
    })
