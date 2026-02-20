# API Спецификация

**Проект**: Joy Vision Calculator
**Дата**: 2026-02-20
**Версия API**: 1.0
**Base URL**: `http://localhost:5000/api`

---

## 1. Общие сведения

### 1.1 Формат запросов/ответов
- Content-Type: `application/json`
- Кодировка: UTF-8

### 1.2 Коды ответов

| Код | Описание |
|-----|----------|
| 200 | Успешный запрос |
| 201 | Ресурс создан |
| 400 | Ошибка валидации |
| 404 | Ресурс не найден |
| 500 | Внутренняя ошибка сервера |

### 1.3 Формат ошибки

```json
{
  "success": false,
  "error": "Описание ошибки",
  "details": {}
}
```

---

## 2. Заказы (Orders)

### 2.1 GET /api/orders

Получить список заказов.

**Query Parameters**:
| Параметр | Тип | Описание |
|----------|-----|----------|
| status | string | Фильтр по статусу |
| limit | int | Лимит записей (default: 50) |
| offset | int | Смещение (default: 0) |

**Response 200**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "customer_name": "ООО Рога и Копыта",
      "city": "Москва",
      "status": "draft",
      "total_price": 125000.00,
      "systems_count": 3,
      "created_at": "2026-02-20T10:30:00"
    }
  ],
  "total": 42,
  "limit": 50,
  "offset": 0
}
```

---

### 2.2 POST /api/orders

Создать новый заказ.

**Request Body**:
```json
{
  "customer_name": "ООО Рога и Копыта",
  "city": "Москва",
  "ral_color": "RAL 9016",
  "discount_percent": 5,
  "with_glass": true,
  "with_assembly": false,
  "with_install": true,
  "notes": "Срочный заказ"
}
```

**Response 201**:
```json
{
  "success": true,
  "data": {
    "id": 42,
    "customer_name": "ООО Рога и Копыта",
    "status": "draft",
    "created_at": "2026-02-20T10:30:00"
  }
}
```

---

### 2.3 GET /api/orders/{id}

Получить заказ с системами.

**Response 200**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "bitrix_deal_id": 12345,
    "customer_name": "ООО Рога и Копыта",
    "city": "Москва",
    "ral_color": "RAL 9016",
    "discount_percent": 5,
    "with_glass": true,
    "with_assembly": false,
    "with_install": true,
    "status": "draft",
    "total_price": 125000.00,
    "notes": "Срочный заказ",
    "systems": [
      {
        "position": 1,
        "system_type": "Slider L",
        "width": 3000,
        "height": 2500,
        "panels": 3,
        "opening": "влево",
        "price": 45000.00,
        "calculated_data": {...}
      }
    ],
    "created_at": "2026-02-20T10:30:00",
    "updated_at": "2026-02-20T11:45:00"
  }
}
```

---

### 2.4 PUT /api/orders/{id}

Обновить заказ.

**Request Body**:
```json
{
  "customer_name": "ООО Новое название",
  "discount_percent": 10,
  "status": "confirmed"
}
```

