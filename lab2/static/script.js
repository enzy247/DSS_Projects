const API_URL = 'http://localhost:8000';

// Глобальные переменные для хранения данных
let allResources = [];
let allTasks = [];
let allAlternatives = [];
let resourcesChart = null;
let tasksChart = null;

// Показ вкладок
function showTab(tabName) {
    // Скрыть все вкладки
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Убрать активный класс у всех кнопок
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Показать выбранную вкладку
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    // Активировать кнопку (находим кнопку по тексту)
    document.querySelectorAll('.tab-btn').forEach(btn => {
        if (btn.textContent.includes(getTabEmoji(tabName))) {
            btn.classList.add('active');
        }
    });
    
    // Загрузить данные при переключении
    if (tabName === 'dashboard') {
        loadDashboard();
    } else if (tabName === 'resources') {
        loadResources();
    } else if (tabName === 'tasks') {
        loadTasks();
    } else if (tabName === 'alternatives') {
        loadAlternatives();
    } else if (tabName === 'stats') {
        loadStats();
    }
}

function getTabEmoji(tabName) {
    // Эмодзи убраны для профессионального вида
    return '';
}

// Уведомления
function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    // Убираем эмодзи из сообщений
    const cleanMessage = message.replace(/[✅❌⏳⚠️🔄📥🚀🗑️✏️🔍➕💾🏠👥📋⚖️📊]/g, '').trim();
    notification.textContent = cleanMessage || message;
    notification.className = `notification ${type}`;
    notification.style.display = 'block';
    
    setTimeout(() => {
        notification.style.display = 'none';
    }, 3000);
}

// ========== РЕСУРСЫ ==========

// Добавление ресурса
document.getElementById('resource-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const resource = {
        name: document.getElementById('resource-name').value,
        type: document.getElementById('resource-type').value,
        available_hours: parseFloat(document.getElementById('resource-hours').value)
    };
    
    try {
        const response = await fetch(`${API_URL}/resource`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(resource)
        });
        
        if (response.ok) {
            showNotification('Ресурс успешно добавлен', 'success');
            document.getElementById('resource-form').reset();
            loadResources();
        } else {
            showNotification('Ошибка при добавлении ресурса', 'error');
        }
    } catch (error) {
        showNotification('Ошибка подключения к серверу', 'error');
    }
});

// Загрузка списка ресурсов
async function loadResources() {
    try {
        const response = await fetch(`${API_URL}/resources`);
        const resources = await response.json();
        
        const container = document.getElementById('resources-list');
        container.innerHTML = '';
        
        if (resources.length === 0) {
            container.innerHTML = '<p class="info-text">Нет добавленных ресурсов</p>';
            return;
        }
        
        resources.forEach(resource => {
            const card = document.createElement('div');
            card.className = 'card';
            card.innerHTML = `
                <h3>${resource.name}</h3>
                <p><strong>Тип:</strong> ${resource.type}</p>
                <p><strong>Доступные часы:</strong> ${resource.available_hours}</p>
                <div class="card-actions">
                    <button class="btn btn-danger btn-small" onclick="deleteResource(${resource.id})">🗑️ Удалить</button>
                </div>
            `;
            container.appendChild(card);
        });
    } catch (error) {
        showNotification('❌ Ошибка загрузки ресурсов', 'error');
    }
}

