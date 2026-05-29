const tg = window.Telegram && window.Telegram.WebApp ? window.Telegram.WebApp : null;

if (tg) {
    tg.expand();
    tg.ready();
}

let currentLang = localStorage.getItem('lang') || 'en';
let currentTheme = localStorage.getItem('theme') || 'light';
let cart = [];
let currentModalProductId = null;

const flags = { en: '🇺🇸 EN', ru: '🇷🇺 RU', uz: '🇺🇿 UZ' };

const dictionary = {
    en: {
        'hero-title': 'Natural Wellness<br>For Everyday Life', 'hero-subtitle': 'Curated essentials for your mind and body.',
        'cat-all': 'All', 'cat-health': 'Health', 'cat-coffee': 'Coffee', 'cat-tea': 'Tea',
        'search-ph': 'Search wellness products...', 'add': 'Add',
        'cart-title': 'Shopping Cart', 'cart-total': 'Total:', 'cart-empty': 'Your cart is empty.',
        'checkout-btn': 'Place Order', 'no-products': 'No products found', 'key-benefits': 'Key Benefits:'
    },
    ru: {
        'hero-title': 'Естественный баланс<br>Каждый День', 'hero-subtitle': 'Премиальные продукты для вашего разума и тела.',
        'cat-all': 'Все', 'cat-health': 'Здоровье', 'cat-coffee': 'Кофе', 'cat-tea': 'Чай',
        'search-ph': 'Поиск продуктов...', 'add': 'Добавить',
        'cart-title': 'Корзина', 'cart-total': 'Итого:', 'cart-empty': 'Корзина пуста.',
        'checkout-btn': 'Оформить заказ', 'no-products': 'Товары не найдены', 'key-benefits': 'Преимущества:'
    },
    uz: {
        'hero-title': 'Har kunlik hayot uchun<br>Tabiiy Salomatlik', 'hero-subtitle': 'Tana va ong uchun premium mahsulotlar.',
        'cat-all': 'Barchasi', 'cat-health': 'Salomatlik', 'cat-coffee': 'Kofe', 'cat-tea': 'Choy',
        'search-ph': 'Mahsulotlarni qidirish...', 'add': 'Qo\'shish',
        'cart-title': 'Savat', 'cart-total': 'Jami:', 'cart-empty': 'Savat bo\'sh.',
        'checkout-btn': 'Buyurtma berish', 'no-products': 'Mahsulotlar topilmadi', 'key-benefits': 'Xususiyatlari:'
    }
};

// Полная база с несколькими картинками для зума
const products = [
    {
        id: 'p1', category: 'coffee', price: 24.99,
        images: [
            'https://images.unsplash.com/photo-1559525839-b184a4d698c7?w=500&q=80',
            'https://images.unsplash.com/photo-1511920170033-f8396924c348?w=500&q=80'
        ],
        name: { en: 'Ganoderma Coffee', ru: 'Кофе с Ганодермой', uz: 'Ganoderma Kofe' },
        desc: { en: 'Premium arabica infused with organic extract.', ru: 'Арабика с органическим экстрактом Ганодермы.', uz: 'Organik ekstraktli arabika kofesi.' },
        benefits: { en: ['Boosts Immunity', 'Energy'], ru: ['Иммунитет', 'Энергия'], uz: ['Imunitetni oshiradi', 'Energiya'] }
    },
    {
        id: 'p2', category: 'tea', price: 18.50,
        images: [
            'https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=500&q=80',
            'https://images.unsplash.com/photo-1564890369478-c89ca6d9cde9?w=500&q=80'
        ],
        name: { en: 'Herbal Zen Tea', ru: 'Травяной Дзен Чай', uz: 'Zen O\'tli Choyi' },
        desc: { en: 'Calming blend of chamomile.', ru: 'Успокаивающая смесь ромашки для глубокого сна.', uz: 'Moychechakli tinchlantiruvchi choy.' },
        benefits: { en: ['Stress Relief', 'Sleep'], ru: ['Снятие стресса', 'Сон'], uz: ['Stressni kamaytirish', 'Uyqu'] }
    },
    {
        id: 'p3', category: 'health', price: 34.00,
        images: ['https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500&q=80'],
        name: { en: 'Cordyceps Caps', ru: 'Кордицепс Капсулы', uz: 'Cordyceps Kapsulalari' },
        desc: { en: 'Performance enhancer.', ru: 'Натуральный энергетик и поддержка дыхания.', uz: 'Nafas olishni yaxshilovchi.' },
        benefits: { en: ['Stamina'], ru: ['Выносливость'], uz: ['Chidamlilik'] }
    },
    {
        id: 'p4', category: 'coffee', price: 26.50,
        images: ['https://images.unsplash.com/photo-1550505096-7bbde10e9f1a?w=500&q=80'],
        name: { en: 'Lion\'s Mane Focus', ru: 'Кофе Ежовик', uz: 'Lion\'s Mane Kofe' },
        desc: { en: 'Focus and clarity.', ru: 'Для ясности ума и фокуса.', uz: 'Zehn ravshanligi uchun.' },
        benefits: { en: ['Focus'], ru: ['Фокус'], uz: ['Diqqat'] }
    }
];

