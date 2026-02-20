# app.py
"""
Joy Vision Calculator - Веб-приложение для расчёта комплектующих
"""

from flask import Flask, render_template, jsonify
from extensions import db
from config import get_config


def create_app(config_class=None):
    """Фабрика приложения Flask"""

    app = Flask(__name__)

    # Загрузка конфигурации
    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)

    # Инициализация БД
    db.init_app(app)

    # Регистрация blueprints
    from modules.orders.routes import orders_bp
    from modules.pricing.routes import pricing_bp
    from modules.pdf.routes import pdf_bp
    from modules.bitrix.routes import bitrix_bp

    app.register_blueprint(orders_bp, url_prefix='/api')
    app.register_blueprint(pricing_bp, url_prefix='/api')
    app.register_blueprint(pdf_bp, url_prefix='/api')
    app.register_blueprint(bitrix_bp, url_prefix='/api/bitrix')

    # Создание таблиц БД
    with app.app_context():
        from models import Order, OrderSystem, PriceItem
        db.create_all()

    # ========== HTML СТРАНИЦЫ ==========

    # Главная страница - список заказов
    @app.route('/')
    @app.route('/orders')
    def index():
        return render_template('index.html')

    # Создание нового заказа
    @app.route('/orders/new')
    def new_order():
        return render_template('orders/new.html')

    # Детали заказа
    @app.route('/order/<int:order_id>')
    def order_detail(order_id):
        return render_template('orders/detail.html', order_id=order_id)

    # Управление ценами
    @app.route('/prices')
    def prices_list():
        return render_template('prices/list.html')

    # Импорт цен
    @app.route('/prices/import')
    def prices_import():
        return render_template('prices/import.html')

    # Страница тестирования
    @app.route('/test')
    def test_page():
        return render_template('test.html')

    # Healthcheck
    @app.route('/health')
    def health():
        return jsonify({'status': 'ok', 'app': 'Joy Vision Calculator'})

    # Обработка ошибок
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'success': False, 'error': 'Not found'}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

    return app


# Точка входа для разработки
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
