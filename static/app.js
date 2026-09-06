const tg = window.Telegram.WebApp;
tg.ready();
tg.expand();

const API_BASE = 'https://windowscleaning-4.onrender.com/api';

function getTelegramId() {
    const initData = tg.initDataUnsafe;
    if (initData && initData.user) {
        return initData.user.id;
    }
    return null;
}

// Показ контента
function showContent(html) {
    const content = document.getElementById('content');
    content.innerHTML = html;
    content.classList.add('active');
}

function hideContent() {
    const content = document.getElementById('content');
    content.classList.remove('active');
    content.innerHTML = '';
}

// Обработчики карточек
document.getElementById('register-card').addEventListener('click', showRegistration);
document.getElementById('new-request-card').addEventListener('click', showNewRequest);
document.getElementById('my-requests-card').addEventListener('click', showMyRequests);

// ========== РЕГИСТРАЦИЯ ==========
function showRegistration() {
    showContent(`
        <button class="back-btn" onclick="hideContent()">← Назад</button>
        <h2 style="margin-bottom:16px;">📝 Регистрация</h2>
        <div class="form-group">
            <label>Выберите дом</label>
            <select id="building-select">
                <option>Загрузка...</option>
            </select>
        </div>
        <div class="form-group">
            <label>Номер квартиры</label>
            <input type="text" id="apartment-number" placeholder="Например, 245">
        </div>
        <div class="form-group">
            <label>ФИО (необязательно)</label>
            <input type="text" id="full-name" placeholder="Иванов Иван">
        </div>
        <div class="form-group">
            <label>Сторона окон</label>
            <select id="window-side">
                <option value="unknown">Не знаю</option>
                <option value="street">Улица</option>
                <option value="yard">Двор</option>
                <option value="north">Север</option>
                <option value="south">Юг</option>
                <option value="east">Восток</option>
                <option value="west">Запад</option>
            </select>
        </div>
        <button class="btn" onclick="submitRegistration()">Зарегистрироваться</button>
    `);

    // Загрузка домов
    fetch(`${API_BASE}/buildings`)
        .then(res => res.json())
        .then(buildings => {
            const sel = document.getElementById('building-select');
            sel.innerHTML = '';
            if (buildings.length === 0) {
                sel.innerHTML = '<option>Нет домов</option>';
            } else {
                buildings.forEach(b => {
                    const opt = document.createElement('option');
                    opt.value = b.id;
                    opt.textContent = b.address;
                    sel.appendChild(opt);
                });
            }
        })
        .catch(err => {
            document.getElementById('building-select').innerHTML = '<option>Ошибка загрузки</option>';
        });
}

function submitRegistration() {
    const telegram_id = getTelegramId();
    const building_id = document.getElementById('building-select').value;
    const apartment_number = document.getElementById('apartment-number').value;
    const full_name = document.getElementById('full-name').value;
    const window_side = document.getElementById('window-side').value;

    if (!telegram_id) {
        alert('Ошибка: Telegram ID не найден');
        return;
    }

    fetch(`${API_BASE}/register`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({telegram_id, building_id, apartment_number, full_name, window_side})
    })
    .then(res => res.json())
    .then(data => {
        alert('✅ Регистрация успешна!');
        hideContent();
    })
    .catch(err => {
        alert('Ошибка: ' + err);
    });
}

// ========== НОВАЯ ЗАЯВКА ==========
function showNewRequest() {
    showContent(`
        <button class="back-btn" onclick="hideContent()">← Назад</button>
        <h2 style="margin-bottom:16px;">🪟 Новая заявка</h2>
        <div class="form-group">
            <label>Тип услуги</label>
            <select id="service-type">
                <option value="windows">Мытьё окон</option>
                <option value="balcony">Мытьё балкона</option>
                <option value="both">Комплекс (окна + балкон)</option>
            </select>
        </div>
        <div class="form-group">
            <label>Комментарий</label>
            <textarea id="comment" placeholder="Например: помыть только кухню"></textarea>
        </div>
        <button class="btn" onclick="submitRequest()">Отправить заявку</button>
    `);
}

function submitRequest() {
    const telegram_id = getTelegramId();
    const service_type = document.getElementById('service-type').value;
    const comment = document.getElementById('comment').value;

    if (!telegram_id) {
        alert('Ошибка: Telegram ID не найден');
        return;
    }

    fetch(`${API_BASE}/requests`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({telegram_id, service_type, comment, apartment_id: 1}) // TODO: брать из регистрации
    })
    .then(res => res.json())
    .then(data => {
        alert('✅ Заявка создана!');
        hideContent();
    })
    .catch(err => {
        alert('Ошибка: ' + err);
    });
}

// ========== МОИ ЗАЯВКИ ==========
function showMyRequests() {
    const telegram_id = getTelegramId();
    if (!telegram_id) {
        alert('Ошибка: Telegram ID не найден');
        return;
    }

    showContent(`
        <button class="back-btn" onclick="hideContent()">← Назад</button>
        <h2 style="margin-bottom:16px;">📋 Мои заявки</h2>
        <div id="requests-list">Загрузка...</div>
    `);

    fetch(`${API_BASE}/my_requests?telegram_id=${telegram_id}`)
        .then(res => res.json())
        .then(requests => {
            const container = document.getElementById('requests-list');
            if (requests.length === 0) {
                container.innerHTML = '<p style="color:#8e8e93;">У вас пока нет заявок</p>';
                return;
            }
            container.innerHTML = requests.map(r => `
                <div class="request-item">
                    <div class="req-header">
                        <span class="req-id">Заявка #${r.id}</span>
                        <span class="req-status status-${r.status}">${r.status}</span>
                    </div>
                    <div>${r.service_type}</div>
                    <div style="color:#8e8e93;font-size:14px;">${r.created_at ? new Date(r.created_at).toLocaleDateString() : ''}</div>
                </div>
            `).join('');
        })
        .catch(err => {
            document.getElementById('requests-list').innerHTML = 'Ошибка загрузки';
        });
}