/* ── Telegram ── */
const tg = window.Telegram?.WebApp || null;
if (tg) { tg.expand(); tg.ready(); }

/* ── State ── */
let lang = localStorage.getItem('lang') || 'uz';
let theme = (tg?.colorScheme) || localStorage.getItem('theme') || 'light';
let cart = [];
let currentProduct = null;

/* ── i18n ── */
const T = {
    uz: {
        badge:'Gano Excel — №1 Dunyoda',
        heroTitle:'Sog\'liqni <em>Tabiiy</em> Kuchga<br>Aylantiring',
        heroSub:'Ganoderma Lucidum asosidagi premium mahsulotlar',
        searchPh:'Mahsulot qidiring...',
        cartTitle:'Savat',totalLabel:'Jami:',
        checkout:'Buyurtma berish',
        empty:'Savat bo\'sh',
        noProducts:'Mahsulot topilmadi',
        add:'Qo\'shish',
        aboutTitle:'Mahsulot haqida',
        benefitsTitle:'Foydalar',
        compTitle:'Tarkibida',
        usageTitle:'Qo\'llash',
        volume:'Hajmi / Qadoq',
        perDay:'/ kun'
    },
    ru: {
        badge:'Gano Excel — №1 в мире',
        heroTitle:'Превратите здоровье<br>в <em>Природную</em> силу',
        heroSub:'Премиум продукты на основе Ganoderma Lucidum',
        searchPh:'Поиск продукта...',
        cartTitle:'Корзина',totalLabel:'Итого:',
        checkout:'Оформить заказ',
        empty:'Корзина пуста',
        noProducts:'Товары не найдены',
        add:'Добавить',
        aboutTitle:'О продукте',
        benefitsTitle:'Польза',
        compTitle:'Состав',
        usageTitle:'Применение',
        volume:'Объём / Упаковка',
        perDay:'/ сутки'
    }
};

