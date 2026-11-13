#!/usr/bin/env python3
"""Собирает сайт Velvet Laser из content/site.json в папку _site/.

Запуск: python3 build.py
Без внешних библиотек — нужен только Python 3.8+.
"""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "_site"
D = json.loads((ROOT / "content" / "site.json").read_text(encoding="utf-8"))
S, L, P, I, O = D["studio"], D["legal"], D["promo"], D["integrations"], D["offers"]


def rub(n):
    return f"{n:,}".replace(",", " ") + " ₽"


def img(name, alt, big=False, eager=False):
    src = f"/assets/img/{name}.webp"
    small = f"/assets/img/{name}-s.webp"
    load = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
    sizes = "(min-width:760px) 50vw, 100vw" if big else "(min-width:760px) 25vw, 50vw"
    return (f'<img src="{src}" srcset="{small} 560w, {src} 1100w" sizes="{sizes}" '
            f'alt="{alt}" {load} decoding="async">')


def head(title, desc, path):
    metrika = ""
    if I.get("yandex_metrika_id"):
        mid = I["yandex_metrika_id"]
        metrika = f"""<script>(function(m,e,t,r,i,k,a){{m[i]=m[i]||function(){{(m[i].a=m[i].a||[]).push(arguments)}};m[i].l=1*new Date();k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)}})(window,document,"script","https://mc.yandex.ru/metrika/tag.js","ym");ym({mid},"init",{{clickmap:true,trackLinks:true,accurateTrackBounce:true,webvisor:true}});</script><noscript><div><img src="https://mc.yandex.ru/watch/{mid}" style="position:absolute;left:-9999px" alt=""></div></noscript>"""
    vk = ""
    if I.get("vk_pixel_id"):
        vid = I["vk_pixel_id"]
        vk = f"""<script>var _tmr=window._tmr||(window._tmr=[]);_tmr.push({{id:"{vid}",type:"pageView",start:(new Date()).getTime()}});(function(d,w,id){{if(d.getElementById(id))return;var ts=d.createElement("script");ts.async=true;ts.id=id;ts.src="https://top-fwz1.mail.ru/js/code.js";var s=d.getElementsByTagName("script")[0];s.parentNode.insertBefore(ts,s)}})(document,window,"tmr-code");</script>"""
    cfg = json.dumps({
        "endpoint": I.get("form_endpoint", ""), "metrika": int(I["yandex_metrika_id"]) if I.get("yandex_metrika_id") else None,
        "phone": S["phone"], "phoneLink": S["phone_link"], "vkWrite": S["vk_write"],
        "callback": S["callback_minutes"],
    }, ensure_ascii=False)
    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta name="theme-color" content="#942539">
<link rel="icon" href="/favicon.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preload" href="/assets/fonts/lora-cyrillic-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/golos-text-cyrillic-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/css/style.css">
<script>window.VL={cfg};</script>
{metrika}{vk}
</head>
<body>
<header class="top"><div class="wrap">
  <a class="brand" href="/"><img src="/assets/img/logo.png" alt="" width="38" height="38"><span>Velvet Laser</span></a>
  <a class="top-phone" href="tel:{S['phone_link']}">{S['phone']}</a>
</div></header>
"""


def footer(cta_label=None):
    sticky = (f'<div class="sticky-cta"><a class="btn" href="#zapis">{cta_label}</a></div>'
              if cta_label else "")
    return f"""<footer><div class="wrap">
  <p><b>Velvet Laser</b> — {S['city']}, {S['address']}. {S['hours'].capitalize()}.</p>
  <p>{L['operator']}, ИНН {L['inn']}, ОГРНИП {L['ogrnip']}. Студия оказывает {L['services_kind']}.</p>
  <div class="links">
    <a href="/akciya/">Правила акции</a>
    <a href="/politika/">Политика обработки персональных данных</a>
    <a href="/soglasie/">Согласие на обработку персональных данных</a>
    <a href="{S['vk']}" target="_blank" rel="noopener">Мы ВКонтакте</a>
  </div>
  <p>{L['warning']}</p>
</div></footer>
{sticky}
<div class="cookie" role="dialog" aria-label="Уведомление о cookie">
  <span>Сайт использует cookie и Яндекс Метрику, чтобы понимать, как им пользуются. <a href="/politika/">Подробнее</a></span>
  <button type="button">Понятно</button>
</div>
<script src="/assets/js/main.js" defer></script>
</body></html>
"""


def ticket(kicker, name, price, old, left, right, extra=""):
    return f"""<div class="ticket-wrap"><div class="ticket" aria-label="Приглашение на первый визит">
  <p class="t-kicker">{kicker}</p>
  <p class="t-name">{name}</p>
  <p class="t-price">{price}</p>
  <p class="t-old">{old}</p>{extra}
  <div class="t-foot"><span>{left}</span><span>{right}</span></div>
</div></div>"""


def facts():
    return f"""<ul class="facts">
  <li>Центр, {S['address']}</li><li>Ежедневно 9:00–21:00</li><li>Чай после процедуры</li>
</ul>"""


def visit_block(photo, alt, steps):
    li = "".join(f"<li><div><b>{t}</b><span>{d}</span></div></li>" for t, d in steps)
    return f"""<section><div class="wrap visit">
  <div class="arch">{img(photo, alt, big=True)}</div>
  <div><h2>Как пройдёт ваш визит</h2>
  <ol class="steps">{li}</ol>
  <p class="promise">О курсах мастер расскажет, только если вы спросите. Решение всегда за вами.</p></div>
</div></section>"""


def studio_block(photos):
    figs = "".join(f'<figure class="{c}">{img(n, a)}</figure>' for n, a, c in photos)
    return f"""<section class="blush"><div class="wrap">
  <div class="sec-head"><h2>Здесь спокойно</h2>
  <p>Небольшая студия в центре: тихие кабинеты, мягкий свет, цветы на стойке администратора. После процедуры можно посидеть с чаем или кофе и никуда не спешить.</p></div>
  <div class="mosaic">{figs}</div>