// Удаление ресурса
async function deleteResource(id) {
    if (!confirm('Вы уверены, что хотите удалить этот ресурс?')) return;
    
    try {
        const response = await fetch(`${API_URL}/resource/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showNotification('Ресурс удален', 'success');
            loadResources();
        } else {
            showNotification('Ошибка при удалении', 'error');
        }
    } catch (error) {
        showNotification('Ошибка подключения', 'error');
    }
}

// ========== ЗАДАЧИ ==========

// Добавление задачи
document.getElementById('task-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const task = {
        title: document.getElementById('task-title').value,
        required_hours: parseFloat(document.getElementById('task-hours').value),
        priority: parseInt(document.getElementById('task-priority').value)
    };
    
    try {
        const response = await fetch(`${API_URL}/task`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(task)
        });
        
        if (response.ok) {
            showNotification('Задача успешно добавлена', 'success');
            document.getElementById('task-form').reset();
            loadTasks();
        } else {
            showNotification('Ошибка при добавлении задачи', 'error');
        }
    } catch (error) {
        showNotification('Ошибка подключения к серверу', 'error');
    }
});

// Загрузка списка задач
async function loadTasks() {
    try {
        const response = await fetch(`${API_URL}/tasks`);
        const tasks = await response.json();
        
        const container = document.getElementById('tasks-list');
        container.innerHTML = '';
        
        if (tasks.length === 0) {
            container.innerHTML = '<p class="info-text">Нет добавленных задач</p>';
            return;
        }
        
        tasks.forEach(task => {
            const card = document.createElement('div');
            card.className = 'card';
            card.innerHTML = `
                <h3>${task.title}</h3>
                <p><strong>Требуемые часы:</strong> ${task.required_hours}</p>
                <p><strong>Приоритет:</strong> ${task.priority} ${getPriorityText(task.priority)}</p>
                <div class="card-actions">
                    <button class="btn btn-danger btn-small" onclick="deleteTask(${task.id})">🗑️ Удалить</button>
                </div>
            `;
            container.appendChild(card);
        });
    } catch (error) {
        showNotification('❌ Ошибка загрузки задач', 'error');
    }
}

function getPriorityText(priority) {
    const texts = {
        1: '(Высший)',
        2: '(Высокий)',
        3: '(Средний)',
        4: '(Низкий)',
        5: '(Низший)'
    };
    return texts[priority] || '';
}

// Удаление задачи
async function deleteTask(id) {
    if (!confirm('Вы уверены, что хотите удалить эту задачу?')) return;
    
    try {
        const response = await fetch(`${API_URL}/task/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showNotification('Задача удалена', 'success');
            loadTasks();
        } else {
            showNotification('Ошибка при удалении', 'error');
        }
    } catch (error) {
        showNotification('Ошибка подключения', 'error');
    }
}

// ========== АЛЬТЕРНАТИВЫ ==========

// Генерация альтернатив
async function generateAlternatives() {
    try {
        showNotification('Генерация альтернатив...', 'success');
        
        const response = await fetch(`${API_URL}/alternatives`);
        
        if (!response.ok) {
            const error = await response.json();
            showNotification(error.detail || 'Ошибка генерации альтернатив', 'error');
            return;
        }
        
        const data = await response.json();
        showNotification(`Сгенерировано ${data.total} альтернатив`, 'success');
        
        displayAlternatives(data.alternatives, data);
        updateCompareDropdowns(data.alternatives);
        updateStatsDropdown(data.alternatives);
        updateMLInfo();
    } catch (error) {
        showNotification('Ошибка генерации альтернатив', 'error');
    }
}

// Загрузка альтернатив
async function loadAlternatives() {
    try {
        const response = await fetch(`${API_URL}/alternatives`);
        
        if (!response.ok) {
            document.getElementById('alternatives-list').innerHTML = 
                '<p class="info-text">Сначала добавьте ресурсы и задачи, затем сгенерируйте альтернативы</p>';
            updateCompareDropdowns([]);
            return;
        }
        
        const data = await response.json();
        displayAlternatives(data.alternatives, data);
        
        // Обновляем информацию о ML модели
        updateMLInfo();
    } catch (error) {
        document.getElementById('alternatives-list').innerHTML = 
            '<p class="info-text">Ошибка загрузки альтернатив</p>';
        updateCompareDropdowns([]);
    }
}

// Обновление информации о ML модели
async function updateMLInfo() {
    const mlInfo = await getMLInfo();
    const mlInfoDiv = document.getElementById('ml-info');
    const mlStatus = document.getElementById('ml-status');
    
    if (mlInfo.ml_available) {
        mlInfoDiv.style.display = 'block';
        if (mlInfo.is_trained) {
            mlStatus.innerHTML = `
                <strong>Статус:</strong> Модель обучена и готова к использованию<br>
                <strong>Рекомендации:</strong> Доступны для альтернатив
            `;
        } else {
            mlStatus.innerHTML = `
                <strong>Статус:</strong> Модель не обучена<br>
                <strong>Действие:</strong> Выберите несколько альтернатив, затем нажмите "Обучить ML модель"
            `;
        }
    } else {
        mlInfoDiv.style.display = 'none';
    }
}