/* ── Products ── */
const products = [
    {
        id:'p1',
        badge:{uz:'Bestseller',ru:'Хит'},badgeType:'',
        images:[
            'https://gano.uz/wp-content/uploads/2023/03/reishi-gold-big.png',
            'https://avatars.mds.yandex.net/get-mpic/11402506/2a0000019944a07a6a5d9e22b9094bffd543/orig'
        ],
        name:{uz:'Reishi Gold',ru:'Reishi Gold'},
        brand:'Gano Excel',
        price:1215000,
        volume:{uz:'100 kapsula',ru:'100 капсул'},
        tags:{uz:['immunitet','quvvat','detoks'],ru:['иммунитет','энергия','детокс']},
        about:{
            uz:'Reishi Gold-Инсон танасидаги ички ва ташқи мувозанатни бошқарувчи ягона гиёх -Табиат туҳфасидир.<br>Хозирги замон Илм – Фан олимларининг -Америка фармакопияси Reishi Ganoderma<br>Lucidum тўғрисидаги нашрида ҳам ўз тасдиғини топган.',
            ru:'Reishi Gold — иммунологический продукт на основе органического экстракта Ganoderma Lucidum. 1 капсула содержит экстракт из 240 грибов Ganoderma Lucidum, выращенных и вызревших за 12 недель (полное созревание за 3 месяца).'
        },
        benefits:{
            uz:['Иммун тизимини қувватлайди','Организмни токсинлардан тозалайди','Юрак қон – томир тизимини қувватлайди','Қонда қанд миқдорини пасайтиради','Асаб тизимини тинчлантиради, руҳий холатни яхшилайди','Жигар тозалайди', 'Нафас олиш тизмини яхшилайди', 'Ўсмага қарши'],
            ru:['Укрепляет иммунитет','Очищает организм','Повышает энергию','Нормализует давление','Уменьшает воспаления','Улучшает сон']
        },
        composition:{
            uz:['Полисахаридлар','Органик Германий','Аденозин','Ганодерма экстракти','Тритерпеноидлар','Оқсиллар', 'Аминокислоталар'],
            ru:['Полисахариды','Органический германий','Витамины','Минералы','Ферменты','Белки']
        },
        usage:{
            uz:'Профилактика мақсадида кунига 1 капсуладан ичиш тавсия этилади. Касаллик пайтида кунига 2-4 капсуладан. Энг яхши натижага EXCELLIUM GOLD (Ехcелиум Голд) билан биргаликда эришиш мумкин.',
            ru:'1–2 капсулы 2 раза в день. Для более эффективного результата рекомендуется до 6 капсул. Рекомендуется принимать совместно с Excellium Gold.'
        }
    },
    {
        id:'p2',
        badge:{uz:'Yangi',ru:'Новинка'},badgeType:'gold',
        images:[
            'https://gano.uz/wp-content/uploads/2023/03/excellium-gold.png'
        ],
        name:{uz:'Excellium Gold',ru:'Excellium Gold'},
        brand:'Gano Excel',
        price:185000,
        volume:{uz:'XXX kapsula',ru:'XXX капсул'},
        tags:{uz:['miya','asab','intellekt'],ru:['мозг','нервы','интеллект']},
        about:{
            uz:'ABOUT.',
            ru:'ABOUT.'
        },
        benefits:{
            uz:['ggggggggg'],
            ru:['ggggggggg']
        },
        composition:{
            uz:['xxxxxxx','xxxxx xxxx','xxxx','xxxxx','xxxxxx','xxxxx','xxxxxx'],
            ru:['xxxxx','xxxxxxxx','xxxxx','xxxxx','xxxxxx','xxxxxxx','xxxxxxxx']
        },
        usage:{
            uz:'usage.',
            ru:'usage.'
        }
    },
    {
        id:'p3',
        badge:{uz:'Yangi',ru:'Новинка'},badgeType:'gold',
        images:[
            'https://gano.uz/wp-content/uploads/2023/03/excellium-gold.png'
        ],
        name:{uz:'Excellium Gold',ru:'Excellium Gold'},
        brand:'Gano Excel',
        price:185000,
        volume:{uz:'XXX kapsula',ru:'XXX капсул'},
        tags:{uz:['miya','asab','intellekt'],ru:['мозг','нервы','интеллект']},
        about:{
            uz:'ABOUT.',
            ru:'ABOUT.'
        },
        benefits:{
            uz:['ggggggggg'],
            ru:['ggggggggg']
        },
        composition:{
            uz:['xxxxxxx','xxxxx xxxx','xxxx','xxxxx','xxxxxx','xxxxx','xxxxxx'],
            ru:['xxxxx','xxxxxxxx','xxxxx','xxxxx','xxxxxx','xxxxxxx','xxxxxxxx']
        },
        usage:{
            uz:'usage.',
            ru:'usage.'
        }
    },
    {
        id:'p4',
        badge:{uz:'Yangi',ru:'Новинка'},badgeType:'gold',
        images:[
            'https://gano.uz/wp-content/uploads/2023/03/excellium-gold.png'
        ],
        name:{uz:'Excellium Gold',ru:'Excellium Gold'},
        brand:'Gano Excel',
        price:185000,
        volume:{uz:'XXX kapsula',ru:'XXX капсул'},
        tags:{uz:['miya','asab','intellekt'],ru:['мозг','нервы','интеллект']},
        about:{
            uz:'ABOUT.',
            ru:'ABOUT.'
        },
        benefits:{
            uz:['ggggggggg'],
            ru:['ggggggggg']
        },
        composition:{
            uz:['xxxxxxx','xxxxx xxxx','xxxx','xxxxx','xxxxxx','xxxxx','xxxxxx'],
            ru:['xxxxx','xxxxxxxx','xxxxx','xxxxx','xxxxxx','xxxxxxx','xxxxxxxx']
        },
        usage:{
            uz:'usage.',
            ru:'usage.'
        }
    },
    {
        id:'p5',
        badge:{uz:'Yangi',ru:'Новинка'},badgeType:'gold',
        images:[
            'https://gano.uz/wp-content/uploads/2023/03/excellium-gold.png'
        ],
        name:{uz:'Excellium Gold',ru:'Excellium Gold'},
        brand:'Gano Excel',
        price:185000,
        volume:{uz:'XXX kapsula',ru:'XXX капсул'},
        tags:{uz:['miya','asab','intellekt'],ru:['мозг','нервы','интеллект']},
        about:{
            uz:'ABOUT.',
            ru:'ABOUT.'
        },
        benefits:{
            uz:['ggggggggg'],
            ru:['ggggggggg']
        },
        composition:{
            uz:['xxxxxxx','xxxxx xxxx','xxxx','xxxxx','xxxxxx','xxxxx','xxxxxx'],
            ru:['xxxxx','xxxxxxxx','xxxxx','xxxxx','xxxxxx','xxxxxxx','xxxxxxxx']
        },
        usage:{
            uz:'usage.',
            ru:'usage.'
        }
    },
    {
        id:'p6',
        badge:{uz:'Yangi',ru:'Новинка'},badgeType:'gold',
        images:[
            'https://gano.uz/wp-content/uploads/2023/03/excellium-gold.png'
        ],
        name:{uz:'Excellium Gold',ru:'Excellium Gold'},
        brand:'Gano Excel',
        price:185000,
        volume:{uz:'XXX kapsula',ru:'XXX капсул'},
        tags:{uz:['miya','asab','intellekt'],ru:['мозг','нервы','интеллект']},
        about:{
            uz:'ABOUT.',
            ru:'ABOUT.'
        },
        benefits:{
            uz:['ggggggggg'],
            ru:['ggggggggg']
        },
        composition:{
            uz:['xxxxxxx','xxxxx xxxx','xxxx','xxxxx','xxxxxx','xxxxx','xxxxxx'],
            ru:['xxxxx','xxxxxxxx','xxxxx','xxxxx','xxxxxx','xxxxxxx','xxxxxxxx']
        },
        usage:{
            uz:'usage.',
            ru:'usage.'
        }
    },
    {
        id:'p7',
        badge:{uz:'Yangi',ru:'Новинка'},badgeType:'gold',
        images:[
            'https://gano.uz/wp-content/uploads/2023/03/excellium-gold.png'
        ],
        name:{uz:'Excellium Gold',ru:'Excellium Gold'},
        brand:'Gano Excel',
        price:185000,
        volume:{uz:'XXX kapsula',ru:'XXX капсул'},
        tags:{uz:['miya','asab','intellekt'],ru:['мозг','нервы','интеллект']},
        about:{
            uz:'ABOUT.',
            ru:'ABOUT.'
        },
        benefits:{
            uz:['ggggggggg'],
            ru:['ggggggggg']
        },
        composition:{
            uz:['xxxxxxx','xxxxx xxxx','xxxx','xxxxx','xxxxxx','xxxxx','xxxxxx'],
            ru:['xxxxx','xxxxxxxx','xxxxx','xxxxx','xxxxxx','xxxxxxx','xxxxxxxx']
        },
        usage:{
            uz:'usage.',
            ru:'usage.'
        }
    },
    {
        id:'p8',
        badge:{uz:'Yangi',ru:'Новинка'},badgeType:'gold',
        images:[
            'https://gano.uz/wp-content/uploads/2023/03/excellium-gold.png'
        ],
        name:{uz:'Excellium Gold',ru:'Excellium Gold'},
        brand:'Gano Excel',
        price:185000,
        volume:{uz:'XXX kapsula',ru:'XXX капсул'},
        tags:{uz:['miya','asab','intellekt'],ru:['мозг','нервы','интеллект']},
        about:{
            uz:'ABOUT.',
            ru:'ABOUT.'
        },
        benefits:{
            uz:['ggggggggg'],
            ru:['ggggggggg']
        },
        composition:{
            uz:['xxxxxxx','xxxxx xxxx','xxxx','xxxxx','xxxxxx','xxxxx','xxxxxx'],
            ru:['xxxxx','xxxxxxxx','xxxxx','xxxxx','xxxxxx','xxxxxxx','xxxxxxxx']
        },
        usage:{
            uz:'usage.',
            ru:'usage.'
        }
    },
    {
        id:'p9',
        badge:{uz:'Yangi',ru:'Новинка'},badgeType:'gold',
        images:[
            'https://gano.uz/wp-content/uploads/2023/03/excellium-gold.png'
        ],
        name:{uz:'Excellium Gold',ru:'Excellium Gold'},
        brand:'Gano Excel',
        price:185000,
        volume:{uz:'XXX kapsula',ru:'XXX капсул'},
        tags:{uz:['miya','asab','intellekt'],ru:['мозг','нервы','интеллект']},
        about:{
            uz:'ABOUT.',
            ru:'ABOUT.'
        },
        benefits:{
            uz:['ggggggggg'],
            ru:['ggggggggg']
        },
        composition:{
            uz:['xxxxxxx','xxxxx xxxx','xxxx','xxxxx','xxxxxx','xxxxx','xxxxxx'],
            ru:['xxxxx','xxxxxxxx','xxxxx','xxxxx','xxxxxx','xxxxxxx','xxxxxxxx']
        },
        usage:{
            uz:'usage.',
            ru:'usage.'
        }
    },
    {
        id:'p10',
        badge:{uz:'Yangi',ru:'Новинка'},badgeType:'gold',
        images:[
            'https://gano.uz/wp-content/uploads/2023/03/excellium-gold.png'
        ],
        name:{uz:'Excellium Gold',ru:'Excellium Gold'},
        brand:'Gano Excel',
        price:185000,
        volume:{uz:'XXX kapsula',ru:'XXX капсул'},
        tags:{uz:['miya','asab','intellekt'],ru:['мозг','нервы','интеллект']},
        about:{
            uz:'ABOUT.',
            ru:'ABOUT.'
        },
        benefits:{
            uz:['ggggggggg'],
            ru:['ggggggggg']
        },
        composition:{
            uz:['xxxxxxx','xxxxx xxxx','xxxx','xxxxx','xxxxxx','xxxxx','xxxxxx'],
            ru:['xxxxx','xxxxxxxx','xxxxx','xxxxx','xxxxxx','xxxxxxx','xxxxxxxx']
        },
        usage:{
            uz:'usage.',
            ru:'usage.'
        }
    },
    {
        id:'p11',
        badge:{uz:'Yangi',ru:'Новинка'},badgeType:'gold',
        images:[
            'https://gano.uz/wp-content/uploads/2023/03/excellium-gold.png'
        ],
        name:{uz:'Excellium Gold',ru:'Excellium Gold'},
        brand:'Gano Excel',
        price:185000,
        volume:{uz:'XXX kapsula',ru:'XXX капсул'},
        tags:{uz:['miya','asab','intellekt'],ru:['мозг','нервы','интеллект']},
        about:{
            uz:'ABOUT.',
            ru:'ABOUT.'
        },
        benefits:{
            uz:['ggggggggg'],
            ru:['ggggggggg']
        },
        composition:{
            uz:['xxxxxxx','xxxxx xxxx','xxxx','xxxxx','xxxxxx','xxxxx','xxxxxx'],
            ru:['xxxxx','xxxxxxxx','xxxxx','xxxxx','xxxxxx','xxxxxxx','xxxxxxxx']
        },
        usage:{
            uz:'usage.',
            ru:'usage.'
        }
    },
    {
        id:'p12',
        badge:{uz:'Yangi',ru:'Новинка'},badgeType:'gold',
        images:[
            'https://gano.uz/wp-content/uploads/2023/03/excellium-gold.png'
        ],
        name:{uz:'Excellium Gold',ru:'Excellium Gold'},
        brand:'Gano Excel',
        price:185000,
        volume:{uz:'XXX kapsula',ru:'XXX капсул'},
        tags:{uz:['miya','asab','intellekt'],ru:['мозг','нервы','интеллект']},
        about:{
            uz:'ABOUT.',
            ru:'ABOUT.'
        },
        benefits:{
            uz:['ggggggggg'],
            ru:['ggggggggg']
        },
        composition:{
            uz:['xxxxxxx','xxxxx xxxx','xxxx','xxxxx','xxxxxx','xxxxx','xxxxxx'],
            ru:['xxxxx','xxxxxxxx','xxxxx','xxxxx','xxxxxx','xxxxxxx','xxxxxxxx']
        },
        usage:{
            uz:'usage.',
            ru:'usage.'
        }
    },
    {
        id:'p13',
        badge:{uz:'Yangi',ru:'Новинка'},badgeType:'gold',
        images:[
            'https://gano.uz/wp-content/uploads/2023/03/excellium-gold.png'
        ],
        name:{uz:'Excellium Gold',ru:'Excellium Gold'},
        brand:'Gano Excel',
        price:185000,
        volume:{uz:'XXX kapsula',ru:'XXX капсул'},
        tags:{uz:['miya','asab','intellekt'],ru:['мозг','нервы','интеллект']},
        about:{
            uz:'ABOUT.',
            ru:'ABOUT.'
        },
        benefits:{
            uz:['ggggggggg'],
            ru:['ggggggggg']
        },
        composition:{
            uz:['xxxxxxx','xxxxx xxxx','xxxx','xxxxx','xxxxxx','xxxxx','xxxxxx'],
            ru:['xxxxx','xxxxxxxx','xxxxx','xxxxx','xxxxxx','xxxxxxx','xxxxxxxx']
        },
        usage:{
            uz:'usage.',
            ru:'usage.'
        }
    },
    {
        id:'p13',
        badge:{uz:'Yangi',ru:'Новинка'},badgeType:'gold',
        images:[
            'https://gano.uz/wp-content/uploads/2023/03/excellium-gold.png'
        ],
        name:{uz:'Excellium Gold',ru:'Excellium Gold'},
        brand:'Gano Excel',
        price:185000,
        volume:{uz:'XXX kapsula',ru:'XXX капсул'},
        tags:{uz:['miya','asab','intellekt'],ru:['мозг','нервы','интеллект']},
        about:{
            uz:'ABOUT.',
            ru:'ABOUT.'
        },
        benefits:{
            uz:['ggggggggg'],
            ru:['ggggggggg']
        },
        composition:{
            uz:['xxxxxxx','xxxxx xxxx','xxxx','xxxxx','xxxxxx','xxxxx','xxxxxx'],
            ru:['xxxxx','xxxxxxxx','xxxxx','xxxxx','xxxxxx','xxxxxxx','xxxxxxxx']
        },
        usage:{
            uz:'usage.',
            ru:'usage.'
        }
    },
    {
        id:'p14',
        badge:{uz:'Yangi',ru:'Новинка'},badgeType:'gold',
        images:[
            'https://gano.uz/wp-content/uploads/2023/03/excellium-gold.png'
        ],
        name:{uz:'Excellium Gold',ru:'Excellium Gold'},
        brand:'Gano Excel',
        price:185000,
        volume:{uz:'XXX kapsula',ru:'XXX капсул'},
        tags:{uz:['miya','asab','intellekt'],ru:['мозг','нервы','интеллект']},
        about:{
            uz:'ABOUT.',
            ru:'ABOUT.'
        },
        benefits:{
            uz:['ggggggggg'],
            ru:['ggggggggg']
        },
        composition:{
            uz:['xxxxxxx','xxxxx xxxx','xxxx','xxxxx','xxxxxx','xxxxx','xxxxxx'],
            ru:['xxxxx','xxxxxxxx','xxxxx','xxxxx','xxxxxx','xxxxxxx','xxxxxxxx']
        },
        usage:{
            uz:'usage.',
            ru:'usage.'
        }
    },
    {
        id:'p15',
        badge:{uz:'Yangi',ru:'Новинка'},badgeType:'gold',
        images:[
            'https://gano.uz/wp-content/uploads/2023/03/excellium-gold.png'
        ],
        name:{uz:'Excellium Gold',ru:'Excellium Gold'},
        brand:'Gano Excel',
        price:185000,
        volume:{uz:'XXX kapsula',ru:'XXX капсул'},
        tags:{uz:['miya','asab','intellekt'],ru:['мозг','нервы','интеллект']},
        about:{
            uz:'ABOUT.',
            ru:'ABOUT.'
        },
        benefits:{
            uz:['ggggggggg'],
            ru:['ggggggggg']
        },
        composition:{
            uz:['xxxxxxx','xxxxx xxxx','xxxx','xxxxx','xxxxxx','xxxxx','xxxxxx'],
            ru:['xxxxx','xxxxxxxx','xxxxx','xxxxx','xxxxxx','xxxxxxx','xxxxxxxx']
        },
        usage:{
            uz:'usage.',
            ru:'usage.'
        }
    },
    {
        id:'p16',
        badge:{uz:'Yangi',ru:'Новинка'},badgeType:'gold',
        images:[
            'https://gano.uz/wp-content/uploads/2023/03/excellium-gold.png'
        ],
        name:{uz:'Excellium Gold',ru:'Excellium Gold'},
        brand:'Gano Excel',
        price:185000,
        volume:{uz:'XXX kapsula',ru:'XXX капсул'},
        tags:{uz:['miya','asab','intellekt'],ru:['мозг','нервы','интеллект']},
        about:{
            uz:'ABOUT.',
            ru:'ABOUT.'
        },
        benefits:{
            uz:['ggggggggg'],
            ru:['ggggggggg']
        },
        composition:{
            uz:['xxxxxxx','xxxxx xxxx','xxxx','xxxxx','xxxxxx','xxxxx','xxxxxx'],
            ru:['xxxxx','xxxxxxxx','xxxxx','xxxxx','xxxxxx','xxxxxxx','xxxxxxxx']
        },
        usage:{
            uz:'usage.',
            ru:'usage.'
        }
    },
    {
        id:'p17',
        badge:{uz:'Yangi',ru:'Новинка'},badgeType:'gold',
        images:[
            'https://gano.uz/wp-content/uploads/2023/03/excellium-gold.png'
        ],
        name:{uz:'Excellium Gold',ru:'Excellium Gold'},
        brand:'Gano Excel',
        price:185000,
        volume:{uz:'XXX kapsula',ru:'XXX капсул'},
        tags:{uz:['miya','asab','intellekt'],ru:['мозг','нервы','интеллект']},
        about:{
            uz:'ABOUT.',
            ru:'ABOUT.'
        },
        benefits:{
            uz:['ggggggggg'],
            ru:['ggggggggg']
        },
        composition:{
            uz:['xxxxxxx','xxxxx xxxx','xxxx','xxxxx','xxxxxx','xxxxx','xxxxxx'],
            ru:['xxxxx','xxxxxxxx','xxxxx','xxxxx','xxxxxx','xxxxxxx','xxxxxxxx']
        },
        usage:{
            uz:'usage.',
            ru:'usage.'
        }
    },
    {
        id:'p18',
        badge:{uz:'Yangi',ru:'Новинка'},badgeType:'gold',
        images:[
            'https://gano.uz/wp-content/uploads/2023/03/excellium-gold.png'
        ],
        name:{uz:'Excellium Gold',ru:'Excellium Gold'},
        brand:'Gano Excel',
        price:185000,
        volume:{uz:'XXX kapsula',ru:'XXX капсул'},
        tags:{uz:['miya','asab','intellekt'],ru:['мозг','нервы','интеллект']},
        about:{
            uz:'ABOUT.',
            ru:'ABOUT.'
        },
        benefits:{
            uz:['ggggggggg'],
            ru:['ggggggggg']
        },
        composition:{
            uz:['xxxxxxx','xxxxx xxxx','xxxx','xxxxx','xxxxxx','xxxxx','xxxxxx'],
            ru:['xxxxx','xxxxxxxx','xxxxx','xxxxx','xxxxxx','xxxxxxx','xxxxxxxx']
        },
        usage:{
            uz:'usage.',
            ru:'usage.'
        }
    },
    {
        id:'p19',
        badge:{uz:'Yangi',ru:'Новинка'},badgeType:'gold',
        images:[
            'https://gano.uz/wp-content/uploads/2023/03/excellium-gold.png'
        ],
        name:{uz:'Excellium Gold',ru:'Excellium Gold'},
        brand:'Gano Excel',
        price:185000,
        volume:{uz:'XXX kapsula',ru:'XXX капсул'},
        tags:{uz:['miya','asab','intellekt'],ru:['мозг','нервы','интеллект']},
        about:{
            uz:'ABOUT.',
            ru:'ABOUT.'
        },
        benefits:{
            uz:['ggggggggg'],
            ru:['ggggggggg']
        },
        composition:{
            uz:['xxxxxxx','xxxxx xxxx','xxxx','xxxxx','xxxxxx','xxxxx','xxxxxx'],
            ru:['xxxxx','xxxxxxxx','xxxxx','xxxxx','xxxxxx','xxxxxxx','xxxxxxxx']
        },
        usage:{
            uz:'usage.',
            ru:'usage.'
        }
    },
    {
        id:'p2',
        badge:{uz:'Yangi',ru:'Новинка'},badgeType:'gold',
        images:[
            'https://gano.uz/wp-content/uploads/2023/03/excellium-gold.png'
        ],
        name:{uz:'Excellium Gold',ru:'Excellium Gold'},
        brand:'Gano Excel',
        price:185000,
        volume:{uz:'XXX kapsula',ru:'XXX капсул'},
        tags:{uz:['miya','asab','intellekt'],ru:['мозг','нервы','интеллект']},
        about:{
            uz:'ABOUT.',
            ru:'ABOUT.'
        },
        benefits:{
            uz:['ggggggggg'],
            ru:['ggggggggg']
        },
        composition:{
            uz:['xxxxxxx','xxxxx xxxx','xxxx','xxxxx','xxxxxx','xxxxx','xxxxxx'],
            ru:['xxxxx','xxxxxxxx','xxxxx','xxxxx','xxxxxx','xxxxxxx','xxxxxxxx']
        },
        usage:{
            uz:'usage.',
            ru:'usage.'
        }
    },
    {
        id:'p2',
        badge:{uz:'Yangi',ru:'Новинка'},badgeType:'gold',
        images:[
            'https://gano.uz/wp-content/uploads/2023/03/excellium-gold.png'
        ],
        name:{uz:'Excellium Gold',ru:'Excellium Gold'},
        brand:'Gano Excel',
        price:185000,
        volume:{uz:'XXX kapsula',ru:'XXX капсул'},
        tags:{uz:['miya','asab','intellekt'],ru:['мозг','нервы','интеллект']},
        about:{
            uz:'ABOUT.',
            ru:'ABOUT.'
        },
        benefits:{
            uz:['ggggggggg'],
            ru:['ggggggggg']
        },
        composition:{
            uz:['xxxxxxx','xxxxx xxxx','xxxx','xxxxx','xxxxxx','xxxxx','xxxxxx'],
            ru:['xxxxx','xxxxxxxx','xxxxx','xxxxx','xxxxxx','xxxxxxx','xxxxxxxx']
        },
        usage:{
            uz:'usage.',
            ru:'usage.'
        }
    },
    {
        id:'p2',
        badge:{uz:'Yangi',ru:'Новинка'},badgeType:'gold',
        images:[
            'https://gano.uz/wp-content/uploads/2023/03/excellium-gold.png'
        ],
        name:{uz:'Excellium Gold',ru:'Excellium Gold'},
        brand:'Gano Excel',
        price:185000,
        volume:{uz:'XXX kapsula',ru:'XXX капсул'},
        tags:{uz:['miya','asab','intellekt'],ru:['мозг','нервы','интеллект']},
        about:{
            uz:'ABOUT.',
            ru:'ABOUT.'
        },
        benefits:{
            uz:['ggggggggg'],
            ru:['ggggggggg']
        },
        composition:{
            uz:['xxxxxxx','xxxxx xxxx','xxxx','xxxxx','xxxxxx','xxxxx','xxxxxx'],
            ru:['xxxxx','xxxxxxxx','xxxxx','xxxxx','xxxxxx','xxxxxxx','xxxxxxxx']
        },
        usage:{
            uz:'usage.',
            ru:'usage.'
        }
    }
];