</div></section>"""


def trust_block():
    return f"""<section><div class="wrap trust">
  <div class="photo">{img('team', 'Мастера студии Velvet Laser', big=True)}</div>
  <div><h2>Почему к нам возвращаются</h2>
  <ul class="points">
    <li><b>Мастера, которые слушают</b><span>Спрашиваем, как вы себя чувствуете, и подстраиваем процедуру под вас. Мастера регулярно учатся и работают по рекомендациям производителей оборудования.</span></li>
    <li><b>Честная цена</b><span>Цена на сайте — это цена в студии. Никаких доплат, о которых вы узнаёте на месте.</span></li>
    <li><b>Без давления</b><span>Не продаём то, что вам не нужно. Решение о курсе принимаете вы, а не мастер.</span></li>
    <li><b>Студия с 2023 года</b><span>Работаем в центре Сыктывкара, во ВКонтакте нас читают больше 2 500 человек.</span></li>
  </ul></div>
</div></section>"""


REVIEWS = {
    'face': [
        ('Светлана Г.', 'март 2026', 'Была на буккальном массаже лица у Анечки. Прекрасный специалист, нежные ручки. Получила удовольствие, рекомендации по уходу и записалась снова.'),
        ('Елена Ф.', 'ноябрь 2024', 'Массаж лица — волшебная процедура. Мастер Наталья всё подробно и очень увлекательно рассказала. А какие у неё горячие руки! Массаж очень расслабляет. Ощущение, что ухаживают за Клеопатрой, не меньше!'),
        ('Яна Л.', 'декабрь 2024', 'Персонал внимательный, всё подробно объяснили, предложили чай, кофе, воду, а в завершение процедуры вручили приятные подарки. Благодарю мастера Александру за компетентную беседу и чудесную процедуру «Массаж лица mini».'),
        ('Наталия К.', 'май 2026', 'Была здесь у массажистов Нины и Анастасии. Всё очень понравилось, массаж чудесный! Также девочки-администраторы очень внимательны и доброжелательны.'),
    ],
    'lpg': [
        ('Ольга', 'ноябрь 2023', 'Впервые сходила на LPG-массаж к мастеру Алине, очень понравился массаж, мастер постоянно интересовалась моим состоянием. После процедуры предложили кофе или чай на выбор. В салоне чисто, уютно.'),
        ('Катерина М.', 'март 2025', 'Администратор встретила и напоила чаем, так как я пришла чуть раньше. Я переоделась в специальный костюм, и мы начали массаж. Интенсивность можно менять, мастер всё время интересовалась, комфортно ли мне. Уже записалась на следующий сеанс.'),
        ('Лолита Г.', 'июнь 2026', 'Все приветливые, мастер Анна внимательная и опытная в своём деле. Плюс предлагают кофе, воду, чай до и после процедуры — в салоне, и с собой можно взять. Приятно!'),
        ('Галина М.', 'май 2026', 'Мне очень-очень нравится посещать эту студию. Всегда дружелюбная атмосфера, приятная обстановка, вежливые сотрудники. Много различных процедур для тела.'),
    ],
}


def reviews_block(first):
    items = REVIEWS[first] + REVIEWS['lpg' if first == 'face' else 'face'][:2]
    cards = "".join(
        f'<figure class="review"><div class="stars" aria-label="5 из 5">★★★★★</div>'
        f'<blockquote>{t}</blockquote><figcaption><b>{n}</b><span>{d} · Яндекс Карты</span></figcaption></figure>'
        for n, d, t in items)
    return f"""<section class="reviews-sec"><div class="wrap">
  <div class="reviews-head">
    <div><h2>Что пишут гости</h2>
    <p class="lead">Отзывы с Яндекс Карт. Некоторые сокращены, смысл не меняли.</p></div>
    <a class="rating" href="{S['yandex_reviews_url']}" target="_blank" rel="noopener" data-goal="maps">
      <b>{S['yandex_rating']}</b><span class="stars">★★★★★</span><span>{S['yandex_reviews_count']}<br>на Яндекс Картах</span></a>
  </div>
  <div class="reviews">{cards}</div>
  <p class="reviews-more"><a href="{S['yandex_reviews_url']}" target="_blank" rel="noopener" data-goal="maps">Все отзывы на Яндекс Картах →</a></p>
</div></section>"""


def contacts_block():
    return f"""<section class="blush"><div class="wrap contacts">
  <div><h2>Как нас найти</h2>
  <dl>
    <div><dt>Адрес</dt><dd>{S['city']}, {S['address']}</dd></div>
    <div><dt>Часы работы</dt><dd>{S['hours'].capitalize()}</dd></div>
    <div><dt>Телефон</dt><dd><a href="tel:{S['phone_link']}">{S['phone']}</a></dd></div>
    <div><dt>ВКонтакте</dt><dd><a href="{S['vk']}" target="_blank" rel="noopener">vk.com/velvetlaser11</a></dd></div>
    <div><dt>Яндекс Карты</dt><dd><a href="{S['yandex_maps_url']}" target="_blank" rel="noopener" data-goal="maps">Маршрут и отзывы</a></dd></div>
  </dl></div>
  <div class="map"><iframe src="{S['map_widget']}" title="Velvet Laser на карте" loading="lazy" allowfullscreen></iframe></div>