// Отображение альтернатив
function displayAlternatives(alternatives, fullData = null) {
    const container = document.getElementById('alternatives-list');
    container.innerHTML = '';
    
    if (alternatives.length === 0) {
        container.innerHTML = '<p class="info-text">Нет альтернатив. Нажмите кнопку "Сгенерировать альтернативы"</p>';
        return;
    }
    
    alternatives.forEach((alt, index) => {
        const altCard = document.createElement('div');
        altCard.className = 'alternative-card';
        
        let allocationsTable = '';
        if (alt.allocations.length > 0) {
            allocationsTable = `
                <table class="allocations-table">
                    <thead>
                        <tr>
                            <th>Ресурс</th>
                            <th>Задача</th>
                            <th>Часы</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${alt.allocations.map(a => `
                            <tr>
                                <td>${a.resource_name}</td>
                                <td>${a.task_title}</td>
                                <td>${a.hours.toFixed(1)}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        }
        
        altCard.innerHTML = `
            <div class="alternative-header">
                <h3>Альтернатива ${index + 1}</h3>
                <div class="alternative-score">Балл: ${alt.score.toFixed(1)}</div>
            </div>
            <div class="alternative-explanation">${alt.explanation}</div>
            ${allocationsTable}
        `;
        
        container.appendChild(altCard);
    });
}

// Обновление выпадающего списка для статистики
function updateStatsDropdown(alternatives) {
    const select = document.getElementById('stats-alternative');
    select.innerHTML = '<option value="">Лучшая альтернатива (по умолчанию)</option>';
    
    alternatives.forEach(alt => {
        const option = document.createElement('option');
        option.value = alt.id;
        option.textContent = `Альтернатива ${alt.id} (Балл: ${alt.score.toFixed(1)})`;
        select.appendChild(option);
    });
}

// ========== СТАТИСТИКА ==========

// Загрузка статистики
async function loadStats() {
    const alternativeId = document.getElementById('stats-alternative').value;
    const url = alternativeId 
        ? `${API_URL}/stats?alternative_id=${alternativeId}`
        : `${API_URL}/stats`;
    
    try {
        const response = await fetch(url);
        const stats = await response.json();
        
        displayStats(stats);
    } catch (error) {
        document.getElementById('stats-content').innerHTML = 
            '<p class="info-text">Ошибка загрузки статистики. Сначала сгенерируйте альтернативы.</p>';
    }
}

// Отображение статистики
function displayStats(stats) {
    const container = document.getElementById('stats-content');
    
    let html = `
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Общая статистика</h3>
                <div class="stat-value">${stats.total_resources}</div>
                <p>Ресурсов</p>
            </div>
            <div class="stat-card">
                <h3>Задач</h3>
                <div class="stat-value">${stats.total_tasks}</div>
            </div>
            <div class="stat-card">
                <h3>Покрытие</h3>
                <div class="stat-value">${stats.overall_coverage_percent.toFixed(1)}%</div>
                <p>Требуемых часов</p>
            </div>
        </div>
    `;
    
    // Статистика по ресурсам
    if (stats.resource_stats && stats.resource_stats.length > 0) {
        html += '<h3 style="margin-top: 30px; color: #667eea;">Загрузка ресурсов</h3>';
        html += '<div class="cards-container">';
        stats.resource_stats.forEach(rs => {
            const overloadClass = rs.overload ? 'btn-danger' : '';
            html += `
                <div class="card">
                    <h3>${rs.resource_name}</h3>
                    <p><strong>Доступно:</strong> ${rs.available_hours} ч</p>
                    <p><strong>Выделено:</strong> ${rs.allocated_hours.toFixed(1)} ч</p>
                    <p><strong>Загрузка:</strong> ${rs.utilization_percent.toFixed(1)}%</p>
                    ${rs.overload ? '<p style="color: #dc3545; font-weight: 600; margin-top: 8px;">Перегрузка ресурса</p>' : ''}
                </div>
            `;
        });
        html += '</div>';
    }
    
    // Статистика по задачам
    if (stats.task_stats && stats.task_stats.length > 0) {
        html += '<h3 style="margin-top: 30px; color: #667eea;">Покрытие задач</h3>';
        html += '<div class="cards-container">';
        stats.task_stats.forEach(ts => {
            const incomplete = ts.coverage_percent < 100;
            html += `
                <div class="card">
                    <h3>${ts.task_title}</h3>
                    <p><strong>Требуется:</strong> ${ts.required_hours} ч</p>
                    <p><strong>Выделено:</strong> ${ts.allocated_hours.toFixed(1)} ч</p>
                    <p><strong>Покрытие:</strong> ${ts.coverage_percent.toFixed(1)}%</p>
                    <p><strong>Приоритет:</strong> ${ts.priority}</p>
                    ${incomplete ? '<p style="color: #ff9800; font-weight: 600; margin-top: 8px;">Не полностью покрыто</p>' : ''}
                </div>
            `;
        });
        html += '</div>';
    }
    
    // Предупреждения
    if (stats.warnings && stats.warnings.length > 0) {
        html += '<div class="warnings">';
        html += '<h3>Предупреждения:</h3>';
        stats.warnings.forEach(warning => {
            html += `<div class="warning-item">${warning}</div>`;
        });
        html += '</div>';
    }
    
    container.innerHTML = html;
}