/* ── Format price ── */
function fmtPrice(n){
    return n.toLocaleString('uz-UZ').replace(/,/g,'\u00a0') + '\u00a0so\'m';
}

/* ── Theme ── */
function applyTheme(t){
    theme=t;
    document.documentElement.className=t;
    localStorage.setItem('theme',t);
}
document.getElementById('theme-btn').onclick=()=>{
    applyTheme(theme==='light'?'dark':'light');
    tg?.HapticFeedback?.impactOccurred('light');
};
applyTheme(theme);

/* ── Language ── */
function setLang(l){
    lang=l;
    localStorage.setItem('lang',l);
    document.getElementById('lang-btn').textContent = l==='uz'?'🇺🇿':'🇷🇺';
    document.getElementById('lang-dropdown').classList.add('hidden');
    applyI18n();
    renderProducts(products);
    updateCart();
    if(currentProduct) openModal(currentProduct.id);
}
function applyI18n(){
    const t=T[lang];
    document.getElementById('hero-badge').innerHTML='● '+t.badge;
    document.getElementById('hero-title').innerHTML=t.heroTitle;
    document.getElementById('hero-sub').textContent=t.heroSub;
    document.getElementById('search-input').placeholder=t.searchPh;
    document.getElementById('cart-title-txt').textContent=t.cartTitle;
    document.getElementById('cart-total-label').textContent=t.totalLabel;
    document.getElementById('checkout-btn').textContent=t.checkout;
}
document.getElementById('lang-btn').onclick=e=>{
    e.stopPropagation();
    document.getElementById('lang-dropdown').classList.toggle('hidden');
};
document.addEventListener('click',()=>document.getElementById('lang-dropdown').classList.add('hidden'));

