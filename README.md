# Joy Vision Calculator

Веб-приложение для расчёта комплектующих систем безрамного остекления.

## Возможности

- Расчёт 4 типов систем: Slider L, Slider X, JV Line, JV Zig-Zag
- Управление заказами с несколькими системами
- Генерация PDF: коммерческое предложение и комплектация
- Управление ценами (прайс-лист)
- Интеграция с Битрикс24

## Требования

- Python 3.10+
- SQLite (разработка) / PostgreSQL (продакшн)

## Быстрый старт

```bash
# Клонирование
cd C:\Hans\app

# Виртуальное окружение
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Зависимости
pip install -r requirements.txt

# Запуск
python app.py
```

Приложение доступно по адресу: http://localhost:5000

## Структура проекта

```
app/
├── app.py              # Точка входа
├── config.py           # Конфигурация
├── models/             # SQLAlchemy модели
├── modules/
│   ├── calculator/     # Расчёт комплектующих
│   ├── orders/         # Управление заказами
│   ├── pdf/            # Генерация PDF
│   ├── pricing/        # Управление ценами
│   └── bitrix/         # Интеграция с Битрикс24
├── templates/          # HTML шаблоны
├── static/             # CSS, JS
├── data/               # БД и файлы
└── docs/               # Документация
```

## Документация

- [AS-IS / TO-BE](docs/01-AS-IS-TO-BE.md) — анализ текущего состояния
- [Модель данных](docs/specs/02-DATA-MODEL.md) — структура БД
- [API спецификация](docs/api/03-API-SPEC.md) — REST API
- [Дизайн-документ](docs/plans/2026-02-20-joyvision-calculator-design.md) — архитектура

## Конфигурация

Переменные окружения (или config.py):

```
DATABASE_URL=sqlite:///data/joyvision.db
BITRIX_WEBHOOK_URL=https://joyvision.bitrix24.ru/rest/1/xxxxx/
SECRET_KEY=your-secret-key
```

## Разработка

```bash
# Запуск в режиме отладки
FLASK_DEBUG=1 python app.py

# Тесты
pytest tests/
```

## Лицензия

Проприетарное ПО. Joy Vision © 2026