</div></section>"""


def book_block(title, sub, offers, extra_rules, options, cta):
    off = "".join(f'<div class="offer"><b>{t}</b><div class="p">{p}{f" <s>{o}</s>" if o else ""}</div><span>{d}</span></div>'
                  for t, p, o, d in offers)
    rules = "".join(f"<li>{r}</li>" for r in extra_rules)
    opts = "".join(
        f'<label><input type="radio" name="offer" value="{v}"{" checked" if i == 0 else ""}><span>{t}</span></label>'
        for i, (v, t) in enumerate(options))
    return f"""<section id="zapis" class="book"><div class="wrap book-grid">
  <div><div class="sec-head"><h2>{title}</h2><p>{sub}</p></div>
  <div class="offers">{off}</div>
  <ul class="rules">
    <li>Цены — для первого посещения студии, до {P['until']} включительно. Одна акционная процедура на гостя.</li>
    {rules}
    <li>Оформите абонемент в течение {P['trial_free_days']} дней после визита — стоимость пробного вычтем из абонемента.</li>
    <li>Места ограничены расписанием мастеров. <a href="/akciya/">Полные правила акции</a></li>
  </ul></div>
  <form class="form-card lead-form" novalidate>
    <h3>Оставьте номер</h3>
    <p class="sub">Администратор перезвонит в течение {S['callback_minutes']} минут с 9:00 до 21:00 и подберёт удобное время. Запись ни к чему не обязывает.</p>
    <div class="field"><span>Что выбираете</span><div class="choice">{opts}</div></div>
    <div class="field"><label for="f-phone">Телефон</label><input id="f-phone" name="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="+7 (___) ___-__-__" required></div>
    <div class="hp" aria-hidden="true"><label>Сайт<input name="website" tabindex="-1" autocomplete="off"></label></div>
    <label class="agree"><input type="checkbox" name="agree" value="1" aria-label="Согласие на обработку персональных данных"><span>Даю <a href="/soglasie/" target="_blank">согласие на обработку персональных данных</a> и подтверждаю, что ознакомлен(а) с <a href="/politika/" target="_blank">политикой</a>.</span></label>
    <button class="btn btn-block" type="submit" data-label="{cta}">{cta}</button>
    <div class="form-msg" role="status" aria-live="polite"></div>
    <div class="form-alt">
      <a class="btn btn-line" href="tel:{S['phone_link']}">Позвонить</a>
      <a class="btn btn-line" href="{S['vk_write']}" target="_blank" rel="noopener">Написать в ВК</a>
    </div>
  </form>
</div></section>"""


def faq_contra(contra_html, items):
    body = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in items)
    return f"""<section><div class="wrap two">
  <div><h2>Кому процедура не подойдёт</h2>
  <p class="muted">Если сомневаетесь — напишите нам до записи, подскажем.</p>
  <div class="contra">{contra_html}<span class="w">{L['warning']}</span></div></div>
  <div><h2>Частые вопросы</h2><div class="faq">{body}</div></div>
</div></section>"""


def cross_block(title, text, href, photo, alt):
    return f"""<section><div class="wrap"><div class="cross">
  <div><h3>{title}</h3><p>{text}</p><a class="btn btn-line" href="{href}">Посмотреть</a></div>
  <div class="arch">{img(photo, alt)}</div>
</div></div></section>"""


# ---------- Массаж лица ----------
def page_face():
    o = O["face"]
    h = head("Массаж лица за 1 290 ₽ в Сыктывкаре — Velvet Laser",
             f"Классический, скульптурный или буккальный массаж лица за 1 290 ₽ для первого посещения, до {P['until']}. Спокойная студия в центре Сыктывкара, {S['address']}.",
             "/massazh-lica/")
    body = f"""
<main>
<section class="hero"><div class="wrap">
  <div class="hero-media">
    <div class="arch pos-low">{img('f-hero', 'Гостья отдыхает с закрытыми глазами во время ухода за лицом', big=True, eager=True)}</div>
    {ticket('Приглашение на первый визит', 'Массаж лица на выбор', '1 290<small>₽</small>', f"обычно <s>{o['price_regular']}</s>", f"до {P['until']}", 'Вдвоём — 2 290 ₽')}
  </div>
  <div class="hero-copy">
    <h1>Вы заботитесь обо&nbsp;всех. Этот час&nbsp;— о&nbsp;вас</h1>
    <p class="lead">Массаж лица в тихом кабинете в центре Сыктывкара. Тёплые руки мастера, мягкий свет и чай после — можно наконец выдохнуть.</p>
  </div>
  <div class="hero-act">
    <div class="hero-cta">
      <a class="btn" href="#zapis">Записаться за {rub(o['price'])}</a>
      <p class="hero-note">Перезвоним за {S['callback_minutes']} минут и подберём время. Запись ни к чему не обязывает.</p>
    </div>
    {facts()}
    <p class="warn-line">{L['warning']}</p>
  </div>
</div></section>

<section class="feel"><div class="wrap">
  <h2>Знакомо?</h2>
  <div>
    <ul>
      <li>Весь день работа, дети, дом, а на себя остаётся пять минут перед сном.</li>
      <li>Хочется, чтобы кто-то просто позаботился о вас — без советов и уговоров.</li>
      <li>Давно собирались на массаж, но всё время что-то важнее.</li>
    </ul>
    <p>Для этого и есть наш час. Вы ложитесь, закрываете глаза, а дальше о вас заботимся мы.</p>
  </div>
</div></section>

<section><div class="wrap">
  <div class="sec-head"><h2>Три массажа — одна цена</h2>
  <p>Выберите тот, что ближе, или решите вместе с мастером на месте. Любой из трёх — {rub(o['price'])} для первого визита.</p></div>
  <div class="kinds">
    <div class="kind"><div class="arch">{img('f-calm', 'Классический массаж лица')}</div>
      <h3>Классический</h3><p>Мягкий и размеренный. Для тех, кто пришёл отдохнуть и выключить голову.</p><span class="tag">обычно 2 290 ₽</span></div>
    <div class="kind"><div class="arch">{img('f-sculpt', 'Скульптурный массаж лица')}</div>
      <h3>Скульптурный</h3><p>Плотнее и глубже. Мастер не спеша прорабатывает лицо и шею, ощущения интенсивнее классического.</p><span class="tag">обычно 2 790 ₽</span></div>
    <div class="kind"><div class="arch">{img('f-buccal', 'Буккальный массаж лица')}</div>
      <h3>Буккальный</h3><p>Мастер работает в том числе с внутренней стороны щёк — в перчатках, бережно и с вашего согласия.</p><span class="tag">обычно 2 790 ₽</span></div>
  </div>
  <p class="kinds-note">Не знаете, что выбрать? Мастер подскажет — цена от этого не изменится.</p>
</div></section>