/* ── Smart Search ── */
function tokenize(str){ return str.toLowerCase().replace(/'/g,'\'').split(/\s+/); }
function scoreProduct(p, q){
    if(!q) return 1;
    const name = p.name[lang].toLowerCase();
    const tags = (p.tags[lang]||[]).join(' ');
    const about = (p.about[lang]||'').toLowerCase();
    const tokens = tokenize(q);
    let score = 0;
    for(const tok of tokens){
        if(name.includes(tok)) score+=10;
        else if(tags.includes(tok)) score+=5;
        else if(about.includes(tok)) score+=2;
    }
    return score;
}

let searchTimeout=null;
document.getElementById('search-input').addEventListener('input',function(){
    clearTimeout(searchTimeout);
    const q=this.value.trim();
    searchTimeout=setTimeout(()=>{
        if(q.length>1){
            const matches=products
                .map(p=>({p,s:scoreProduct(p,q)}))
                .filter(x=>x.s>0)
                .sort((a,b)=>b.s-a.s);
            showSuggestions(matches.map(x=>x.p),q);
            renderProducts(matches.map(x=>x.p));
        } else {
            document.getElementById('suggestions').classList.add('hidden');
            renderProducts(products);
        }
    },120);
});

function showSuggestions(items,q){
    const el=document.getElementById('suggestions');
    if(!items.length){el.classList.add('hidden');return;}
    el.innerHTML=items.slice(0,4).map(p=>`
        <div class="suggestion-item" onclick="openModal('${p.id}');document.getElementById('suggestions').classList.add('hidden')">
            <div class="suggestion-icon">🌿</div>
            <div class="suggestion-name">${p.name[lang]}</div>
            <div class="suggestion-price">${fmtPrice(p.price)}</div>
        </div>
    `).join('');
    el.classList.remove('hidden');
}
document.getElementById('search-input').addEventListener('focus',function(){
    if(this.value.length>1) document.getElementById('suggestions').classList.remove('hidden');
});
document.addEventListener('click',e=>{
    if(!e.target.closest('.search-wrap')&&!e.target.closest('.suggestions'))
        document.getElementById('suggestions').classList.add('hidden');
});

