// Joy Vision Calculator - Main JavaScript

/**
 * Форматирование цены в рубли
 */
function formatPrice(price) {
    return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB',
        minimumFractionDigits: 0
    }).format(price || 0);
}

/**
 * Форматирование даты
 */
function formatDate(dateStr) {
    if (!dateStr) return '—';
    const date = new Date(dateStr);
    return date.toLocaleDateString('ru-RU');
}

/**
 * API запрос с обработкой ошибок
 */
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Ошибка запроса');
        }

        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

/**
 * Показать уведомление
 */
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    const container = document.querySelector('main.container');
    container.insertBefore(alertDiv, container.firstChild);

    // Автоматическое скрытие через 5 секунд
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

/**
 * Инициализация при загрузке страницы
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Joy Vision Calculator loaded');
});
