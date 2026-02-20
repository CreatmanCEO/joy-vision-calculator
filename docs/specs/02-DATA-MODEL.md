# Спецификация модели данных

**Проект**: Hans Calculator
**Дата**: 2026-02-20
**Версия**: 1.0

---

## 1. ER-диаграмма

```
┌─────────────────┐       ┌─────────────────────┐       ┌─────────────────┐
│     Order       │       │    OrderSystem      │       │    PriceItem    │
├─────────────────┤       ├─────────────────────┤       ├─────────────────┤
│ id (PK)         │──┐    │ id (PK)             │       │ id (PK)         │
│ bitrix_deal_id  │  │    │ order_id (FK)       │◄──────│ article (UQ)    │
│ customer_name   │  └───►│ position            │       │ name            │
│ city            │       │ system_type         │       │ unit            │
│ ral_color       │       │ width               │       │ price           │
│ discount_percent│       │ height              │       │ category        │
│ with_glass      │       │ panels              │       │ updated_at      │
│ with_assembly   │       │ opening             │       └─────────────────┘
│ with_install    │       │ left_edge           │
│ status          │       │ right_edge          │
│ total_price     │       │ handle_type         │
│ created_at      │       │ handle_count        │
│ updated_at      │       │ latch_count         │
│                 │       │ glass_thickness     │
│                 │       │ seal_type           │
│                 │       │ handle_height       │
│                 │       │ floor_lock          │
│                 │       │ closer              │
│                 │       │ painting            │
│                 │       │ ral_color           │
│                 │       │ calculated_data(JSON)│
│                 │       │ price               │
│                 │       │ created_at          │
└─────────────────┘       └─────────────────────┘
```

---

## 2. Таблица: orders

| Поле | Тип | Nullable | Default | Описание |
|------|-----|----------|---------|----------|
| id | INTEGER | NO | AUTO | Первичный ключ |
| bitrix_deal_id | INTEGER | YES | NULL | ID сделки в Битрикс24 |
| customer_name | VARCHAR(255) | NO | | Название заказчика |
| city | VARCHAR(100) | YES | NULL | Город доставки |
| ral_color | VARCHAR(50) | YES | 'RAL 9016' | Цвет покраски по RAL |
| discount_percent | DECIMAL(5,2) | NO | 0 | Скидка в процентах |
| with_glass | BOOLEAN | NO | TRUE | Заказ со стеклом |
| with_assembly | BOOLEAN | NO | FALSE | Заказ со сборкой |
| with_install | BOOLEAN | NO | FALSE | Заказ с монтажом |
| status | VARCHAR(20) | NO | 'draft' | Статус заказа |
| total_price | DECIMAL(12,2) | NO | 0 | Итоговая сумма |
| notes | TEXT | YES | NULL | Примечания |
| created_at | TIMESTAMP | NO | NOW() | Дата создания |
| updated_at | TIMESTAMP | NO | NOW() | Дата обновления |

**Индексы**:
- PRIMARY KEY (id)
- INDEX idx_orders_bitrix (bitrix_deal_id)
- INDEX idx_orders_status (status)
- INDEX idx_orders_created (created_at)

**Статусы заказа**:
- `draft` — черновик
- `confirmed` — подтверждён
- `in_production` — в производстве
- `completed` — выполнен
- `cancelled` — отменён

---

## 3. Таблица: order_systems

| Поле | Тип | Nullable | Default | Описание |
|------|-----|----------|---------|----------|
| id | INTEGER | NO | AUTO | Первичный ключ |
| order_id | INTEGER | NO | | FK → orders.id |
| position | INTEGER | NO | | Позиция в заказе (1, 2, 3...) |
| system_type | VARCHAR(50) | NO | | Тип системы |
| width | INTEGER | NO | | Ширина проёма, мм |
| height | INTEGER | NO | | Высота проёма, мм |
| panels | DECIMAL(3,1) | NO | | Кол-во створок |
| opening | VARCHAR(20) | NO | 'влево' | Направление открывания |
| left_edge | VARCHAR(50) | NO | 'боковой профиль' | Тип левого края |
| right_edge | VARCHAR(50) | NO | 'боковой профиль' | Тип правого края |
| handle_type | VARCHAR(30) | YES | 'круглая' | Тип ручки |
| handle_count | INTEGER | YES | 2 | Количество ручек |
| latch_count | INTEGER | YES | 2 | Количество защёлок |
| glass_thickness | INTEGER | YES | 10 | Толщина стекла, мм |
| seal_type | VARCHAR(30) | YES | 'светопрозрачный' | Тип уплотнителя |
| handle_height | INTEGER | YES | 1000 | Высота ручки от пола, мм |
| floor_lock | BOOLEAN | NO | FALSE | Замок в пол |
| closer | BOOLEAN | NO | FALSE | Напольный доводчик |
| painting | BOOLEAN | NO | FALSE | Требуется покраска |
| custom_ral_color | VARCHAR(50) | YES | NULL | Индивидуальный цвет |
| calculated_data | JSON | YES | NULL | Результат расчёта |
| price | DECIMAL(12,2) | NO | 0 | Стоимость системы |
| created_at | TIMESTAMP | NO | NOW() | Дата создания |

**Индексы**:
- PRIMARY KEY (id)
- FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
- INDEX idx_systems_order (order_id)
- UNIQUE INDEX idx_systems_position (order_id, position)