// ========== ДАШБОРД ==========

// Загрузка дашборда
async function loadDashboard() {
    await Promise.all([
        loadDashboardStats(),
        loadDashboardCharts(),
        loadRecentAlternatives()
    ]);
}

// Загрузка статистики дашборда
async function loadDashboardStats() {
    try {
        const [resourcesRes, tasksRes, alternativesRes] = await Promise.all([
            fetch(`${API_URL}/resources`),
            fetch(`${API_URL}/tasks`),
            fetch(`${API_URL}/alternatives`)
        ]);
        
        const resources = resourcesRes.ok ? await resourcesRes.json() : [];
        const tasks = tasksRes.ok ? await tasksRes.json() : [];
        const alternatives = alternativesRes.ok ? (await alternativesRes.json()).alternatives : [];
        
        document.getElementById('stat-resources').textContent = resources.length;
        document.getElementById('stat-tasks').textContent = tasks.length;
        document.getElementById('stat-alternatives').textContent = alternatives.length;
        
        // Расчет общей загрузки
        if (alternatives.length > 0 && resources.length > 0) {
            const statsRes = await fetch(`${API_URL}/stats`);
            if (statsRes.ok) {
                const stats = await statsRes.json();
                document.getElementById('stat-load').textContent = 
                    stats.overall_coverage_percent.toFixed(1) + '%';
            }
        } else {
            document.getElementById('stat-load').textContent = '0%';
        }
    } catch (error) {
        console.error('Ошибка загрузки статистики:', error);
    }
}

// Загрузка графиков дашборда
async function loadDashboardCharts() {
    try {
        const statsRes = await fetch(`${API_URL}/stats`);
        if (!statsRes.ok) {
            document.getElementById('resources-chart').style.display = 'none';
            document.getElementById('tasks-chart').style.display = 'none';
            return;
        }
        
        const stats = await statsRes.json();
        
        // График загрузки ресурсов
        const resourcesCtx = document.getElementById('resources-chart');
        if (resourcesChart) resourcesChart.destroy();
        
        if (stats.resource_stats && stats.resource_stats.length > 0) {
            resourcesChart = new Chart(resourcesCtx, {
                type: 'bar',
                data: {
                    labels: stats.resource_stats.map(r => r.resource_name),
                    datasets: [{
                        label: 'Загрузка (%)',
                        data: stats.resource_stats.map(r => r.utilization_percent),
                        backgroundColor: stats.resource_stats.map(r => 
                            r.overload ? 'rgba(220, 53, 69, 0.7)' : 'rgba(102, 126, 234, 0.7)'
                        ),
                        borderColor: stats.resource_stats.map(r => 
                            r.overload ? 'rgb(220, 53, 69)' : 'rgb(102, 126, 234)'
                        ),
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 120
                        }
                    }
                }
            });
        }
        
        // График покрытия задач
        const tasksCtx = document.getElementById('tasks-chart');
        if (tasksChart) tasksChart.destroy();
        
        if (stats.task_stats && stats.task_stats.length > 0) {
            tasksChart = new Chart(tasksCtx, {
                type: 'doughnut',
                data: {
                    labels: stats.task_stats.map(t => t.task_title),
                    datasets: [{
                        data: stats.task_stats.map(t => t.coverage_percent),
                        backgroundColor: [
                            'rgba(102, 126, 234, 0.7)',
                            'rgba(118, 75, 162, 0.7)',
                            'rgba(255, 193, 7, 0.7)',
                            'rgba(40, 167, 69, 0.7)',
                            'rgba(220, 53, 69, 0.7)'
                        ]
                    }]
                },
                options: {
                    responsive: true
                }
            });
        }
    } catch (error) {
        console.error('Ошибка загрузки графиков:', error);
    }
}

