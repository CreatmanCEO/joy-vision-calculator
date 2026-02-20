# 🌐 Интеграция сайта Tilda с Joy Vision Calculator

Подробная инструкция по подключению вашего сайта на Tilda к API калькулятора.

## 📋 Содержание

1. [Обзор интеграции](#1-обзор-интеграции)
2. [Подготовка API](#2-подготовка-api)
3. [Настройка формы на Tilda](#3-настройка-формы-на-tilda)
4. [JavaScript код для интеграции](#4-javascript-код-для-интеграции)
5. [Обработка ответа](#5-обработка-ответа)
6. [Готовые примеры форм](#6-готовые-примеры-форм)
7. [Отладка и тестирование](#7-отладка-и-тестирование)

---

## 1. Обзор интеграции

### Схема работы:

```
Tilda сайт → Форма расчёта → API калькулятора → Результат → PDF → Email
```

### Возможности:

- ✅ Форма расчёта стоимости прямо на сайте
- ✅ Мгновенный расчёт без перезагрузки страницы
- ✅ Автоматическая генерация PDF
- ✅ Отправка результата на email
- ✅ Сохранение заказа в CRM Битрикс24

---

## 2. Подготовка API

### Шаг 1: Убедитесь что API доступно извне

Ваш API должен быть доступен по публичному адресу:

**Вариант A: Локальный сервер (для разработки)**
- Используйте ngrok для создания публичного URL:
  ```bash
  ngrok http 5000
  ```
- Получите URL вида: `https://abcd1234.ngrok.io`

**Вариант B: VPS сервер (для продакшена)**
- API уже доступно по адресу: `https://ваш-домен.ru`

### Шаг 2: Настройте CORS

Чтобы Tilda мог делать запросы к API, добавьте CORS:

Откройте файл `app.py` и добавьте:

```python
from flask_cors import CORS

def create_app(config_class=None):
    app = Flask(__name__)

    # ... существующий код ...

    # Добавьте CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "https://ваш-сайт.tilda.ws",
                "https://ваш-домен.ru"
            ],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type"]
        }
    })

    # ... остальной код ...
```

Установите flask-cors:
```bash
pip install flask-cors
```

Добавьте в `requirements.txt`:
```
flask-cors>=4.0.0
```

---

## 3. Настройка формы на Tilda

### Шаг 1: Создайте блок с формой

1. Войдите в редактор Tilda
2. Добавьте блок **"Форма"** (T123, T170 или любой другой)
3. Настройте поля формы:

#### Обязательные поля:

- **Имя/Компания** (input name="customer_name")
- **Email** (input name="email")
- **Телефон** (input name="phone")
- **Город** (input name="city")
- **Тип системы** (select name="system_type")
  - Slider L
  - Slider X
  - JV Line
  - JV Zig-Zag
- **Ширина проёма, мм** (input name="width" type="number")
- **Высота проёма, мм** (input name="height" type="number")
- **Количество створок** (input name="panels" type="number")

#### Дополнительные поля (опционально):

- **Направление открывания** (select name="opening")
  - влево
  - вправо
  - от центра
- **Скидка, %** (input name="discount_percent" type="number")
- **Комментарий** (textarea name="notes")

### Шаг 2: Добавьте ID полям

Для каждого поля формы добавьте уникальный ID через настройки поля:

- `customer_name` → id="customer_name"
- `email` → id="email"
- `width` → id="width"
- и т.д.

---

## 4. JavaScript код для интеграции

### Добавление кода на страницу Tilda:

1. В редакторе Tilda откройте **Настройки страницы**
2. Перейдите на вкладку **"Дополнительно"**
3. В поле **"HTML-код для вставки внутри <head>"** добавьте:

```html
<script>
// Конфигурация
const API_URL = 'https://ваш-домен.ru/api'; // Замените на ваш URL API

// Функция отправки формы
async function submitCalculatorForm(event) {
    event.preventDefault();

    // Показать индикатор загрузки
    const submitBtn = document.querySelector('#calc-form button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Расчёт...';
    submitBtn.disabled = true;

    try {
        // Собрать данные формы
        const formData = {
            customer_name: document.getElementById('customer_name').value,
            email: document.getElementById('email').value,
            phone: document.getElementById('phone').value || '',
            city: document.getElementById('city').value || '',
            discount_percent: parseFloat(document.getElementById('discount_percent')?.value || 0),
            notes: document.getElementById('notes')?.value || ''
        };

        // Создать заказ
        const orderResponse = await fetch(`${API_URL}/orders`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        if (!orderResponse.ok) {
            throw new Error('Ошибка создания заказа');
        }

        const orderData = await orderResponse.json();
        const orderId = orderData.data.id;

        // Добавить систему к заказу
        const systemData = {
            system_type: document.getElementById('system_type').value,
            width: parseInt(document.getElementById('width').value),
            height: parseInt(document.getElementById('height').value),
            panels: parseFloat(document.getElementById('panels').value),
            opening: document.getElementById('opening')?.value || 'влево'
        };

        const systemResponse = await fetch(`${API_URL}/orders/${orderId}/systems`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(systemData)
        });

        if (!systemResponse.ok) {
            throw new Error('Ошибка расчёта системы');
        }

        const systemResult = await systemResponse.json();

        // Получить полные данные заказа с итоговой суммой
        const finalOrderResponse = await fetch(`${API_URL}/orders/${orderId}`);
        const finalOrder = await finalOrderResponse.json();

        // Показать результат
        displayResult(finalOrder.data);

        // Опционально: отправить в Битрикс24
        // await syncToBitrix(orderId);

    } catch (error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при расчёте. Пожалуйста, попробуйте ещё раз.');
    } finally {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }
}

// Функция отображения результата
function displayResult(order) {
    const resultHtml = `
        <div class="calculator-result">
            <h3>✅ Расчёт выполнен!</h3>
            <p><strong>Номер заказа:</strong> ${order.id}</p>
            <p><strong>Компания:</strong> ${order.customer_name}</p>
            <p><strong>Количество систем:</strong> ${order.systems_count}</p>
            <p><strong>Итоговая стоимость:</strong> ${order.total_price.toLocaleString('ru-RU')} ₽</p>
            <p>Коммерческое предложение и разблюдовка отправлены на ${order.email || 'вашу почту'}</p>
            <div style="margin-top: 20px;">
                <a href="${API_URL}/orders/${order.id}/pdf/kp"
                   class="t-btn"
                   download="КП_${order.id}.pdf">
                   📄 Скачать КП (PDF)
                </a>
                <a href="${API_URL}/orders/${order.id}/pdf/spec"
                   class="t-btn"
                   download="Разблюдовка_${order.id}.pdf"
                   style="margin-left: 10px;">
                   📋 Скачать разблюдовку (PDF)
                </a>
            </div>
        </div>
    `;

    // Показать результат в модальном окне или специальном блоке
    const resultContainer = document.getElementById('calculator-result');
    if (resultContainer) {
        resultContainer.innerHTML = resultHtml;
        resultContainer.style.display = 'block';
    } else {
        // Если нет специального контейнера, показать alert
        alert(`Расчёт выполнен! Итого: ${order.total_price.toLocaleString('ru-RU')} ₽`);
    }
}

// Опционально: синхронизация с Битрикс24
async function syncToBitrix(orderId) {
    try {
        await fetch(`${API_URL}/bitrix/sync/${orderId}`, {
            method: 'POST'
        });
        console.log('Заказ синхронизирован с Битрикс24');
    } catch (error) {
        console.error('Ошибка синхронизации с Битрикс24:', error);
    }
}

// Привязать обработчик к форме после загрузки страницы
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('calc-form');
    if (form) {
        form.addEventListener('submit', submitCalculatorForm);
    }
});
</script>
```

**⚠️ Важно:** Замените `https://ваш-домен.ru/api` на реальный URL вашего API!

---

## 5. Обработка ответа

### Добавление блока для отображения результата:

В редакторе Tilda добавьте блок **"HTML-код"** (T123) после формы:

```html
<div id="calculator-result" style="display: none; margin-top: 40px; padding: 30px; background: #f5f5f5; border-radius: 10px;">
    <!-- Результат будет вставлен JavaScript'ом -->
</div>

<style>
.calculator-result {
    text-align: center;
}

.calculator-result h3 {
    color: #4CAF50;
    font-size: 24px;
    margin-bottom: 20px;
}

.calculator-result p {
    font-size: 16px;
    margin: 10px 0;
}

.calculator-result .t-btn {
    display: inline-block;
    padding: 12px 30px;
    background: #4CAF50;
    color: white;
    text-decoration: none;
    border-radius: 5px;
    transition: background 0.3s;
}

.calculator-result .t-btn:hover {
    background: #45a049;
}
</style>
```

---

## 6. Готовые примеры форм

### Пример 1: Простая форма расчёта

```html
<form id="calc-form" class="t-form">
    <div class="t-input-group">
        <label>Ваше имя или компания *</label>
        <input type="text" id="customer_name" name="customer_name" required>
    </div>

    <div class="t-input-group">
        <label>Email *</label>
        <input type="email" id="email" name="email" required>
    </div>

    <div class="t-input-group">
        <label>Телефон</label>
        <input type="tel" id="phone" name="phone">
    </div>

    <div class="t-input-group">
        <label>Город</label>
        <input type="text" id="city" name="city">
    </div>

    <div class="t-input-group">
        <label>Тип системы *</label>
        <select id="system_type" name="system_type" required>
            <option value="">Выберите тип</option>
            <option value="Slider L">Slider L (параллельно-сдвижная)</option>
            <option value="Slider X">Slider X (усиленная)</option>
            <option value="JV Line">JV Line (с парковкой)</option>
            <option value="JV Zig-Zag">JV Zig-Zag (гармошка)</option>
        </select>
    </div>

    <div class="t-input-group">
        <label>Ширина проёма, мм *</label>
        <input type="number" id="width" name="width" min="1000" max="10000" required>
    </div>

    <div class="t-input-group">
        <label>Высота проёма, мм *</label>
        <input type="number" id="height" name="height" min="1000" max="5000" required>
    </div>

    <div class="t-input-group">
        <label>Количество створок *</label>
        <input type="number" id="panels" name="panels" min="2" max="10" step="1" required>
    </div>

    <div class="t-input-group">
        <label>Скидка, %</label>
        <input type="number" id="discount_percent" name="discount_percent" min="0" max="50" value="0">
    </div>

    <div class="t-input-group">
        <label>Комментарий</label>
        <textarea id="notes" name="notes" rows="3"></textarea>
    </div>

    <button type="submit" class="t-btn t-btn_primary">
        Рассчитать стоимость
    </button>
</form>
```

### Пример 2: Виджет быстрого расчёта

Компактная форма для боковой панели:

```html
<div class="quick-calc-widget">
    <h4>Быстрый расчёт</h4>
    <form id="quick-calc-form">
        <select id="q-system_type" required>
            <option value="Slider L">Slider L</option>
            <option value="Slider X">Slider X</option>
        </select>

        <input type="number" id="q-width" placeholder="Ширина, мм" required>
        <input type="number" id="q-height" placeholder="Высота, мм" required>
        <input type="number" id="q-panels" placeholder="Створок" min="2" max="10" required>

        <button type="submit">Узнать цену</button>
    </form>

    <div id="quick-result" style="display: none;">
        <p class="price">Примерная стоимость:<br><strong id="total-price"></strong></p>
        <a href="#full-form" class="detail-link">Подробный расчёт →</a>
    </div>
</div>
```

---

## 7. Отладка и тестирование

### Включение режима отладки в консоли:

```javascript
// Добавьте в начало вашего скрипта
const DEBUG = true;

function log(...args) {
    if (DEBUG) console.log('[Calculator]', ...args);
}

// Используйте в коде:
log('Отправка данных:', formData);
log('Ответ API:', orderData);
```

### Проверка работы API:

Откройте консоль браузера (F12) и выполните:

```javascript
// Тест создания заказа
fetch('https://ваш-домен.ru/api/orders', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({customer_name: 'Тест'})
})
.then(r => r.json())
.then(data => console.log('Результат:', data));
```

### Частые ошибки:

1. **CORS ошибка**
   - Убедитесь что добавили flask-cors
   - Проверьте домен в настройках CORS

2. **404 Not Found**
   - Проверьте URL API
   - Убедитесь что сервер запущен

3. **400 Bad Request**
   - Проверьте формат данных
   - Убедитесь что все обязательные поля заполнены

4. **500 Internal Server Error**
   - Проверьте логи сервера
   - Проверьте подключение к БД

---

## ✅ Готово!

Теперь ваш сайт на Tilda интегрирован с калькулятором Joy Vision!

**Что получилось:**
- ✅ Форма расчёта прямо на сайте
- ✅ Мгновенный расчёт стоимости
- ✅ Генерация PDF документов
- ✅ Сохранение заказов в системе
- ✅ Интеграция с Битрикс24

**Дополнительные возможности:**
- 💌 Настройте отправку email с PDF
- 📊 Добавьте Google Analytics события
- 🎨 Кастомизируйте дизайн результата
- 📱 Оптимизируйте для мобильных

**Нужна помощь?**
- Проверьте логи API: `sudo journalctl -u joyvision -f`
- Проверьте консоль браузера (F12)
- Протестируйте API напрямую через Postman

**Приятной работы! 🚀**
