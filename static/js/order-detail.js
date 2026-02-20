// order-detail.js - Логика страницы деталей заказа

function loadOrder(orderId) {
    fetch(`/api/orders/${orderId}`)
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                throw new Error(data.error || 'Заказ не найден');
            }
            renderOrder(data.data);
        })
        .catch(error => {
            document.getElementById('order-container').innerHTML = `
                <div class="alert alert-danger">
                    <h4>Ошибка загрузки заказа</h4>
                    <p>${error.message}</p>
                    <a href="/orders" class="btn btn-primary">Вернуться к списку</a>
                </div>
            `;
        });
}

function renderOrder(order) {
    const container = document.getElementById('order-container');

    const systemsHTML = order.systems && order.systems.length > 0
        ? order.systems.map(s => renderSystem(s)).join('')
        : '<p class="text-muted text-center py-4">Нет систем. Добавьте первую систему.</p>';

    container.innerHTML = `
        <div class="d-flex justify-content-between align-items-start mb-4">
            <div>
                <h1><i class="bi bi-file-earmark-text"></i> Заказ #${order.id}</h1>
                <p class="text-muted mb-0">
                    ${order.customer_name}
                    ${order.city ? ' • ' + order.city : ''}
                </p>
            </div>
            <div class="btn-group">
                <a href="/orders" class="btn btn-outline-secondary">
                    <i class="bi bi-arrow-left"></i> Назад
                </a>
                <button class="btn btn-outline-primary" onclick="downloadPDF('kp', ${order.id})">
                    <i class="bi bi-file-pdf"></i> КП
                </button>
                <button class="btn btn-outline-primary" onclick="downloadPDF('spec', ${order.id})">
                    <i class="bi bi-file-pdf"></i> Разблюдовка
                </button>
                <button class="btn btn-outline-success" onclick="syncToBitrix(${order.id})">
                    <i class="bi bi-cloud-upload"></i> Битрикс24
                </button>
            </div>
        </div>

        <div class="row">
            <div class="col-lg-8">
                <div class="card mb-4">
                    <div class="card-header bg-white d-flex justify-content-between align-items-center">
                        <h5 class="mb-0"><i class="bi bi-list-columns"></i> Системы (${order.systems_count})</h5>
                        <button class="btn btn-sm btn-primary" data-bs-toggle="modal" data-bs-target="#addSystemModal">
                            <i class="bi bi-plus-lg"></i> Добавить систему
                        </button>
                    </div>
                    <div class="card-body">
                        ${systemsHTML}
                    </div>
                </div>
            </div>

            <div class="col-lg-4">
                <div class="card mb-4">
                    <div class="card-header bg-white">
                        <h5 class="mb-0">Сводка</h5>
                    </div>
                    <div class="card-body">
                        <dl class="row mb-0">
                            <dt class="col-sm-6">Статус:</dt>
                            <dd class="col-sm-6">${formatStatus(order.status)}</dd>

                            <dt class="col-sm-6">Цвет RAL:</dt>
                            <dd class="col-sm-6">${order.ral_color}</dd>

                            <dt class="col-sm-6">Скидка:</dt>
                            <dd class="col-sm-6">${order.discount_percent}%</dd>
                        </dl>

                        <hr>

                        <div class="text-center">
                            <p class="text-muted mb-1">Итоговая стоимость</p>
                            <h2 class="price-tag mb-0">${formatPrice(order.total_price)}</h2>
                        </div>

                        ${order.bitrix_deal_id ? `
                            <div class="alert alert-success mt-3 mb-0">
                                <i class="bi bi-check-circle"></i> Синхронизировано с Битрикс24<br>
                                <small>ID сделки: ${order.bitrix_deal_id}</small>
                            </div>
                        ` : ''}
                    </div>
                </div>

                ${order.notes ? `
                    <div class="card">
                        <div class="card-header bg-white">
                            <h6 class="mb-0">Примечания</h6>
                        </div>
                        <div class="card-body">
                            <p class="mb-0">${order.notes}</p>
                        </div>
                    </div>
                ` : ''}
            </div>
        </div>
    `;

    setupAddSystemForm();
}

function renderSystem(system) {
    return `
        <div class="system-card card mb-3">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h5 class="card-title">
                            <span class="badge badge-system bg-primary me-2">${system.position}</span>
                            ${system.system_type}
                        </h5>
                        <p class="card-text">
                            <i class="bi bi-arrows-fullscreen"></i> ${system.width} × ${system.height} мм<br>
                            <i class="bi bi-grid-3x3"></i> Створок: ${system.panels}<br>
                            <i class="bi bi-arrow-right"></i> Открывание: ${system.opening}
                        </p>
                    </div>
                    <div class="text-end">
                        <h4 class="price-tag mb-0">${formatPrice(system.price)}</h4>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function setupAddSystemForm() {
    const form = document.getElementById('add-system-form');
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData(this);
        const data = {
            system_type: formData.get('system_type'),
            width: parseInt(formData.get('width')),
            height: parseInt(formData.get('height')),
            panels: parseFloat(formData.get('panels')),
            opening: formData.get('opening')
        };

        const submitBtn = this.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Расчёт...';

        fetch(`/api/orders/${ORDER_ID}/systems`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                bootstrap.Modal.getInstance(document.getElementById('addSystemModal')).hide();
                form.reset();
                loadOrder(ORDER_ID);
            } else {
                alert('Ошибка: ' + result.error);
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="bi bi-check-lg"></i> Добавить и рассчитать';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Произошла ошибка при добавлении системы');
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="bi bi-check-lg"></i> Добавить и рассчитать';
        });
    });
}

function downloadPDF(type, orderId) {
    window.open(`/api/orders/${orderId}/pdf/${type}`, '_blank');
}

function syncToBitrix(orderId) {
    if (!confirm('Синхронизировать заказ с Битрикс24?')) return;

    const btn = event.target.closest('button');
    const originalHTML = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Синхронизация...';

    fetch(`/api/bitrix/sync/${orderId}`, {method: 'POST'})
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                alert(`Успешно синхронизировано!\nID сделки: ${result.data.bitrix_deal_id}\nЗагружено файлов: ${result.data.files_uploaded.length}`);
                loadOrder(ORDER_ID);
            } else {
                alert('Ошибка: ' + result.error);
                btn.disabled = false;
                btn.innerHTML = originalHTML;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Произошла ошибка при синхронизации');
            btn.disabled = false;
            btn.innerHTML = originalHTML;
        });
}

function formatPrice(price) {
    return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB',
        minimumFractionDigits: 0
    }).format(price || 0);
}

function formatStatus(status) {
    const statusMap = {
        'draft': '<span class="badge bg-secondary">Черновик</span>',
        'confirmed': '<span class="badge bg-info">Подтверждён</span>',
        'in_production': '<span class="badge bg-warning">В производстве</span>',
        'completed': '<span class="badge bg-success">Выполнен</span>',
        'cancelled': '<span class="badge bg-danger">Отменён</span>'
    };
    return statusMap[status] || status;
}