// Загрузка последних альтернатив
async function loadRecentAlternatives() {
    try {
        const response = await fetch(`${API_URL}/alternatives`);
        if (!response.ok) {
            document.getElementById('recent-alternatives').innerHTML = 
                '<p class="info-text">Сгенерируйте альтернативы для просмотра</p>';
            return;
        }
        
        const data = await response.json();
        const alternatives = data.alternatives.slice(0, 3); // Первые 3
        
        const container = document.getElementById('recent-alternatives');
        if (alternatives.length === 0) {
            container.innerHTML = '<p class="info-text">Нет альтернатив</p>';
            return;
        }
        
        container.innerHTML = alternatives.map(alt => `
            <div class="alternative-preview-card" onclick="showTab('alternatives'); event.target.closest('.tab-btn')?.click()">
                <h4>Альтернатива ${alt.id}</h4>
                <p><strong>Балл:</strong> ${alt.score.toFixed(1)}</p>
                <p style="font-size: 0.9em; color: #666; margin-top: 10px;">${alt.explanation.substring(0, 100)}...</p>
            </div>
        `).join('');
    } catch (error) {
        console.error('Ошибка загрузки альтернатив:', error);
    }
}

// Загрузка примерных данных
async function loadExampleData() {
    try {
        showNotification('Загрузка примерных данных...', 'success');
        const response = await fetch(`${API_URL}/load-example-data`, {
            method: 'POST'
        });
        
        if (response.ok) {
            const data = await response.json();
            showNotification(`Загружено: ${data.resources_added} ресурсов, ${data.tasks_added} задач`, 'success');
            loadDashboard();
            loadResources();
            loadTasks();
        } else {
            showNotification('Ошибка загрузки данных', 'error');
        }
    } catch (error) {
        showNotification('Ошибка подключения', 'error');
    }
}

// Очистка всех данных
async function clearAllData() {
    if (!confirm('ВНИМАНИЕ! Вы уверены, что хотите удалить ВСЕ данные?\n\nЭто действие удалит:\n- Все ресурсы\n- Все задачи\n- Все альтернативы\n\nЭто действие необратимо!')) {
        return;
    }
    
    if (!confirm('Вы действительно уверены? Это действие нельзя отменить!')) {
        return;
    }
    
    try {
        showNotification('Удаление данных...', 'success');
        const response = await fetch(`${API_URL}/clear-all-data`, {
            method: 'POST'
        });
        
        if (response.ok) {
            const data = await response.json();
            showNotification(
                `Удалено: ${data.resources_deleted} ресурсов, ${data.tasks_deleted} задач, ${data.alternatives_deleted || 0} альтернатив`, 
                'success'
            );
            loadDashboard();
            loadResources();
            loadTasks();
            document.getElementById('alternatives-list').innerHTML = 
                '<p class="info-text">Нет альтернатив. Сначала добавьте ресурсы и задачи, затем сгенерируйте альтернативы</p>';
            document.getElementById('stats-content').innerHTML = 
                '<p class="info-text">Нет данных для статистики</p>';
        } else {
            const errorData = await response.json().catch(() => ({ detail: 'Неизвестная ошибка' }));
            showNotification(`Ошибка: ${errorData.detail || 'Ошибка при удалении данных'}`, 'error');
            console.error('Ошибка удаления:', errorData);
        }
    } catch (error) {
        showNotification(`Ошибка подключения: ${error.message}`, 'error');
        console.error('Ошибка:', error);
    }
}

// ========== ПОИСК И ФИЛЬТРАЦИЯ ==========

// Фильтрация ресурсов
function filterResources() {
    const search = document.getElementById('resource-search').value.toLowerCase();
    const typeFilter = document.getElementById('resource-type-filter').value;
    
    const filtered = allResources.filter(r => {
        const matchesSearch = r.name.toLowerCase().includes(search) || 
                             r.type.toLowerCase().includes(search);
        const matchesType = !typeFilter || r.type === typeFilter;
        return matchesSearch && matchesType;
    });
    
    displayResources(filtered);
}

// Фильтрация задач
function filterTasks() {
    const search = document.getElementById('task-search').value.toLowerCase();
    const priorityFilter = document.getElementById('task-priority-filter').value;
    
    const filtered = allTasks.filter(t => {
        const matchesSearch = t.title.toLowerCase().includes(search);
        const matchesPriority = !priorityFilter || t.priority.toString() === priorityFilter;
        return matchesSearch && matchesPriority;
    });
    
    displayTasks(filtered);
}

// ========== РЕДАКТИРОВАНИЕ ==========

