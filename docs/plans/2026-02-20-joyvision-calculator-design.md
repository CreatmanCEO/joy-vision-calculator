# Дизайн-документ: Joy Vision Calculator

**Дата**: 2026-02-20
**Версия**: 1.0
**Статус**: Утверждён

---

## 1. Обзор проекта

### 1.1 Цель
Создать веб-приложение для расчёта комплектующих систем безрамного остекления с возможностью:
- Расчёта 4 типов систем (Slider L/X, JV Line, Zig-Zag)
- Управления заказами с несколькими системами
- Генерации PDF (КП и разблюдовка)
- Управления ценами
- Интеграции с Битрикс24

### 1.2 Стейкхолдеры
- **Пользователи**: Менеджеры по продажам (1-3 человека)
- **Заказчик**: Joy Vision

### 1.3 Технологический стек
| Компонент | Технология |
|-----------|------------|
| Backend | Python 3.10+, Flask 3.x |
| ORM | SQLAlchemy 2.x |
| БД (dev) | SQLite + WAL |
| БД (prod) | PostgreSQL 15+ |
| Frontend | Jinja2, Bootstrap 5, HTMX |
| PDF | ReportLab |
| Деплой | Gunicorn + Nginx (VPS) |

---

## 2. Архитектура

### 2.1 Структура проекта

```
C:\Hans\app\
├── app.py                      # Точка входа
├── config.py                   # Конфигурация
├── requirements.txt
├── models/
│   ├── __init__.py
│   ├── order.py
│   ├── system.py
│   └── price.py
├── modules/
│   ├── calculator/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── slider_l.py
│   │   ├── slider_x.py
│   │   ├── line.py
│   │   └── zigzag.py
│   ├── orders/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── service.py
│   ├── pdf/
│   │   ├── __init__.py
│   │   ├── commercial.py
│   │   └── specification.py
│   ├── pricing/
│   │   ├── __init__.py
│   │   └── routes.py
│   └── bitrix/
│       ├── __init__.py
│       └── api.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── order/
│   │   ├── list.html
│   │   ├── detail.html
│   │   └── system_form.html
│   └── prices/
│       └── list.html
├── static/
│   ├── css/
│   └── js/
├── data/
│   ├── joyvision.db
│   └── exports/
└── docs/
```

### 2.2 Модули и зависимости

```
┌──────────────────────────────────────────────────────┐
│                      Flask App                        │
│  ┌────────────┬────────────┬────────────┬──────────┐ │
│  │   orders   │  pricing   │    pdf     │  bitrix  │ │
│  │   routes   │  routes    │  generator │   api    │ │
│  └─────┬──────┴─────┬──────┴─────┬──────┴────┬─────┘ │
│        │            │            │           │        │
│        ▼            ▼            │           │        │
│  ┌─────────────────────────┐    │           │        │
│  │      calculator         │◄───┘           │        │
│  │  (slider, line, zigzag) │                │        │
│  └─────────────────────────┘                │        │
│        │                                    │        │
│        ▼                                    ▼        │
│  ┌─────────────────────────────────────────────────┐ │
│  │              SQLAlchemy Models                  │ │
│  │         (Order, OrderSystem, PriceItem)         │ │
│  └─────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │   SQLite / PG    │
              └──────────────────┘
```

---

## 3. Модель данных

### 3.1 Сущности

**Order** (Заказ):
- id, bitrix_deal_id
- customer_name, city, ral_color
- discount_percent
- with_glass, with_assembly, with_install
- status, total_price
- created_at, updated_at

**OrderSystem** (Система в заказе):
- id, order_id, position
- system_type, width, height, panels
- opening, left_edge, right_edge
- handle_type, handle_count, latch_count
- glass_thickness, seal_type, handle_height
- floor_lock, closer, painting
- calculated_data (JSON)
- price

**PriceItem** (Позиция прайса):
- id, article, name, unit
- price, category
- is_active, updated_at

### 3.2 Связи
- Order 1:N OrderSystem

---

## 4. API

### 4.1 REST эндпоинты

