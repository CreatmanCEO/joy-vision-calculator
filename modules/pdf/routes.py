# modules/pdf/routes.py
from flask import Blueprint, send_file, jsonify, current_app
from models import Order
from .specification import generate_specification_pdf
import os

pdf_bp = Blueprint('pdf', __name__)

@pdf_bp.route('/orders/<int:order_id>/pdf/spec', methods=['GET'])
def download_specification(order_id):
    """Скачать разблюдовку (спецификацию комплектующих) для заказа"""
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'success': False, 'error': 'Заказ не найден'}), 404

    # Путь для сохранения PDF
    output_dir = current_app.config.get('PDF_EXPORTS_DIR', 'data/exports')
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, f'Spec_{order_id}.pdf')

    try:
        generate_specification_pdf(order, output_path)
    except Exception as e:
        return jsonify({'success': False, 'error': f'Ошибка генерации PDF: {str(e)}'}), 500

    return send_file(
        output_path,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'Разблюдовка_{order_id}.pdf'
    )