{visit_block('f-care', 'Мастер наносит средство кистью, гостья отдыхает с закрытыми глазами', [
    ('Звонок', f"Администратор перезванивает в течение {S['callback_minutes']} минут и подбирает удобное время."),
    ('Знакомство', 'Мастер спрашивает о самочувствии и о том, чего вам хочется от процедуры.'),
    ('Массаж', 'Вы лежите с закрытыми глазами. Интенсивность подбираем под вас и спрашиваем, комфортно ли.'),
    ('Чай', 'После — чай или кофе в зоне отдыха. Торопиться не нужно.'),
])}

{studio_block([('tea', 'Кофе и чай в зоне отдыха', 'arch tall'), ('art', 'Картина в интерьере студии', ''), ('decor', 'Детали интерьера студии', ''), ('outside', 'Вход в студию Velvet Laser', 'wide')])}

{trust_block()}

{reviews_block('face')}

{book_block('Ваше приглашение', 'Выберите, как хотите прийти, и оставьте номер — остальное сделаем мы.', [
    ('Массаж лица на выбор', rub(o['price']), o['price_regular'], 'Классический, скульптурный или буккальный.'),
    ('Вдвоём с подругой', rub(o['pair_price']), rub(o['price'] * 2), 'Два массажа лица, если вы обе впервые в студии.'),
], ['«Вдвоём с подругой» — для двух гостей, которые приходят в студию впервые.'],
    [('Массаж лица — 1290', f"Массаж лица — {rub(o['price'])}"), ('Вдвоём с подругой — 2290', f"Вдвоём с подругой — {rub(o['pair_price'])}")],
    f"Записаться за {rub(o['price'])}")}

{faq_contra('Массаж лица не проводится при беременности и лактации, онкологических заболеваниях, острых инфекционных заболеваниях, кожных заболеваниях в зоне массажа, эпилепсии, кардиостимуляторе.', [
    ("Это больно?", "Нет. Ощущения как от плотного массажа. Мастер спрашивает, комфортно ли вам, и меняет интенсивность."),
    ("Какой массаж выбрать?", f"Любой из трёх стоит {rub(o['price'])}. Если не знаете, что ближе, — мастер подскажет на месте."),
    ("Будут ли уговаривать на курс?", f"Нет. О курсе расскажем, только если спросите. Решите оформить абонемент в течение {P['trial_free_days']} дней — стоимость первого визита вычтем."),
    ("Я уже была у вас. Акция для меня?", "Цена действует для первого посещения студии. Для постоянных гостей есть абонементы и программа «для подруг»: 1 000 ₽ на баланс за каждую приглашённую."),
    ("Как прийти вдвоём с подругой?", f"Выберите в форме «Вдвоём с подругой» — два массажа лица за {rub(o['pair_price'])}, если вы обе впервые в студии."),
    ("Можно подарить?", "Да, у нас есть подарочный сертификат на любой номинал."),
    ("Как перенести запись?", "Напишите или позвоните нам не позже чем за 24 часа."),
])}

{contacts_block()}

{cross_block(f"Для тела — LPG с костюмом за {rub(O['lpg']['price'] + O['lpg']['suit_price'])}", f"40 минут аппаратного массажа, после которых телу легче. Тоже для первого визита, до {P['until']}.", f"/{O['lpg']['slug']}/", 'l-hero', 'LPG-массаж в студии')}
</main>
"""
    return h + body + footer(f"Записаться за {rub(o['price'])}")


# ---------- LPG ----------
def page_lpg():
    o = O["lpg"]
    h = head("LPG с костюмом за 1 190 ₽ в Сыктывкаре — Velvet Laser",
             f"LPG-массаж 40 минут и новый личный костюм за 1 190 ₽ или вакуумный массаж за 890 ₽ для первого посещения, до {P['until']}. Студия в центре Сыктывкара, {S['address']}.",
             "/lpg/")
    booking = book_block('Ваше приглашение', 'Выберите процедуру и оставьте номер — остальное сделаем мы.', [
    (f"LPG-массаж, {o['duration']}", rub(o['price'] + o['suit_price']), "", f"Включены процедура {rub(o['price'])} и новый костюм {rub(o['suit_price'])}. Костюм остаётся у вас."),
    ('Вакуумный массаж всего тела', rub(o['vacuum_price']), o['vacuum_regular'], 'Без костюма и дополнительных покупок.'),
], ['Акционная цена — на LPG-массаж или на вакуумный массаж всего тела, на выбор.'],
    [('LPG — 890 + костюм 300', f"LPG с новым костюмом — {rub(o['price'] + o['suit_price'])}"), ('Вакуум всего тела — 890', f"Вакуум — {rub(o['vacuum_price'])}")],
    f"Выбрать процедуру и время")
    form_start = booking.index('  <form')
    form_end = booking.index('</form>', form_start) + len('</form>')
    quick_form = booking[form_start:form_end]
    quick_form = quick_form.replace('<h3>Оставьте номер</h3>', '<h3>Подберём время для вас</h3>')
    quick_form = quick_form.replace('Администратор перезвонит в течение ', 'Перезвоним в течение ')
    quick_form = quick_form.replace(' и подберёт удобное время. Запись ни к чему не обязывает.', '.')
    quick_form = quick_form.replace('Выбрать процедуру и время', 'Подобрать время')
    booking_details = (booking[:form_start] + booking[form_end:]).replace('id="zapis"', 'id="ceny"').replace('class="wrap book-grid"', 'class="wrap"')
    booking_details = booking_details.replace('</div></section>', '<p style="margin-top:24px"><a class="btn btn-light" href="#zapis">Подобрать время</a></p></div></section>')
    hero_style = """<style>