| Метод | URL | Описание |
|-------|-----|----------|
| GET | /api/orders | Список заказов |
| POST | /api/orders | Создать заказ |
| GET | /api/orders/{id} | Получить заказ |
| PUT | /api/orders/{id} | Обновить заказ |
| DELETE | /api/orders/{id} | Удалить заказ |
| POST | /api/orders/{id}/systems | Добавить систему |
| PUT | /api/orders/{id}/systems/{pos} | Обновить систему |
| DELETE | /api/orders/{id}/systems/{pos} | Удалить систему |
| POST | /api/calculate | Расчёт без сохранения |
| GET | /api/orders/{id}/pdf/kp | PDF КП |
| GET | /api/orders/{id}/pdf/spec | PDF разблюдовка |
| GET | /api/prices | Прайс-лист |
| PUT | /api/prices/{article} | Обновить цену |
| POST | /api/prices/import | Импорт из Excel |
| POST | /api/bitrix/sync/{id} | Синхронизация |

### 4.2 Формат ответов
```json
{
  "success": true,
  "data": {...},
  "error": null
}
```

---

## 5. Пользовательский интерфейс

### 5.1 Страницы

1. **Главная** `/`
   - Таблица заказов
   - Фильтры по статусу
   - Кнопка "Новый заказ"

2. **Заказ** `/order/{id}`
   - Шапка: заказчик, город, цвет
   - Таблица систем
   - Кнопки: добавить систему, скачать PDF

3. **Форма системы** `/order/{id}/system/new`
   - Выбор типа системы
   - Ввод параметров
   - Предпросмотр расчёта
   - Кнопка "Добавить"

4. **Цены** `/prices`
   - Таблица прайса
   - Редактирование inline
   - Импорт из Excel

### 5.2 UI Framework
- Bootstrap 5 (responsive)
- HTMX (динамическое обновление без SPA)
- Без React/Vue (простота)

---

## 6. Генерация PDF

### 6.1 Коммерческое предложение (КП)
- Логотип Joy Vision
- Реквизиты компании
- Данные заказчика
- Таблица систем (тип, размер, цена)
- Итого со скидкой
- Условия оплаты
- Срок действия КП

### 6.2 Разблюдовка (Комплектация)
Адаптация из `reader_0.2.py`:
- Шапка: номер заказа, цвет RAL, дата
- Дополнительные работы (чекбоксы)
- Таблица комплектующих по блокам:
  - Профили
  - Фурнитура
  - Уплотнители
  - Прочее
- Колонки: наименование, ед.изм., системы 1..N, итого
- Плитки с параметрами систем

---

## 7. Интеграция с Битрикс24

### 7.1 Функции
- Создание сделки (`crm.deal.add`)
- Обновление суммы сделки (`crm.deal.update`)
- Загрузка PDF на диск (`disk.folder.uploadfile`)

### 7.2 Ограничения
- Чтение JSON из сделки нестабильно
- Решение: хранить данные в локальной БД, в Битрикс только ID и сумму

---

## 8. Безопасность

### 8.1 Фаза 1 (MVP)
- Базовая HTTP Basic Auth (опционально)
- CORS для localhost

### 8.2 Фаза 2 (Продакшн)
- Авторизация Flask-Login
- HTTPS (Let's Encrypt)
- Защита от CSRF

---

## 9. Развёртывание

### 9.1 Разработка (Локально)
```bash
cd C:\Hans\app
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
# → http://localhost:5000
```

### 9.2 Продакшн (VPS)
```bash
# Gunicorn + Nginx
gunicorn -w 4 -b 127.0.0.1:8000 app:app

# Nginx reverse proxy
# PostgreSQL вместо SQLite
```

---

## 10. План реализации

| Фаза | Задачи | Срок |
|------|--------|------|
| **1. MVP** | Структура, модели, калькулятор, базовый UI | 2-3 нед |
| **2. PDF** | Генерация КП и разблюдовки | 1-2 нед |
| **3. Цены** | CRUD прайса, импорт Excel | 1 нед |
| **4. Битрикс** | Синхронизация сделок | 1 нед |
| **5. Продакшн** | PostgreSQL, VPS, авторизация | 1 нед |

---

## 11. Переиспользуемый код

| Источник | Назначение | Изменения |
|----------|------------|-----------|
| `calculator.py` | `modules/calculator/` | Разбить на модули |
| `reader_0.2.py` | `modules/pdf/specification.py` | Адаптировать под Flask |
| `old/core/bitrix_api.py` | `modules/bitrix/api.py` | Убрать tkinter |

---

## 12. Согласование

| Роль | Дата | Статус |
|------|------|--------|
| Заказчик | 2026-02-20 | Утверждено |