**Response 200**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "customer_name": "ООО Новое название",
    "status": "confirmed",
    "updated_at": "2026-02-20T12:00:00"
  }
}
```

---

### 2.5 DELETE /api/orders/{id}

Удалить заказ.

**Response 200**:
```json
{
  "success": true,
  "message": "Заказ #1 удалён"
}
```

---

## 3. Системы в заказе (Order Systems)

### 3.1 POST /api/orders/{order_id}/systems

Добавить систему в заказ.

**Request Body**:
```json
{
  "system_type": "Slider L",
  "width": 3000,
  "height": 2500,
  "panels": 3,
  "opening": "влево",
  "left_edge": "боковой профиль",
  "right_edge": "боковой профиль",
  "handle_type": "круглая",
  "handle_count": 2,
  "latch_count": 2,
  "glass_thickness": 10,
  "seal_type": "светопрозрачный",
  "handle_height": 1000,
  "painting": false
}
```

**Response 201**:
```json
{
  "success": true,
  "data": {
    "position": 1,
    "system_type": "Slider L",
    "calculated_data": {
      "system_info": {...},
      "profiles": [...],
      "hardware": [...],
      "seals": [...],
      "summary": {...}
    },
    "price": 45000.00
  }
}
```

---

### 3.2 PUT /api/orders/{order_id}/systems/{position}

Обновить систему.

**Request Body**: аналогично POST

**Response 200**: аналогично POST

---

### 3.3 DELETE /api/orders/{order_id}/systems/{position}

Удалить систему из заказа.

**Response 200**:
```json
{
  "success": true,
  "message": "Система на позиции 2 удалена"
}
```

---

## 4. Расчёт (Calculate)

### 4.1 POST /api/calculate

Расчёт комплектующих без сохранения.

**Request Body**:
```json
{
  "system_type": "Slider L",
  "width": 3000,
  "height": 2500,
  "panels": 3,
  "opening": "влево",
  "left_edge": "боковой профиль",
  "right_edge": "боковой профиль",
  "handle_type": "круглая",
  "handle_count": 2,
  "latch_count": 2,
  "glass_thickness": 10,
  "seal_type": "светопрозрачный"
}
```

**Response 200**:
```json
{
  "success": true,
  "data": {
    "system_info": {
      "type": "Slider L",
      "track_type": "3 дорожки",
      "track_count": 3,
      "glass_width_mm": 980.5,
      "glass_height_mm": 2395,
      "glass_weight_kg": 58.7
    },
    "profiles": [
      {
        "code": "S-010",
        "name": "Верхний профиль 3 дорожки",
        "qty": 1,
        "total_m": 3.075,
        "price_per_unit": 1500.00,
        "total_price": 4612.50
      }
    ],
    "hardware": [...],
    "seals": [...],
    "consumables": [...],
    "fasteners": [...],
    "summary": {
      "total_profiles_m": 12.5,
      "total_hardware_items": 24,
      "total_price": 45000.00
    }
  }
}
```

---

## 5. PDF генерация

### 5.1 GET /api/orders/{id}/pdf/kp

Скачать коммерческое предложение.

**Response 200**: `application/pdf`

**Headers**:
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="KP_42.pdf"
```

---

### 5.2 GET /api/orders/{id}/pdf/spec

Скачать разблюдовку (комплектацию для склада).

**Query Parameters**:
| Параметр | Тип | Описание |
|----------|-----|----------|
| works | string | Доп. работы через запятую |

**Example**: `/api/orders/42/pdf/spec?works=склейка,монтаж`

**Response 200**: `application/pdf`

---

## 6. Цены (Prices)

### 6.1 GET /api/prices

Получить прайс-лист.

**Query Parameters**:
| Параметр | Тип | Описание |
|----------|-----|----------|
| category | string | Фильтр по категории |
| search | string | Поиск по названию/артикулу |

**Response 200**:
```json
{
  "success": true,
  "data": [
    {
      "article": "S-010",
      "name": "Верхний профиль 3 дорожки",
      "unit": "п.м.",
      "price": 1500.00,
      "category": "Профили",
      "updated_at": "2026-02-20"
    }
  ]
}
```

---

### 6.2 PUT /api/prices/{article}

Обновить цену.

**Request Body**:
```json
{
  "price": 1650.00
}
```

**Response 200**:
```json
{
  "success": true,
  "data": {
    "article": "S-010",
    "price": 1650.00,
    "updated_at": "2026-02-20T14:00:00"
  }
}
```

---

### 6.3 POST /api/prices/import

Импорт цен из Excel.

**Request**: `multipart/form-data`

| Поле | Тип | Описание |
|------|-----|----------|
| file | file | Excel файл (.xlsx, .xlsm) |

**Response 200**:
```json
{
  "success": true,
  "message": "Импортировано 156 позиций",
  "updated": 142,
  "created": 14,
  "errors": []
}
```

---

## 7. Битрикс интеграция

### 7.1 POST /api/bitrix/sync/{order_id}

Синхронизировать заказ с Битрикс24.

**Response 200**:
```json
{
  "success": true,
  "data": {
    "bitrix_deal_id": 12345,
    "action": "created",
    "files_uploaded": ["KP_42.pdf", "Spec_42.pdf"]
  }
}
```

---

### 7.2 GET /api/bitrix/deal/{deal_id}

Получить данные сделки из Битрикс.

**Response 200**:
```json
{
  "success": true,
  "data": {
    "deal_id": 12345,
    "title": "Заказ #42",
    "company": "ООО Рога и Копыта",
    "stage": "C0:NEW",
    "opportunity": 125000.00
  }
}
```

---

## 8. Веб-страницы (HTML)

| URL | Описание |
|-----|----------|
| `/` | Главная страница / список заказов |
| `/order/new` | Форма нового заказа |
| `/order/<id>` | Просмотр/редактирование заказа |
| `/order/<id>/system/new` | Добавление системы |
| `/prices` | Управление ценами |
| `/settings` | Настройки (Битрикс, и т.д.) |