/* ── Render Products ── */
function renderProducts(items){
    const grid=document.getElementById('products-grid');
    if(!items.length){
        grid.innerHTML=`<div class="empty-state"><div class="emoji">🌿</div><p>${T[lang].noProducts}</p></div>`;
        return;
    }
    grid.innerHTML=items.map(p=>{
        const inCart=cart.find(c=>c.id===p.id);
        return `
        <div class="product-card" onclick="openModal('${p.id}')">
            <div class="product-img-wrap">
                <img src="${p.images[0]}" class="product-img" loading="lazy" onerror="this.style.background='var(--surface2)'">
                <span class="product-badge${p.badgeType==='gold'?' gold':''}">${p.badge[lang]}</span>
            </div>
            <div class="product-body">
                <div class="product-title">${p.name[lang]}</div>
                <div class="product-price-wrap">
                    <div class="product-price">${fmtPrice(p.price)}</div>
                    <div class="product-price-sub">${p.volume[lang]}</div>
                </div>
                <div class="product-actions" id="pa-${p.id}" onclick="event.stopPropagation()">
                    ${actionHTML(p.id)}
                </div>
            </div>
        </div>`;
    }).join('');
}

function actionHTML(id){
    const item=cart.find(c=>c.id===id);
    if(item) return `
        <div class="qty-pill">
            <button class="pill-btn" onclick="changeQty('${id}',-1,event)">−</button>
            <span class="pill-count">${item.qty}</span>
            <button class="pill-btn" onclick="changeQty('${id}',1,event)">+</button>
        </div>`;
    return `
        <button class="btn-add" onclick="addToCart('${id}',event)">
            <svg viewBox="0 0 24 24" width="13" height="13" stroke="#fff" fill="none" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            ${T[lang].add}
        </button>`;
}