function initTheme() {
    if (tg && tg.colorScheme) currentTheme = tg.colorScheme;
    document.documentElement.className = currentTheme;

    document.getElementById('theme-btn').addEventListener('click', () => {
        currentTheme = currentTheme === 'light' ? 'dark' : 'light';
        document.documentElement.className = currentTheme;
        localStorage.setItem('theme', currentTheme);
        if (tg && tg.HapticFeedback) tg.HapticFeedback.impactOccurred('light');
    });
}

function changeLanguage(lang) {
    currentLang = lang;
    localStorage.setItem('lang', lang);
    document.getElementById('lang-btn').textContent = flags[lang];
    document.getElementById('lang-dropdown').classList.add('hidden');

    document.querySelectorAll('[data-i18n]').forEach(elem => {
        const key = elem.getAttribute('data-i18n');
        if (dictionary[lang][key]) elem.innerHTML = dictionary[lang][key];
    });

    const searchInp = document.getElementById('search-input');
    if(searchInp) searchInp.placeholder = dictionary[lang]['search-ph'];

    runFilters();
    updateCartUI();
    if(currentModalProductId) openModal(currentModalProductId);
}

// --- Поиск и Рендер ---
function runFilters() {
    const activeChip = document.querySelector('.category-chip.active');
    const category = activeChip ? activeChip.dataset.category : 'all';
    const query = document.getElementById('search-input').value.toLowerCase();

    let filtered = products;
    if (category !== 'all') filtered = filtered.filter(p => p.category === category);
    if (query) filtered = filtered.filter(p => p.name[currentLang].toLowerCase().includes(query));

    renderProducts(filtered);
}

function renderProducts(items) {
    const grid = document.getElementById('products-section');
    if (!grid) return;

    if (items.length === 0) {
        grid.innerHTML = `<p style="grid-column:1/-1; text-align:center; color:var(--text-muted); padding:40px 0;">${dictionary[currentLang]['no-products']}</p>`;
        return;
    }

    grid.innerHTML = items.map(p => `
        <div class="product-card" onclick="openModal('${p.id}')">
            <img src="${p.images[0]}" class="product-img" loading="lazy">
            <h3 class="product-title">${p.name[currentLang]}</h3>
            <div class="product-price">$${p.price.toFixed(2)}</div>
            <div id="action-${p.id}" class="product-actions" onclick="event.stopPropagation()"></div>
        </div>
    `).join('');

    items.forEach(p => renderAction(p.id));
}

function renderAction(id) {
    const container = document.getElementById(`action-${id}`);
    const modalContainer = document.getElementById('modal-action-container');
    const cartItem = cart.find(c => c.id === id);

    const html = cartItem ? `
        <div class="qty-pill">
            <button class="pill-btn" onclick="updateQty('${id}', -1, event)">−</button>
            <span class="pill-count">${cartItem.qty}</span>
            <button class="pill-btn" onclick="updateQty('${id}', 1, event)">+</button>
        </div>
    ` : `
        <button class="btn-buy" onclick="handleAddToCart('${id}', event)">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
            ${dictionary[currentLang]['add']}
        </button>
    `;

    if (container) container.innerHTML = html;
    if (modalContainer && currentModalProductId === id) modalContainer.innerHTML = html;
}

function handleAddToCart(id, event) {
    if (event) event.stopPropagation();
    const product = products.find(p => p.id === id);
    cart.push({ ...product, qty: 1 });
    updateCartUI();
    renderAction(id);
    if (tg && tg.HapticFeedback) tg.HapticFeedback.impactOccurred('medium');
}

function updateQty(id, delta, event) {
    if (event) event.stopPropagation();
    const item = cart.find(i => i.id === id);
    if (!item) return;

    item.qty += delta;
    if (item.qty <= 0) cart = cart.filter(i => i.id !== id);

    updateCartUI();
    renderAction(id);
    if (tg && tg.HapticFeedback) tg.HapticFeedback.impactOccurred('light');
}

// --- Корзина (Receipt UI) ---
function updateCartUI() {
    const totalQty = cart.reduce((sum, item) => sum + item.qty, 0);
    const totalSum = cart.reduce((sum, item) => sum + (item.price * item.qty), 0);

    document.getElementById('cart-badge').textContent = totalQty;
    document.getElementById('cart-badge').classList.toggle('hidden', totalQty === 0);
    document.getElementById('cart-total-price').textContent = `$${totalSum.toFixed(2)}`;

    const cartItemsContainer = document.getElementById('cart-items');
    cartItemsContainer.innerHTML = cart.length === 0 ?
        `<p style="color: var(--text-muted); text-align: center; margin: 20px 0;">${dictionary[currentLang]['cart-empty']}</p>` :
        cart.map(item => `
            <div class="cart-item">
                <img src="${item.images[0]}" class="cart-item-img">
                <div class="cart-item-info">
                    <div class="cart-item-title">${item.name[currentLang]}</div>
                    <div class="cart-item-price">$${(item.price).toFixed(2)}</div>
                </div>
                <div class="cart-item-controls">
                    <button class="qty-btn" onclick="updateQty('${item.id}', -1)">-</button>
                    <span style="font-size:14px; font-weight:700;">${item.qty}</span>
                    <button class="qty-btn" onclick="updateQty('${item.id}', 1)">+</button>
                </div>
            </div>
        `).join('');

    if (tg && tg.MainButton) {
        if (cart.length > 0) {
            tg.MainButton.text = `${dictionary[currentLang]['checkout-btn'].toUpperCase()} ($${totalSum.toFixed(2)})`;
            tg.MainButton.show();
        } else { tg.MainButton.hide(); }
    }
}