**Типы систем** (system_type):
- `Slider L`
- `Slider X`
- `JV Line`
- `JV Zig-Zag`

**Направления открывания** (opening):
- `влево`
- `вправо`
- `от центра`

---

## 4. Таблица: price_items

| Поле | Тип | Nullable | Default | Описание |
|------|-----|----------|---------|----------|
| id | INTEGER | NO | AUTO | Первичный ключ |
| article | VARCHAR(30) | NO | | Артикул (уникальный) |
| name | VARCHAR(255) | NO | | Наименование |
| unit | VARCHAR(20) | NO | 'шт' | Единица измерения |
| price | DECIMAL(10,2) | NO | 0 | Цена за единицу |
| category | VARCHAR(50) | NO | | Категория |
| system_types | JSON | YES | NULL | Для каких систем применимо |
| is_active | BOOLEAN | NO | TRUE | Активен ли артикул |
| updated_at | TIMESTAMP | NO | NOW() | Дата обновления |

**Индексы**:
- PRIMARY KEY (id)
- UNIQUE INDEX idx_price_article (article)
- INDEX idx_price_category (category)
- INDEX idx_price_active (is_active)

**Категории** (category):
- `Профили`
- `Фурнитура`
- `Уплотнители`
- `Прочее`

---

## 5. Структура calculated_data (JSON)

```json
{
  "system_info": {
    "type": "Slider L",
    "track_type": "3 дорожки",
    "track_count": 3,
    "opening": "влево",
    "panels": 3,
    "width_mm": 3000,
    "height_mm": 2500,
    "glass_width_mm": 980.5,
    "glass_height_mm": 2395,
    "glass_weight_kg": 58.7
  },
  "profiles": [
    {
      "code": "S-010",
      "name": "Верхний профиль 3 дорожки",
      "length_per_piece_mm": 3000,
      "total_with_waste_mm": 3075,
      "qty": 1,
      "total_m": 3.075
    }
  ],
  "hardware": [
    {
      "code": "SL-140-0",
      "name": "Заглушка боковая",
      "qty": 2
    }
  ],
  "seals": [
    {
      "code": "AA-030",
      "name": "Уплотнитель щеточный 5х4",
      "total_m": 18.0
    }
  ],
  "consumables": [...],
  "fasteners": [...],
  "summary": {
    "total_profiles_m": 12.5,
    "total_hardware_items": 24,
    "glue_info": "Клей: 1 туб, Активатор: 1 банок"
  }
}
```

---

## 6. Миграции

### 6.1 Создание таблиц (SQLite)

```sql
-- 001_create_orders.sql
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bitrix_deal_id INTEGER,
    customer_name VARCHAR(255) NOT NULL,
    city VARCHAR(100),
    ral_color VARCHAR(50) DEFAULT 'RAL 9016',
    discount_percent DECIMAL(5,2) DEFAULT 0,
    with_glass BOOLEAN DEFAULT 1,
    with_assembly BOOLEAN DEFAULT 0,
    with_install BOOLEAN DEFAULT 0,
    status VARCHAR(20) DEFAULT 'draft',
    total_price DECIMAL(12,2) DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_orders_bitrix ON orders(bitrix_deal_id);
CREATE INDEX idx_orders_status ON orders(status);

-- 002_create_order_systems.sql
CREATE TABLE order_systems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    system_type VARCHAR(50) NOT NULL,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    panels DECIMAL(3,1) NOT NULL,
    opening VARCHAR(20) DEFAULT 'влево',
    left_edge VARCHAR(50) DEFAULT 'боковой профиль',
    right_edge VARCHAR(50) DEFAULT 'боковой профиль',
    handle_type VARCHAR(30) DEFAULT 'круглая',
    handle_count INTEGER DEFAULT 2,
    latch_count INTEGER DEFAULT 2,
    glass_thickness INTEGER DEFAULT 10,
    seal_type VARCHAR(30) DEFAULT 'светопрозрачный',
    handle_height INTEGER DEFAULT 1000,
    floor_lock BOOLEAN DEFAULT 0,
    closer BOOLEAN DEFAULT 0,
    painting BOOLEAN DEFAULT 0,
    custom_ral_color VARCHAR(50),
    calculated_data TEXT,
    price DECIMAL(12,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
);

CREATE INDEX idx_systems_order ON order_systems(order_id);
CREATE UNIQUE INDEX idx_systems_position ON order_systems(order_id, position);

-- 003_create_price_items.sql
CREATE TABLE price_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article VARCHAR(30) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    unit VARCHAR(20) DEFAULT 'шт',
    price DECIMAL(10,2) DEFAULT 0,
    category VARCHAR(50) NOT NULL,
    system_types TEXT,
    is_active BOOLEAN DEFAULT 1,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_price_category ON price_items(category);
```

---

## 7. Совместимость SQLite ↔ PostgreSQL

| Особенность | SQLite | PostgreSQL | Решение |
|-------------|--------|------------|---------|
| JSON | TEXT + json.loads | JSONB | SQLAlchemy JSON type |
| AUTO_INCREMENT | AUTOINCREMENT | SERIAL | SQLAlchemy Integer + autoincrement |
| BOOLEAN | 0/1 | true/false | SQLAlchemy Boolean |
| TIMESTAMP | TEXT | TIMESTAMP | SQLAlchemy DateTime |

SQLAlchemy абстрагирует эти различия, миграция будет бесшовной.