function refreshAction(id){
    const pa=document.getElementById('pa-'+id);
    if(pa) pa.innerHTML=actionHTML(id);
    const ma=document.getElementById('modal-action-'+id);
    if(ma) ma.innerHTML=actionHTML(id);
}

function addToCart(id,e){
    e?.stopPropagation();
    if(!cart.find(c=>c.id===id)){
        const p=products.find(p=>p.id===id);
        cart.push({...p,qty:1});
    }
    refreshAction(id);
    updateCart();
    tg?.HapticFeedback?.impactOccurred('medium');
}
function changeQty(id,d,e){
    e?.stopPropagation();
    const i=cart.find(c=>c.id===id);
    if(!i)return;
    i.qty+=d;
    if(i.qty<=0) cart=cart.filter(c=>c.id!==id);
    refreshAction(id);
    updateCart();
    tg?.HapticFeedback?.impactOccurred('light');
}

/* ── Cart UI ── */
function updateCart(){
    const qty=cart.reduce((s,i)=>s+i.qty,0);
    const total=cart.reduce((s,i)=>s+i.price*i.qty,0);

    const badge=document.getElementById('cart-badge');
    badge.textContent=qty;
    badge.classList.toggle('hidden',qty===0);

    document.getElementById('cart-total-val').textContent=fmtPrice(total);

    const container=document.getElementById('cart-items');
    if(!cart.length){
        container.innerHTML=`<p style="color:var(--muted);text-align:center;padding:28px 0;">${T[lang].empty}</p>`;
    } else {
        container.innerHTML=cart.map(item=>`
            <div class="cart-item">
                <img class="ci-img" src="${item.images[0]}" onerror="this.style.background='var(--surface2)'">
                <div class="ci-info">
                    <div class="ci-name">${item.name[lang]}</div>
                    <div class="ci-price">${fmtPrice(item.price)} × ${item.qty}</div>
                </div>
                <div class="ci-ctrl">
                    <button onclick="changeQty('${item.id}',-1)">−</button>
                    <span class="ci-qty">${item.qty}</span>
                    <button onclick="changeQty('${item.id}',1)">+</button>
                </div>
            </div>
        `).join('');
    }

    if(tg?.MainButton){
        if(cart.length>0){
            tg.MainButton.text=`${T[lang].checkout.toUpperCase()} — ${fmtPrice(total)}`;
            tg.MainButton.show();
        } else tg.MainButton.hide();
    }
}

