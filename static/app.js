const tg = window.Telegram.WebApp;
tg.ready();
const API_BASE = 'https://windowscleaning-4.onrender.com/api'; // замените на ваш URL

function getTelegramId() {
    const initData = tg.initDataUnsafe;
    if (initData && initData.user) {
        return initData.user.id;
    }
    return null;
}

document.getElementById('register-btn').addEventListener('click', showRegistration);
document.getElementById('new-request-btn').addEventListener('click', showNewRequest);
document.getElementById('my-requests-btn').addEventListener('click', showMyRequests);

function showRegistration() {
    const content = document.getElementById('content');
    content.innerHTML = `
        <h2>Регистрация</h2>
        <p>Выберите дом и квартиру</p>
        <select id="building-select"></select>
        <input type="text" id="apartment-number" placeholder="Номер квартиры">
        <input type="text" id="full-name" placeholder="ФИО (необязательно)">
        <label>Сторона окон:
            <select id="window-side">
                <option value="unknown">Не знаю</option>
                <option value="street">Улица</option>
                <option value="yard">Двор</option>
                <option value="north">Север</option>
                <option value="south">Юг</option>
                <option value="east">Восток</option>
                <option value="west">Запад</option>
            </select>
        </label>
        <button onclick="submitRegistration()">Отправить</button>
    `;
    fetch(`${API_BASE}/buildings`)
        .then(res => res.json())
        .then(buildings => {
            const sel = document.getElementById('building-select');
            buildings.forEach(b => {
                const opt = document.createElement('option');
                opt.value = b.id;
                opt.textContent = b.address;
                sel.appendChild(opt);
            });
        });
}

function submitRegistration() {
    const telegram_id = getTelegramId();
    const building_id = document.getElementById('building-select').value;
    const apartment_number = document.getElementById('apartment-number').value;
    const full_name = document.getElementById('full-name').value;
    const window_side = document.getElementById('window-side').value;
    fetch(`${API_BASE}/register`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({telegram_id, building_id, apartment_number, full_name, window_side})
    })
    .then(res => res.json())
    .then(data => {
        alert('Регистрация успешна');
    })
    .catch(err => alert('Ошибка: ' + err));
}

function showNewRequest() {
    const content = document.getElementById('content');
    content.innerHTML = `
        <h2>Новая заявка</h2>
        <p>Выберите тип услуги:</p>
        <select id="service-type">
            <option value="windows">Мытьё окон</option>
            <option value="balcony">Мытьё балкона</option>
            <option value="both">Комплекс</option>
        </select>
        <textarea id="comment" placeholder="Комментарий"></textarea>
        <button onclick="submitRequest()">Отправить</button>
    `;
}

function submitRequest() {
    const telegram_id = getTelegramId();
    const service_type = document.getElementById('service-type').value;
    const comment = document.getElementById('comment').value;
    fetch(`${API_BASE}/requests`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({telegram_id, service_type, comment, apartment_id: 1}) // заглушка
    })
    .then(res => res.json())
    .then(data => {
        alert('Заявка создана');
    })
    .catch(err => alert('Ошибка: ' + err));
}

function showMyRequests() {
    const telegram_id = getTelegramId();
    fetch(`${API_BASE}/my_requests?telegram_id=${telegram_id}`)
        .then(res => res.json())
        .then(requests => {
            let html = '<h2>Мои заявки</h2>';
            requests.forEach(r => {
                html += `<p>#${r.id} - ${r.service_type} - ${r.status}</p>`;
            });
            document.getElementById('content').innerHTML = html;
        });
}
