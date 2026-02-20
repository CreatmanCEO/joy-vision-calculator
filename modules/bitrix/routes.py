# modules/bitrix/routes.py
from flask import Blueprint, jsonify, current_app
from models import Order
from extensions import db
from .api import create_deal, update_deal, upload_file_to_bitrix
from modules.pdf.commercial import generate_commercial_pdf
from modules.pdf.specification import generate_specification_pdf
import os

bitrix_bp = Blueprint('bitrix', __name__)


@bitrix_bp.route('/sync/<int:order_id>', methods=['POST'])
def sync_order(order_id):
    """Синхронизация заказа с Битрикс24"""
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'success': False, 'error': 'Заказ не найден'}), 404

    try:
        # Создаём/обновляем сделку
        if order.bitrix_deal_id:
            update_deal(order.bitrix_deal_id, order.total_price)
            action = 'updated'
        else:
            deal_id = create_deal(
                company_name=order.customer_name,
                total_price=order.total_price,
                address=order.city or ""
            )
            order.bitrix_deal_id = deal_id
            db.session.commit()
            action = 'created'

        # Генерируем и загружаем PDF
        exports_dir = current_app.config.get('PDF_EXPORTS_DIR', 'data/exports')
        os.makedirs(exports_dir, exist_ok=True)
        files_uploaded = []

        # Коммерческое предложение
        kp_path = os.path.join(exports_dir, f'KP_{order_id}.pdf')
        generate_commercial_pdf(order, kp_path)
        upload_file_to_bitrix(kp_path)
        files_uploaded.append(f'КП_{order_id}.pdf')

        # Разблюдовка
        spec_path = os.path.join(exports_dir, f'Spec_{order_id}.pdf')
        generate_specification_pdf(order, spec_path)
        upload_file_to_bitrix(spec_path)
        files_uploaded.append(f'Разблюдовка_{order_id}.pdf')

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