/* Логика полной очистки корзины */
document.getElementById('clear-cart-btn').onclick = () => {
    if (cart.length === 0) return;

    // Сохраняем ID перед очисткой для обновления UI кнопок
    const oldCartIds = cart.map(item => item.id);
    cart = [];

    // Сбрасываем внешний вид кнопок всех очищенных товаров
    oldCartIds.forEach(id => refreshAction(id));

    updateCart();
    tg?.HapticFeedback?.impactOccurred('medium');
};

/* ── Modal ── */
function openModal(id){
    const p=products.find(x=>x.id===id);
    if(!p)return;
    currentProduct=p;

    document.getElementById('gallery-row').innerHTML=p.images.map((src,i)=>
        `<img src="${src}" class="gallery-img" loading="lazy" onclick="openViewer('${src}')" onerror="this.style.background='var(--surface2)'">`
    ).join('');

    const t=T[lang];
    document.getElementById('detail-body').innerHTML=`
        <div class="detail-brand">${p.brand}</div>
        <div class="detail-title">${p.name[lang]}</div>

        <div class="detail-price-card">
            <div>
                <div class="detail-price-main">${fmtPrice(p.price)}</div>
                <div class="detail-price-label">${p.volume[lang]}</div>
            </div>
            <div class="detail-action-wrap" id="modal-action-${p.id}">
                ${actionHTML(p.id)}
            </div>
        </div>

        <div class="desc-section">
            <div class="desc-section-title">${t.aboutTitle}</div>
            <div class="desc-text">${p.about[lang]}</div>
        </div>

        <div class="desc-section">
            <div class="desc-section-title">${t.benefitsTitle}</div>
            <div class="benefits-grid">
                ${p.benefits[lang].map(b=>`<div class="benefit-item"><div class="benefit-dot"></div><div class="benefit-text">${b}</div></div>`).join('')}
            </div>
        </div>

        <div class="desc-section">
            <div class="desc-section-title">${t.compTitle}</div>
            <div class="composition-list">
                ${p.composition[lang].map(c=>`<span class="comp-tag">${c}</span>`).join('')}
            </div>
        </div>

        <div class="desc-section">
            <div class="desc-section-title">${t.usageTitle}</div>
            <div class="usage-box">${p.usage[lang]}</div>
        </div>
    `;

    document.getElementById('modal-overlay').classList.add('active');
    document.getElementById('product-sheet').classList.add('active');
    tg?.HapticFeedback?.impactOccurred('light');
}