// Открытие модального окна редактирования ресурса
async function openEditResourceModal(resourceId) {
    try {
        const response = await fetch(`${API_URL}/resource/${resourceId}`);
        const resource = await response.json();
        
        document.getElementById('edit-resource-id').value = resource.id;
        document.getElementById('edit-resource-name').value = resource.name;
        document.getElementById('edit-resource-type').value = resource.type;
        document.getElementById('edit-resource-hours').value = resource.available_hours;
        document.getElementById('edit-resource-modal').style.display = 'block';
    } catch (error) {
        showNotification('Ошибка загрузки данных ресурса', 'error');
    }
}

// Закрытие модального окна редактирования ресурса
function closeEditResourceModal() {
    document.getElementById('edit-resource-modal').style.display = 'none';
}

// Сохранение изменений ресурса
document.getElementById('edit-resource-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const id = document.getElementById('edit-resource-id').value;
    const resource = {
        name: document.getElementById('edit-resource-name').value,
        type: document.getElementById('edit-resource-type').value,
        available_hours: parseFloat(document.getElementById('edit-resource-hours').value)
    };
    
    try {
        const response = await fetch(`${API_URL}/resource/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(resource)
        });
        
        if (response.ok) {
            showNotification('Ресурс успешно обновлен', 'success');
            closeEditResourceModal();
            loadResources();
            loadDashboard();
        } else {
            showNotification('Ошибка при обновлении', 'error');
        }
    } catch (error) {
        showNotification('Ошибка подключения', 'error');
    }
});

// Открытие модального окна редактирования задачи
async function openEditTaskModal(taskId) {
    try {
        const response = await fetch(`${API_URL}/task/${taskId}`);
        const task = await response.json();
        
        document.getElementById('edit-task-id').value = task.id;
        document.getElementById('edit-task-title').value = task.title;
        document.getElementById('edit-task-hours').value = task.required_hours;
        document.getElementById('edit-task-priority').value = task.priority;
        document.getElementById('edit-task-modal').style.display = 'block';
    } catch (error) {
        showNotification('Ошибка загрузки данных задачи', 'error');
    }
}

// Закрытие модального окна редактирования задачи
function closeEditTaskModal() {
    document.getElementById('edit-task-modal').style.display = 'none';
}

// Сохранение изменений задачи
document.getElementById('edit-task-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const id = document.getElementById('edit-task-id').value;
    const task = {
        title: document.getElementById('edit-task-title').value,
        required_hours: parseFloat(document.getElementById('edit-task-hours').value),
        priority: parseInt(document.getElementById('edit-task-priority').value)
    };
    
    try {
        const response = await fetch(`${API_URL}/task/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(task)
        });
        
        if (response.ok) {
            showNotification('Задача успешно обновлена', 'success');
            closeEditTaskModal();
            loadTasks();
            loadDashboard();
        } else {
            showNotification('Ошибка при обновлении', 'error');
        }
    } catch (error) {
        showNotification('Ошибка подключения', 'error');
    }
});

// Закрытие модальных окон при клике вне их
window.onclick = function(event) {
    const resourceModal = document.getElementById('edit-resource-modal');
    const taskModal = document.getElementById('edit-task-modal');
    if (event.target === resourceModal) {
        closeEditResourceModal();
    }
    if (event.target === taskModal) {
        closeEditTaskModal();
    }
}

// ========== СРАВНЕНИЕ АЛЬТЕРНАТИВ ==========

// Сравнение альтернатив
async function compareAlternatives() {
    const alt1Id = document.getElementById('compare-alt1').value;
    const alt2Id = document.getElementById('compare-alt2').value;
    
    if (!alt1Id || !alt2Id) {
        showNotification('Выберите обе альтернативы для сравнения', 'error');
        return;
    }
    
    if (alt1Id === alt2Id) {
        showNotification('Выберите разные альтернативы', 'error');
        return;
    }
    
    try {
        const [alt1Res, alt2Res] = await Promise.all([
            fetch(`${API_URL}/alternative/${alt1Id}`),
            fetch(`${API_URL}/alternative/${alt2Id}`)
        ]);
        
        const alt1 = await alt1Res.json();
        const alt2 = await alt2Res.json();
        
        displayComparison(alt1, alt2);
    } catch (error) {
        showNotification('Ошибка загрузки альтернатив', 'error');
    }
}