.lpg-page{--max:1200px}
.lpg-page section{padding:68px 0}
.lpg-page .lpg-first{padding:24px 0 0}
.lpg-first .wrap{display:grid;gap:22px;grid-template-areas:"copy" "media" "act";padding-bottom:32px}
.lpg-first .eyebrow,.lpg-page .eyebrow{font:500 11px/1.5 var(--sans);letter-spacing:.12em;text-transform:uppercase;color:var(--wine);margin:0 0 14px}
.lpg-first h1{font-size:clamp(38px,8vw,66px);line-height:1.06;max-width:12em;letter-spacing:-.035em;margin-bottom:16px}
.lpg-first h1 em{color:var(--wine);font-weight:400}
.lpg-first .lead{font-size:16px;line-height:1.6;max-width:32em}
.lpg-first .hero-media{padding:0;position:relative}
.lpg-first .hero-media .arch{aspect-ratio:16/10;border-radius:100px 100px 20px 20px}
.lpg-first .hero-media img{object-position:50% 52%}
.lpg-first .photo-label{position:absolute;bottom:14px;left:14px;right:14px;background:rgba(251,247,244,.96);padding:10px 14px;border-radius:12px;font-size:12px;display:flex;justify-content:space-between;gap:10px}
.lpg-first .photo-label b{font-weight:500}
.lpg-first .hero-act{display:block}
.lpg-first .hero-price{display:flex;align-items:center;gap:16px;margin:0 0 14px}
.lpg-first .hero-price strong{font:400 44px/1 var(--serif);letter-spacing:-.04em;color:var(--wine);white-space:nowrap}
.lpg-first .hero-price span{font-size:13px;line-height:1.5;max-width:180px}
.lpg-first .hero-cta{max-width:none;margin:0}
.lpg-first .offer-note{font-size:12px;color:var(--ink-2);margin:12px 0 0}
.lpg-first .warn-line{font-size:11px;margin:12px 0 0}
.lpg-page .evidence{padding:22px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.evidence .wrap{display:grid;grid-template-columns:1fr 1fr;gap:18px}
.evidence a{text-decoration:none;color:var(--ink)}
.evidence strong{display:block;font:400 27px/1.2 var(--serif);color:var(--wine)}
.evidence span{font-size:12px;color:var(--ink-2);display:block;margin-top:5px}
.evidence .evidence-last{grid-column:1/-1;border-top:1px solid var(--line);padding-top:15px}
.lpg-page .first-visit{background:var(--plum);color:var(--paper)}
.first-visit h2{color:var(--paper);max-width:14em}
.first-visit .eyebrow{color:#ecc0c7}
.first-visit .reason-grid{display:grid;gap:26px;margin-top:32px}
.reason{border-top:1px solid #76565e;padding-top:18px}
.reason .num{color:#e2a7b2;font-size:12px;letter-spacing:.12em}
.reason h3{color:var(--paper);font-size:25px;margin:10px 0}
.reason p{font-size:15px;color:#ead8db;margin:0;max-width:30em}
.lpg-page .guest-proof{padding:40px 0;background:var(--blush)}
.guest-proof .wrap{max-width:900px}
.guest-proof blockquote{font:400 clamp(22px,4.5vw,32px)/1.45 var(--serif);margin:0 0 18px}
.guest-proof p{font-size:13px;color:var(--ink-2);margin:0}
.guest-proof a{display:inline-block;font-size:13px;margin-top:16px}
.lpg-page .kind .arch{border-radius:24px;aspect-ratio:4/3}
.lpg-page .kinds{gap:26px}
.lpg-page .kind{padding-bottom:24px;border-bottom:1px solid var(--line)}
.lpg-page .kind h3{font-size:28px}
.lpg-page .kind .tag{font-size:18px}
.lpg-page .kind .btn{margin-top:18px;min-height:48px;font-size:14px}
.lpg-page .booking-panel{background:var(--wine);color:var(--paper);scroll-margin-top:70px}
.booking-panel .wrap{display:grid;gap:28px;align-items:start}
.booking-panel h2{color:var(--paper);font-size:clamp(34px,5vw,48px);max-width:11em}
.booking-panel .eyebrow{color:#ecc0c7}
.booking-panel .booking-lead{font-size:17px;max-width:30em;color:#f4dee2}
.booking-panel .booking-steps{list-style:none;margin:24px 0 0;padding:0;display:grid;gap:14px}
.booking-steps li{font-size:14px;padding-top:14px;border-top:1px solid #b96272;color:#f4dee2}
.booking-steps b{font-weight:500;color:white;display:block;font-size:16px}
.booking-panel .form-card{padding:26px 22px;box-shadow:0 18px 50px #4b0e2533}
.booking-panel .form-card h3{font-size:26px}
.booking-panel .choice span{font-size:13px;padding:10px 12px}
.lpg-page .book{background:var(--blush);color:var(--ink)}
.lpg-page .book h2,.lpg-page .book .offer b,.lpg-page .book .offer .p{color:var(--ink)}
.lpg-page .book .sec-head p,.lpg-page .book .offer span,.lpg-page .book .rules{color:var(--ink-2)}
.lpg-page .book .offer{background:var(--paper);border-color:var(--line)}
.lpg-page .book .rules a{color:var(--wine)}
.lpg-page .book .offer .p s{color:var(--ink-2)}
.lpg-page .book .btn-light{background:var(--wine);color:#fff}
.lpg-page .trust .photo{aspect-ratio:5/4;border-radius:22px 22px 100px 22px}
.lpg-page .trust .points b{font-size:23px}
.lpg-page .trust .points span{font-size:15px}
.lpg-page .mosaic figure.arch{border-radius:24px}
@media(min-width:760px){
.lpg-page section{padding:80px 0}
.lpg-page .lpg-first{padding-top:38px}
.lpg-first .wrap{grid-template-columns:1fr 1fr;grid-template-areas:"copy media" "act media";column-gap:64px;row-gap:24px;align-items:center;padding-bottom:48px}
.lpg-first .hero-copy{align-self:end}
.lpg-first .hero-act{align-self:start}
.lpg-first .hero-media{align-self:stretch;min-height:580px}
.lpg-first .hero-media .arch{aspect-ratio:auto;height:100%;border-radius:240px 240px 24px 24px}
.lpg-first .photo-label{bottom:24px;left:24px;right:24px;padding:14px 18px;font-size:13px}
.lpg-first .hero-price strong{font-size:58px}
.lpg-first .hero-cta{max-width:390px}
.evidence .wrap{grid-template-columns:1fr 1fr 1fr;gap:36px}
.evidence .evidence-last{grid-column:auto;border-top:0;padding-top:0}
.lpg-page .evidence{padding:30px 0}
.first-visit .reason-grid{grid-template-columns:repeat(3,1fr);gap:32px;margin-top:44px}
.booking-panel .wrap{grid-template-columns:1fr 1fr;gap:64px}
.lpg-page .kinds{grid-template-columns:1fr 1fr}
.lpg-page .book .offers{grid-template-columns:1fr 1fr}
}
@media(max-width:380px){.lpg-first h1{font-size:35px}.lpg-first .hero-price strong{font-size:39px}.lpg-first .hero-price{gap:12px}.lpg-first .photo-label{font-size:11px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
</style>"""
    h = h.replace('</head>', hero_style + '</head>')
    body = f"""
<main class="lpg-page">
<section class="hero lpg-first" data-landing-version="lpg-visual-20261113"><div class="wrap">
  <div class="hero-copy">
    <p class="eyebrow">Velvet Laser / Сыктывкар · {S['address']}</p>
    <h1>LPG-массаж.<br><em>40 минут для себя.</em></h1>
    <p class="lead">Плотный аппаратный массаж тела в спокойной студии. Мастер подберёт интенсивность и будет спрашивать, комфортно ли вам.</p>
  </div>
  <div class="hero-media">
    <div class="arch">{img('l-hero', 'Мастер проводит LPG-массаж в студии Velvet Laser', big=True, eager=True)}</div>
    <div class="photo-label"><b>Так проходит LPG у нас</b><span>Настоящее фото студии</span></div>
  </div>
  <div class="hero-act">
    <p class="hero-price"><strong>{rub(o['price'] + o['suit_price'])}</strong><span>первый LPG, 40 минут<br>новый костюм включён</span></p>
    <div class="hero-cta"><a class="btn" href="#zapis">Записаться на первый визит</a></div>
    <p class="offer-note">Процедура {rub(o['price'])} + личный костюм {rub(o['suit_price'])}.<br>Для первого посещения до {P['until']}.</p>
    <p class="warn-line">{L['warning']}</p>
  </div>
</div></section>
<section class="evidence" aria-label="О студии"><div class="wrap">
  <a href="{S['yandex_reviews_url']}" target="_blank" rel="noopener"><strong>{S['yandex_rating']} / 5</strong><span>{S['yandex_reviews_count']} на Яндекс Картах ↗</span></a>
  <div><strong>С 2023 года</strong><span>Принимаем гостей в центре Сыктывкара</span></div>
  <div class="evidence-last"><strong>Один визит</strong><span>Можно начать без покупки абонемента</span></div>
</div></section>
<section class="guest-proof"><div class="wrap">
  <p class="eyebrow">Гости — о первом посещении</p>
  <blockquote>«Интенсивность можно менять, мастер всё время интересовалась, комфортно ли мне. Уже записалась на следующий сеанс.»</blockquote>
  <p>Катерина М. · март 2025 · фрагмент отзыва на Яндекс Картах</p>
  <a href="{S['yandex_reviews_url']}" target="_blank" rel="noopener">Прочитать отзывы о студии ↗</a>
</div></section>
<section class="first-visit"><div class="wrap">
  <p class="eyebrow">Первое посещение — всё понятно заранее</p>
  <h2>Попробуйте один раз.<br>А дальше решите сами.</h2>
  <div class="reason-grid">
    <article class="reason"><span class="num">01 / ЦЕНА</span><h3>Костюм уже в стоимости</h3><p>Первый LPG-визит — {rub(o['price'] + o['suit_price'])}. Новый костюм остаётся у вас, его можно использовать на следующих процедурах.</p></article>
    <article class="reason"><span class="num">02 / ОЩУЩЕНИЯ</span><h3>Интенсивность под вас</h3><p>Скажите мастеру, если хочется мягче. Перед процедурой обсудим самочувствие и противопоказания.</p></article>
    <article class="reason"><span class="num">03 / ВЫБОР</span><h3>Без покупки курса</h3><p>Начните с одного посещения. О курсе расскажем, если спросите. Решение можно принять после знакомства со студией.</p></article>
  </div>
</div></section>

<section><div class="wrap">
  <div class="sec-head"><h2>Два варианта первого визита</h2>
  <p>LPG с новым личным костюмом — {rub(o['price'] + o['suit_price'])}. Вакуум без костюма — {rub(o['vacuum_price'])}. Выберите, что ближе.</p></div>
  <div class="kinds" style="grid-template-columns:repeat(auto-fit,minmax(260px,1fr))">
    <div class="kind"><div class="arch">{img('l-lpg', 'Руки мастера проводят LPG-массаж')}</div>
      <h3>LPG-массаж, {o['duration']}</h3><p>Аппарат с роликами работает по телу через специальный костюм. Ощущения как от плотного массажа.</p><span class="tag">{rub(o['price'] + o['suit_price'])} с новым костюмом</span><br><a class="btn btn-line" href="#zapis">Хочу попробовать LPG</a></div>
    <div class="kind"><div class="arch">{img('l-device', 'Аппарат для массажа тела в кабинете студии')}</div>
      <h3>Вакуумный массаж всего тела</h3><p>Аппаратный массаж без костюма. Подойдёт, если хотите попробовать, ничего не покупая заранее.</p><span class="tag">{rub(o['vacuum_price'])} · костюм не нужен</span><br><a class="btn btn-line" href="#zapis">Выбрать вакуумный массаж</a></div>
  </div>
  <p class="kinds-note">Костюм для LPG личный: он остаётся у вас и пригодится, если решите продолжить.</p>
</div></section>

<section class="booking-panel" id="zapis"><div class="wrap">
  <div><p class="eyebrow">Первый шаг — выбрать время</p><h2>Начнём с одного визита?</h2>
  <p class="booking-lead">Оставьте номер. Администратор перезвонит в течение {S['callback_minutes']} минут с 9:00 до 21:00 и предложит свободное время.</p>
  <ul class="booking-steps"><li><b>LPG — {rub(o['price'] + o['suit_price'])}</b>40 минут, новый личный костюм включён.</li><li><b>Вакуум — {rub(o['vacuum_price'])}</b>Массаж тела без костюма.</li><li><b>{S['address']}</b>Центр Сыктывкара · ежедневно 9:00–21:00.</li></ul></div>
  {quick_form}
</div></section>

{trust_block()}

{reviews_block('lpg')}

{booking_details}

{faq_contra('<b>LPG-массаж</b> не проводится при заболеваниях крови и склонности к тромбообразованию, туберкулёзе, опухолях, индивидуальной непереносимости массажа, нарушениях психики. Процедуру откладываем при лихорадке, острых заболеваниях и инфекциях, интоксикации, заболеваниях кожи, кровотечениях, во время беременности и менструации.<br><br><b>Вакуумный массаж</b> — противопоказания администратор уточнит при записи.', [
    ("Какие ощущения во время LPG?", "Ощущения похожи на плотный массаж. Чувствительность у всех разная. Если вам неприятно, скажите мастеру — интенсивность можно уменьшить."),
    ("Зачем костюм?", f"LPG-массаж проводится через специальный костюм. Он личный, стоит {rub(o['suit_price'])} и остаётся у вас. Не хотите покупать костюм — выберите вакуумный массаж за {rub(o['vacuum_price'])}."),
    ("LPG или вакуум?", "Обе процедуры — аппаратный массаж тела. Расскажите администратору, чего хотите, — подскажем."),
    ("Будут ли уговаривать на курс?", f"Нет. О курсе расскажем, только если спросите. Решите оформить абонемент в течение {P['trial_free_days']} дней — стоимость первого визита вычтем."),
    ("Я уже была у вас. Акция для меня?", "Цена действует для первого посещения студии. Для постоянных гостей есть абонементы и программа «для подруг»: 1 000 ₽ на баланс за каждую приглашённую."),
    ("Как перенести запись?", "Напишите или позвоните нам не позже чем за 24 часа."),
])}

{studio_block([('tea', 'Кофе и чай в зоне отдыха', 'arch tall'), ('room', 'Кабинет студии', ''), ('decor', 'Детали интерьера студии', ''), ('outside', 'Вход в студию Velvet Laser', 'wide')])}

{contacts_block()}

{cross_block(f"Для лица — массаж за {rub(O['face']['price'])}", f"Классический, скульптурный или буккальный — на выбор. Тоже для первого визита, до {P['until']}.", f"/{O['face']['slug']}/", 'f-brush', 'Уход за лицом в студии')}
</main>
"""
    return h + body + footer(f"Выбрать процедуру и время")


# ---------- Главная ----------
def page_index():
    h = head("Velvet Laser — студия в центре Сыктывкара",
             f"Массаж лица за 1 290 ₽ и LPG-массаж от 890 ₽ для первого посещения, до {P['until']}. {S['address']}.", "/")
    body = f"""
<main><section class="hero"><div class="wrap" style="grid-template-columns:1fr">
  <div><h1>Время для себя — в центре Сыктывкара</h1>
  <p class="lead">Выберите процедуру, чтобы узнать подробности и записаться.</p></div>
  <div class="hub">
    <a href="/{O['face']['slug']}/"><img src="/assets/img/f-hero-s.webp" alt="Массаж лица" loading="lazy"><span><b>Массаж лица — {rub(O['face']['price'])}</b><span class="muted">обычно {O['face']['price_regular']}</span></span></a>
    <a href="/{O['lpg']['slug']}/"><img src="/assets/img/l-hero-s.webp" alt="LPG-массаж" loading="lazy"><span><b>LPG с костюмом — {rub(O['lpg']['price'] + O['lpg']['suit_price'])}</b><span class="muted">обычно {O['lpg']['price_regular']}</span></span></a>
  </div>
  <p class="warn-line">{L['warning']}</p>
</div></section>
{contacts_block()}</main>
"""
    return h + body + footer()


# ---------- Документы ----------
def doc_page(path, title, html):
    return head(f"{title} — Velvet Laser", title, path) + f'<main><div class="wrap doc"><h1>{title}</h1>{html}</div></main>' + footer()


def page_akciya():
    f, l = O["face"], O["lpg"]
    return doc_page("/akciya/", "Правила акции «Первое посещение»", f"""
<p>Организатор акции — {L['operator']}, ИНН {L['inn']}, ОГРНИП {L['ogrnip']}. Место проведения — студия Velvet Laser: {S['city']}, {S['address']}.</p>
<h2>1. Срок</h2><p>Акция действует с даты публикации этой страницы по {P['until']} включительно.</p>
<h2>2. Кто может участвовать</h2><p>Гости старше 18 лет, которые приходят в студию Velvet Laser впервые. Одна акционная процедура на одного гостя.</p>
<h2>3. Акционные предложения</h2>
<ul>
<li>Массаж лица на выбор — классический, скульптурный или буккальный — {rub(f['price'])} вместо {f['price_regular']}.</li>
<li>«Вдвоём с подругой» — два массажа лица за {rub(f['pair_price'])} для двух гостей, которые приходят в студию впервые.</li>
<li>LPG-массаж, {l['duration']} — {rub(l['price'])} вместо {l['price_regular']}. Для процедуры нужен личный костюм, его стоимость — {rub(l['suit_price'])}, костюм остаётся у гостя.</li>
<li>Вакуумный массаж всего тела — {rub(l['vacuum_price'])} вместо {l['vacuum_regular']}.</li>
</ul>
<h2>4. Пробный визит бесплатно при покупке абонемента</h2><p>Если в течение {P['trial_free_days']} календарных дней после акционной процедуры гость оформляет абонемент на любую процедуру студии, стоимость оплаченной акционной процедуры вычитается из стоимости абонемента.</p>
<h2>5. Запись</h2><p>Запись предварительная — через форму на сайте, по телефону <a href="tel:{S['phone_link']}">{S['phone']}</a> или в сообщениях сообщества ВКонтакте. Количество акционных мест ограничено расписанием мастеров. Перенести или отменить запись можно не позже чем за 24 часа.</p>
<h2>6. Прочее</h2><p>Перед процедурой гость заполняет карту гостя и подписывает информированное согласие. Мастер вправе отказать в процедуре при наличии противопоказаний. Остальные условия — в публичной оферте студии, размещённой в сообществе <a href="{S['vk']}" target="_blank" rel="noopener">ВКонтакте</a> и в студии.</p>
<p><b>{L['warning']}</b></p>""")


def page_politika():
    return doc_page("/politika/", "Политика обработки персональных данных", f"""
<p>Политика описывает, как {L['operator']} (ИНН {L['inn']}, ОГРНИП {L['ogrnip']}), далее — Оператор, обрабатывает персональные данные посетителей этого сайта. Политика составлена в соответствии с Федеральным законом № 152-ФЗ «О персональных данных».</p>
<h2>1. Какие данные мы получаем</h2>
<ul><li>Имя и номер телефона, удобное время визита и выбранная процедура — когда вы оставляете заявку.</li>
<li>Технические данные: cookie, IP-адрес, сведения о браузере и устройстве, страницы и рекламные метки, по которым вы пришли, — через сервис Яндекс Метрика.</li></ul>
<h2>2. Зачем</h2>
<ul><li>Связаться с вами, ответить на вопросы и записать на процедуру.</li>
<li>Информировать о записи и изменениях в работе студии.</li>
<li>Понимать, как пользуются сайтом, и улучшать его и рекламу.</li></ul>
<h2>3. Основание</h2><p>Ваше согласие на обработку персональных данных, которое вы даёте, отправляя заявку.</p>
<h2>4. Как мы обрабатываем данные</h2>
<p>Обработка — с использованием средств автоматизации и без них: сбор, запись, систематизация, накопление, хранение, уточнение, использование, передача (предоставление), удаление. Для учёта гостей и записи используются CRM-система и сервис онлайн-записи; для статистики сайта — Яндекс Метрика (ООО «Яндекс»).</p>
<p>Чтобы администратор быстро получил заявку, её данные (имя, телефон, выбранная процедура и удобное время) передаются в мессенджер Telegram (Telegram Messenger Inc.) и в сервис Google (Google LLC), где хранится резервная копия заявок. Это трансграничная передача персональных данных, она осуществляется с вашего согласия и только в целях, указанных в этой политике.</p>
<p>Мы не продаём и не передаём ваши данные третьим лицам, кроме случаев, предусмотренных законом.</p>
<h2>5. Сколько храним</h2><p>До достижения целей обработки или до отзыва согласия, но не дольше 3 лет с момента последнего обращения, если иное не требует закон.</p>
<h2>6. Ваши права</h2><p>Вы можете узнать, какие данные мы храним, потребовать их уточнить или удалить и отозвать согласие. Для этого напишите на <a href="mailto:{L['email']}">{L['email']}</a> или направьте письмо по адресу: {L['mail_address']}. Ответим в течение 10 рабочих дней.</p>
<h2>7. Cookie</h2><p>Вы можете отключить cookie в настройках браузера. Сайт продолжит работать, но статистика будет неполной.</p>
<h2>8. Контакты Оператора</h2><p>{L['operator']}<br>Адрес: {L['mail_address']}<br>Электронная почта: <a href="mailto:{L['email']}">{L['email']}</a><br>Телефон студии: <a href="tel:{S['phone_link']}">{S['phone']}</a></p>""")


def page_soglasie():
    return doc_page("/soglasie/", "Согласие на обработку персональных данных", f"""
<p>Отправляя заявку на сайте, я свободно, своей волей и в своём интересе даю согласие {L['operator']} (ИНН {L['inn']}, ОГРНИП {L['ogrnip']}, адрес: {L['mail_address']}) на обработку моих персональных данных на следующих условиях.</p>
<ul>
<li><b>Данные:</b> имя, номер телефона, удобное время визита, выбранная процедура, а также технические данные (cookie, IP-адрес, сведения о браузере и устройстве, рекламные метки).</li>
<li><b>Цели:</b> обработка заявки, связь со мной, запись на процедуру, информирование о записи и работе студии, анализ работы сайта.</li>
<li><b>Действия:</b> сбор, запись, систематизация, накопление, хранение, уточнение, использование, передача (предоставление), обезличивание, блокирование, удаление — с использованием средств автоматизации и без них.</li>
<li><b>Трансграничная передача:</b> я согласен(на), что имя, телефон, выбранная процедура и удобное время передаются в мессенджер Telegram (Telegram Messenger Inc.) и сервис Google (Google LLC) для уведомления администратора и хранения копии заявки.</li>
<li><b>Срок:</b> согласие действует до достижения целей обработки, но не дольше 3 лет, либо до его отзыва.</li>
<li><b>Отзыв:</b> я могу отозвать согласие, написав на <a href="mailto:{L['email']}">{L['email']}</a> или направив письмо по адресу: {L['mail_address']}.</li>
</ul>
<p>Порядок обработки описан в <a href="/politika/">Политике обработки персональных данных</a>.</p>""")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "assets", OUT / "assets")
    for f in ["favicon.png", "apple-touch-icon.png", "robots.txt", "CNAME"]:
        if (ROOT / f).exists():
            shutil.copy(ROOT / f, OUT / f)
    pages = {
        "index.html": page_index(),
        f"{O['face']['slug']}/index.html": page_face(),
        f"{O['lpg']['slug']}/index.html": page_lpg(),
        "akciya/index.html": page_akciya(),
        "politika/index.html": page_politika(),
        "soglasie/index.html": page_soglasie(),
    }
    base = D.get("base_path", "").rstrip("/")
    for p, html in pages.items():
        if base:
            html = (html.replace('href="/', f'href="{base}/').replace('src="/', f'src="{base}/')
                        .replace('srcset="/', f'srcset="{base}/').replace(', /assets/', f', {base}/assets/'))
        t = OUT / p
        t.parent.mkdir(parents=True, exist_ok=True)
        t.write_text(html, encoding="utf-8")
    (OUT / ".nojekyll").write_text("")
    print("Собрано страниц:", len(pages))


if __name__ == "__main__":
    main()