function closeModal(){
    document.getElementById('modal-overlay').classList.remove('active');
    document.getElementById('product-sheet').classList.remove('active');
    setTimeout(()=>{ currentProduct=null; },300);
}
document.getElementById('close-sheet').onclick=closeModal;
document.getElementById('modal-overlay').onclick=closeModal;

/* ── Viewer ── */
function openViewer(src){
    const v=document.getElementById('viewer');
    const img=document.getElementById('viewer-img');
    img.src=src; img.classList.remove('zoomed');
    v.classList.add('active');
}
function closeViewer(){document.getElementById('viewer').classList.remove('active');}
document.getElementById('viewer-close').onclick=closeViewer;
document.getElementById('viewer').onclick=e=>{if(e.target===e.currentTarget)closeViewer();};
document.getElementById('viewer-img').onclick=function(e){e.stopPropagation();this.classList.toggle('zoomed');};

/* ── Cart drawer ── */
function openCartDrawer(){
    document.getElementById('cart-sheet').classList.add('active');
    document.getElementById('cart-overlay').classList.add('active');
}
function closeCartDrawer(){
    document.getElementById('cart-sheet').classList.remove('active');
    document.getElementById('cart-overlay').classList.remove('active');
}
document.getElementById('cart-btn').onclick=openCartDrawer;
document.getElementById('close-cart').onclick=closeCartDrawer;
document.getElementById('cart-overlay').onclick=closeCartDrawer;

/* ── Checkout ── */
function processCheckout(){
    if(!cart.length){ tg?.HapticFeedback?.notificationOccurred('error'); return; }
    const orderData={
        action:'checkout',
        lang,
        total_price:cart.reduce((s,i)=>s+i.price*i.qty,0),
        items:cart.map(i=>({id:i.id,name:i.name.uz,quantity:i.qty,price:i.price}))
    };
    if(tg){
        try{ tg.sendData(JSON.stringify(orderData)); tg.close(); }
        catch(err){ console.error(err); alert('Xatolik yuz berdi. Iltimos qayta urinib ko\'ring.'); }
    } else {
        console.log('Test order:',orderData);
        alert('Test rejim: buyurtma konsolga chiqarildi.');
    }
}
document.getElementById('checkout-btn').onclick=processCheckout;
tg?.MainButton?.onClick(processCheckout);

/* ── Init ── */
applyI18n();
renderProducts(products);
updateCart();