// --- Модальное окно и Фотогалерея (Zoom) ---
function openModal(id) {
    const product = products.find(p => p.id === id);
    if (!product) return;
    currentModalProductId = id;

    // Галерея изображений
    document.getElementById('modal-gallery').innerHTML = product.images.map(img =>
        `<img src="${img}" class="modal-img" onclick="openViewer('${img}')">`
    ).join('');

    document.getElementById('modal-title').textContent = product.name[currentLang];
    document.getElementById('modal-price').textContent = `$${product.price.toFixed(2)}`;
    document.getElementById('modal-desc').textContent = product.desc[currentLang];
    document.getElementById('modal-benefits').innerHTML = `<strong>${dictionary[currentLang]['key-benefits']}</strong><ul>${product.benefits[currentLang].map(b => `<li>${b}</li>`).join('')}</ul>`;

    renderAction(id);

    document.getElementById('product-modal').classList.remove('hidden');
    setTimeout(() => document.getElementById('product-modal').classList.add('active'), 10);
}

function closeModal() {
    document.getElementById('product-modal').classList.remove('active');
    setTimeout(() => {
        document.getElementById('product-modal').classList.add('hidden');
        currentModalProductId = null;
    }, 300);
}

// Fullscreen Photo Zoom
function openViewer(src) {
    const viewer = document.getElementById('image-viewer');
    const img = document.getElementById('viewer-img');
    img.src = src;
    img.classList.remove('zoomed');
    viewer.classList.remove('hidden');
    setTimeout(() => viewer.classList.add('active'), 10);
}

function closeViewer() {
    const viewer = document.getElementById('image-viewer');
    viewer.classList.remove('active');
    setTimeout(() => viewer.classList.add('hidden'), 300);
}

document.getElementById('viewer-img').addEventListener('click', function(e) {
    e.stopPropagation();
    this.classList.toggle('zoomed');
});
document.getElementById('image-viewer').addEventListener('click', closeViewer);
document.getElementById('close-viewer').addEventListener('click', closeViewer);

// Закрытие модалки по клику на фон (Overlay)
document.getElementById('product-modal').addEventListener('click', (e) => {
    if (e.target.id === 'product-modal') closeModal();
});

// --- Checkout ---
document.getElementById('checkout-btn').addEventListener('click', () => {
    if (cart.length === 0) return;
    const orderData = {
        action: 'checkout', lang: currentLang,
        total: cart.reduce((sum, i) => sum + (i.price * i.qty), 0).toFixed(2),
        items: cart.map(i => ({ id: i.id, name: i.name.en, qty: i.qty, price: i.price }))
    };
    if (tg && tg.sendData) tg.sendData(JSON.stringify(orderData));
    else alert("Order Data:\n" + JSON.stringify(orderData, null, 2));
});

// --- Инициализация ---
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    changeLanguage(currentLang);

    // Lang Dropdown
    document.getElementById('lang-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        document.getElementById('lang-dropdown').classList.toggle('hidden');
    });
    document.addEventListener('click', () => document.getElementById('lang-dropdown').classList.add('hidden'));

    // Search
    document.getElementById('search-input').addEventListener('input', runFilters);

    // Categories
    document.querySelectorAll('.category-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            document.querySelectorAll('.category-chip').forEach(c => c.classList.remove('active'));
            chip.classList.add('active');
            runFilters();
        });
    });

    // Cart Handlers
    const openCart = () => {
        document.getElementById('cart-drawer').classList.remove('hidden');
        document.getElementById('cart-overlay').classList.remove('hidden');
        setTimeout(() => {
            document.getElementById('cart-drawer').classList.add('active');
            document.getElementById('cart-overlay').classList.add('active');
        }, 10);
    };
    const closeCart = () => {
        document.getElementById('cart-drawer').classList.remove('active');
        document.getElementById('cart-overlay').classList.remove('active');
        setTimeout(() => {
            document.getElementById('cart-drawer').classList.add('hidden');
            document.getElementById('cart-overlay').classList.add('hidden');
        }, 300);
    };

    document.getElementById('cart-btn').addEventListener('click', openCart);
    document.getElementById('close-cart').addEventListener('click', closeCart);
    document.getElementById('cart-overlay').addEventListener('click', closeCart);
    document.getElementById('close-modal').addEventListener('click', closeModal);
});