// Отображение сравнения
function displayComparison(alt1, alt2) {
    const container = document.getElementById('compare-result');
    container.style.display = 'block';
    container.innerHTML = `
        <div class="compare-container">
            <div class="compare-card">
                <h3>Альтернатива ${alt1.id} (Балл: ${alt1.score.toFixed(1)})</h3>
                <p><strong>Пояснение:</strong> ${alt1.explanation}</p>
                <h4>Распределения:</h4>
                <table class="allocations-table">
                    <thead>
                        <tr><th>Ресурс</th><th>Задача</th><th>Часы</th></tr>
                    </thead>
                    <tbody>
                        ${alt1.allocations.map(a => `
                            <tr>
                                <td>${a.resource_name}</td>
                                <td>${a.task_title}</td>
                                <td>${a.hours.toFixed(1)}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
            <div class="compare-card">
                <h3>Альтернатива ${alt2.id} (Балл: ${alt2.score.toFixed(1)})</h3>
                <p><strong>Пояснение:</strong> ${alt2.explanation}</p>
                <h4>Распределения:</h4>
                <table class="allocations-table">
                    <thead>
                        <tr><th>Ресурс</th><th>Задача</th><th>Часы</th></tr>
                    </thead>
                    <tbody>
                        ${alt2.allocations.map(a => `
                            <tr>
                                <td>${a.resource_name}</td>
                                <td>${a.task_title}</td>
                                <td>${a.hours.toFixed(1)}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>
        <div style="margin-top: 20px; padding: 15px; background: #e7f3ff; border-radius: 8px;">
            <h4>Различия:</h4>
            <div class="difference-item">
                <strong>Разница в баллах:</strong> ${Math.abs(alt1.score - alt2.score).toFixed(1)} 
                (${alt1.score > alt2.score ? 'Альтернатива 1 лучше' : 'Альтернатива 2 лучше'})
            </div>
        </div>
    `;
    
    // Прокрутка к результатам
    container.scrollIntoView({ behavior: 'smooth' });
}

// Обновление выпадающих списков для сравнения
function updateCompareDropdowns(alternatives) {
    const select1 = document.getElementById('compare-alt1');
    const select2 = document.getElementById('compare-alt2');
    const controls = document.getElementById('compare-controls');
    
    if (alternatives.length >= 2) {
        controls.style.display = 'block';
        select1.innerHTML = '<option value="">Выберите первую альтернативу...</option>';
        select2.innerHTML = '<option value="">Выберите вторую альтернативу...</option>';
        
        alternatives.forEach(alt => {
            const option1 = document.createElement('option');
            option1.value = alt.id;
            option1.textContent = `Альтернатива ${alt.id} (Балл: ${alt.score.toFixed(1)})`;
            select1.appendChild(option1);
            
            const option2 = document.createElement('option');
            option2.value = alt.id;
            option2.textContent = `Альтернатива ${alt.id} (Балл: ${alt.score.toFixed(1)})`;
            select2.appendChild(option2);
        });
    } else {
        controls.style.display = 'none';
    }
}

// Обновление функции отображения ресурсов
function displayResources(resources) {
    const container = document.getElementById('resources-list');
    container.innerHTML = '';
    
    if (resources.length === 0) {
        container.innerHTML = '<p class="info-text">Нет ресурсов, соответствующих фильтрам</p>';
        return;
    }
    
    resources.forEach(resource => {
        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `
            <h3>${resource.name}</h3>
            <p><strong>Тип:</strong> ${resource.type}</p>
            <p><strong>Доступные часы:</strong> ${resource.available_hours}</p>
            <div class="card-actions">
                <button class="btn btn-primary btn-small" onclick="openEditResourceModal(${resource.id})">Редактировать</button>
                <button class="btn btn-danger btn-small" onclick="deleteResource(${resource.id})">Удалить</button>
            </div>
        `;
        container.appendChild(card);
    });
}

// Обновление функции отображения задач
function displayTasks(tasks) {
    const container = document.getElementById('tasks-list');
    container.innerHTML = '';
    
    if (tasks.length === 0) {
        container.innerHTML = '<p class="info-text">Нет задач, соответствующих фильтрам</p>';
        return;
    }
    
    tasks.forEach(task => {
        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `
            <h3>${task.title}</h3>
            <p><strong>Требуемые часы:</strong> ${task.required_hours}</p>
            <p><strong>Приоритет:</strong> ${task.priority} ${getPriorityText(task.priority)}</p>
            <div class="card-actions">
                <button class="btn btn-primary btn-small" onclick="openEditTaskModal(${task.id})">Редактировать</button>
                <button class="btn btn-danger btn-small" onclick="deleteTask(${task.id})">Удалить</button>
            </div>
        `;
        container.appendChild(card);
    });
}

// Обновление функции загрузки ресурсов
async function loadResources() {
    try {
        const response = await fetch(`${API_URL}/resources`);
        allResources = await response.json();
        filterResources(); // Используем фильтрацию для отображения
    } catch (error) {
        showNotification('❌ Ошибка загрузки ресурсов', 'error');
    }
}

// Обновление функции загрузки задач
async function loadTasks() {
    try {
        const response = await fetch(`${API_URL}/tasks`);
        allTasks = await response.json();
        filterTasks(); // Используем фильтрацию для отображения
    } catch (error) {
        showNotification('❌ Ошибка загрузки задач', 'error');
    }
}

// Обновление функции отображения альтернатив
function displayAlternatives(alternatives, fullData = null) {
    allAlternatives = alternatives;
    const container = document.getElementById('alternatives-list');
    container.innerHTML = '';
    
    if (alternatives.length === 0) {
        container.innerHTML = '<p class="info-text">Нет альтернатив. Нажмите кнопку "Сгенерировать альтернативы"</p>';
        updateCompareDropdowns([]);
        return;
    }
    
    alternatives.forEach((alt, index) => {
        const altCard = document.createElement('div');
        altCard.className = 'alternative-card';
        
        // Проверяем, есть ли рекомендация ML
        const isRecommended = fullData && fullData.recommendations && fullData.recommendations.some(
            r => r.alternative_id === alt.id && r.is_recommended
        );
        const recommendationScore = fullData && fullData.recommendations && fullData.recommendations.find(
            r => r.alternative_id === alt.id
        )?.recommendation_score;
        
        let allocationsTable = '';
        if (alt.allocations.length > 0) {
            allocationsTable = `
                <table class="allocations-table">
                    <thead>
                        <tr>
                            <th>Ресурс</th>
                            <th>Задача</th>
                            <th>Часы</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${alt.allocations.map(a => `
                            <tr>
                                <td>${a.resource_name}</td>
                                <td>${a.task_title}</td>
                                <td>${a.hours.toFixed(1)}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        }
        
        altCard.innerHTML = `
            <div class="alternative-header">
                <h3>Альтернатива ${index + 1}${isRecommended ? ' <span class="ml-badge">Рекомендуется ML</span>' : ''}</h3>
                <div class="alternative-score">Балл: ${alt.score.toFixed(1)}${recommendationScore ? ` <span style="font-size: 0.8em; color: #667eea;">(ML: ${(recommendationScore * 100).toFixed(0)}%)</span>` : ''}</div>
            </div>
            <div class="alternative-explanation">${alt.explanation}</div>
            ${allocationsTable}
            <div class="card-actions" style="margin-top: 15px;">
                <button class="btn btn-primary btn-small" onclick="selectAlternative(${alt.id})">Выбрать эту альтернативу</button>
            </div>
        `;
        
        container.appendChild(altCard);
    });
    
    updateCompareDropdowns(alternatives);
    updateStatsDropdown(alternatives);
}

// ========== ML ФУНКЦИИ ==========

// Выбор альтернативы (для обучения ML)
async function selectAlternative(alternativeId) {
    try {
        const response = await fetch(`${API_URL}/alternative/${alternativeId}/select`, {
            method: 'POST'
        });
        
        if (response.ok) {
            const data = await response.json();
            showNotification(
                `Альтернатива выбрана. ${data.ml_prediction ? `ML предсказал: ${(data.ml_prediction * 100).toFixed(0)}%` : ''}`, 
                'success'
            );
        } else {
            showNotification('Ошибка при сохранении выбора', 'error');
        }
    } catch (error) {
        showNotification('Ошибка подключения', 'error');
    }
}

// Обучение ML модели
async function trainMLModel() {
    try {
        showNotification('Обучение ML модели...', 'success');
        const response = await fetch(`${API_URL}/ml/train`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showNotification(
                `Модель обучена! Точность: ${(data.accuracy * 100).toFixed(1)}%`, 
                'success'
            );
            // Перезагружаем альтернативы для получения рекомендаций
            loadAlternatives();
        } else {
            showNotification(data.message || 'Ошибка обучения модели', 'error');
        }
    } catch (error) {
        showNotification('Ошибка подключения', 'error');
    }
}

// Получение информации о ML модели
async function getMLInfo() {
    try {
        const response = await fetch(`${API_URL}/ml/info`);
        const data = await response.json();
        return data;
    } catch (error) {
        return { is_trained: false, ml_available: false };
    }
}

// Загрузка данных при загрузке страницы
window.addEventListener('load', () => {
    loadDashboard();
    loadResources();
    loadTasks();
});

