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
<link rel="preload" href="/assets/fonts/playfair-display-cyrillic-600-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/montserrat-cyrillic-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/css/style.css">
<script>window.VL={cfg};</script>
{metrika}{vk}
</head>
<body>
<header class="top"><div class="wrap">
  <a class="brand" href="/"><img src="/assets/img/logo.png" alt="" width="40" height="40"><span>Velvet Laser</span></a>
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


def visit_steps():
    return f"""<ol class="steps">
  <li><b>Заявка</b><span>Оставляете номер — администратор перезванивает в течение {S['callback_minutes']} минут и подбирает удобное время.</span></li>
  <li><b>Знакомство</b><span>Мастер коротко спрашивает о ваших ожиданиях и самочувствии, вы подписываете карту гостя.</span></li>
  <li><b>Процедура</b><span>Интенсивность подбираем под вас и спрашиваем, комфортно ли.</span></li>
  <li><b>Отдых</b><span>После — чай или кофе в зоне отдыха. Торопиться не нужно.</span></li>
  <li><b>Без давления</b><span>Если спросите, мастер расскажет, что можно делать дальше. Если нет — просто будем рады видеть вас снова.</span></li>
</ol>"""


def studio_block(photos):
    figs = "".join(f'<figure class="{c}">{img(n, a)}</figure>' for n, a, c in photos)
    return f"""<section class="alt"><div class="wrap">
  <div class="sec-head"><span class="eyebrow">Студия</span><h2>Здесь спокойно</h2>
  <p class="muted">Тихие кабинеты, зона отдыха и чай после процедуры. В холодное время года кофе или чай можно взять с собой.</p></div>
  <div class="gallery">{figs}</div>
</div></section>"""


def team_block():
    return f"""<section><div class="wrap split">
  <div class="split-photo">{img('team', 'Мастера студии Velvet Laser', big=True)}</div>
  <div><span class="eyebrow">Кто делает</span><h2>Мастера студии</h2>
  <p>Процедуры ведут мастера Velvet Laser. Они регулярно учатся новым техникам и работают по рекомендациям производителей оборудования.</p>
  <p class="muted">Мы рекомендуем только то, что действительно нужно. Никаких лишних процедур и продаж «в лоб».</p></div>
</div></section>"""


def contacts_block():
    return f"""<section class="alt"><div class="wrap two-col contacts">
  <div><span class="eyebrow">Как нас найти</span><h2>{S['address']}</h2>
  <dl>
    <div><dt>Адрес</dt><dd>{S['city']}, {S['address']} — {S['address_note']}</dd></div>
    <div><dt>Время работы</dt><dd>{S['hours'].capitalize()}</dd></div>
    <div><dt>Телефон</dt><dd><a href="tel:{S['phone_link']}">{S['phone']}</a></dd></div>
    <div><dt>ВКонтакте</dt><dd><a href="{S['vk']}" target="_blank" rel="noopener">vk.com/velvetlaser11</a></dd></div>
  </dl></div>
  <div class="map"><iframe src="{S['map_widget']}" title="Velvet Laser на карте" loading="lazy" allowfullscreen></iframe></div>
</div></section>"""


def lead_form(title, options, cta):
    opts = "".join(
        f'<label><input type="radio" name="offer" value="{v}"{" checked" if i == 0 else ""}><span>{t}</span></label>'
        for i, (v, t) in enumerate(options))
    return f"""<section id="zapis"><div class="wrap two-col">
  <div><span class="eyebrow">Запись</span><h2>{title}</h2>
  <p class="muted">Оставьте номер — администратор позвонит в течение {S['callback_minutes']} минут с 09:00 до 21:00 и подберёт удобное время.</p>
  <p class="small muted">Цены — {P['for_whom']}, до {P['until']}.</p></div>
  <form class="form-card lead-form" novalidate>
    <div class="field"><label>Что выбираете</label><div class="choice">{opts}</div></div>
    <div class="field"><label for="f-name">Как к вам обращаться</label><input id="f-name" name="name" autocomplete="given-name" required></div>
    <div class="field"><label for="f-phone">Телефон</label><input id="f-phone" name="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="+7 (___) ___-__-__" required></div>
    <div class="field"><label>Когда удобнее прийти</label><div class="choice">
      <label><input type="radio" name="time" value="утро"><span>Утро</span></label>
      <label><input type="radio" name="time" value="день"><span>День</span></label>
      <label><input type="radio" name="time" value="вечер"><span>Вечер</span></label>
    </div></div>
    <div aria-hidden="true" style="position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden"><label>Сайт<input name="website" tabindex="-1" autocomplete="off"></label></div>
    <label class="agree"><input type="checkbox" name="agree" value="1"><span>Даю <a href="/soglasie/" target="_blank">согласие на обработку персональных данных</a> и подтверждаю, что ознакомлен(а) с <a href="/politika/" target="_blank">политикой</a>.</span></label>
    <button class="btn btn-block" type="submit" data-label="{cta}">{cta}</button>
    <div class="form-msg" role="status" aria-live="polite"></div>
    <div class="form-alt">
      <a class="btn btn-ghost" href="tel:{S['phone_link']}">Позвонить</a>
      <a class="btn btn-ghost" href="{S['vk_write']}" target="_blank" rel="noopener">Написать в ВК</a>
    </div>
  </form>
</div></section>"""


def faq(items):
    body = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in items)
    return f"""<section class="alt"><div class="wrap two-col">
  <div><span class="eyebrow">Вопросы</span><h2>Что обычно спрашивают</h2></div>
  <div class="faq">{body}</div>
</div></section>"""


def rules_list(extra):
    li = "".join(f"<li>{x}</li>" for x in extra)
    return f"""<div class="rules"><b>Условия акции</b><ul>
  <li>Цена действует {P['for_whom']} — одна акционная процедура на гостя.</li>
  <li>Срок — до {P['until']} включительно.</li>
  {li}
  <li>Оформите абонемент в течение {P['trial_free_days']} дней после пробного визита — его стоимость вычтем из абонемента.</li>
  <li>Количество мест ограничено расписанием мастеров. <a href="/akciya/">Полные правила акции</a></li>
</ul></div>"""


# ---------- Массаж лица ----------
def page_face():
    o = O["face"]
    dur = f"<span>{o['duration']}</span>" if o.get("duration") else ""
    h = head("Массаж лица за 1 290 ₽ в Сыктывкаре — Velvet Laser",
             f"Классический, скульптурный или буккальный массаж лица за 1 290 ₽ для первого посещения, до {P['until']}. Студия в центре Сыктывкара, {S['address']}.",
             "/massazh-lica/")
    body = f"""
<main>
<section class="hero"><div class="wrap">
  <div>
    <span class="eyebrow">Для первого посещения · до {P['until']}</span>
    <h1>Массаж лица за&nbsp;{rub(o['price'])}</h1>
    <p class="lead">Время, когда заботятся о вас. Классический, скульптурный или буккальный — выберите сами или решите вместе с мастером.</p>
    <div class="price-line"><span class="price-now">{rub(o['price'])}</span><span class="price-old">обычно <s>{o['price_regular']}</s></span></div>
    <div class="hero-cta">
      <a class="btn" href="#zapis">Записаться за {rub(o['price'])}</a>
      <a class="btn btn-ghost" href="#zapis">Вдвоём с подругой — {rub(o['pair_price'])}</a>
    </div>
    <div class="hero-note">Оформите абонемент в течение {P['trial_free_days']} дней — <b>пробный визит станет бесплатным</b>: его стоимость вычтем.</div>
    <div class="facts"><span>центр, {S['address']}</span><span>с 09:00 до 21:00</span><span>чай после процедуры</span>{dur}</div>
    <p class="warning-line">{L['warning']}</p>
  </div>
  <div class="hero-photo">{img('face-hero', 'Массаж лица в студии Velvet Laser', big=True, eager=True)}</div>
</div></section>

<section class="alt"><div class="wrap">
  <div class="sec-head"><span class="eyebrow">Три массажа на выбор</span><h2>Какой массаж выбрать</h2>
  <p class="muted">Все три — по одной цене. Не знаете, что ближе, — мастер подскажет на месте.</p></div>
  <ol class="steps steps-3">
    <li><b>Классический</b><span>Мягкие, размеренные движения по лицу и шее. Подходит, чтобы просто отдохнуть и выдохнуть.</span></li>
    <li><b>Скульптурный</b><span>Более глубокая и плотная проработка. По ощущениям интенсивнее классического.</span></li>
    <li><b>Буккальный</b><span>Мастер работает в том числе с внутренней стороны щёк — в перчатках, аккуратно и с вашего согласия.</span></li>
  </ol>
</div></section>

<section><div class="wrap split rev">
  <div class="split-photo">{img('face-master', 'Мастер делает массаж лица', big=True)}</div>
  <div><span class="eyebrow">Как проходит визит</span><h2>Спокойно и без спешки</h2>{visit_steps()}</div>
</div></section>

{studio_block([('tea', 'Кофе и чай в зоне отдыха', ''), ('face-hands', 'Массаж лица', ''), ('decor', 'Интерьер студии', ''), ('art', 'Картина в студии', ''), ('outside', 'Вход в студию Velvet Laser с улицы', 'wide'), ('reception', 'Стойка администратора', ''), ('face-calm', 'Гостья на массаже лица', '')])}

{team_block()}

<section id="ceny" class="alt"><div class="wrap">
  <div class="sec-head"><span class="eyebrow">Цены</span><h2>Сколько стоит</h2></div>
  <table class="price-table">
    <thead><tr><th>Что</th><th>Обычно</th><th>По акции</th></tr></thead>
    <tbody>
      <tr><td>Массаж лица — классический, скульптурный или буккальный</td><td class="num"><s>{o['price_regular']}</s></td><td class="num accent">{rub(o['price'])}</td></tr>
      <tr><td>Вдвоём с подругой — два массажа лица, обе впервые в студии</td><td class="num"><s>{rub(o['price'] * 2)}</s></td><td class="num accent">{rub(o['pair_price'])}</td></tr>
      <tr><td>Курс после пробного: 5 процедур</td><td class="num" colspan="2">от 10&nbsp;000 до 12&nbsp;500&nbsp;₽</td></tr>
    </tbody>
  </table>
  {rules_list(["«Вдвоём с подругой» — для двух гостей, которые приходят в студию впервые."])}
</div></section>

<section><div class="wrap two-col">
  <div><span class="eyebrow">Важно</span><h2>Кому процедура не подойдёт</h2>
  <p class="muted">Если сомневаетесь — напишите нам до записи, мы подскажем.</p></div>
  <div class="contra">Массаж лица не проводится при беременности и лактации, онкологических заболеваниях, острых инфекционных заболеваниях, кожных заболеваниях в зоне массажа, эпилепсии, кардиостимуляторе.
  <span class="warn">{L['warning']}</span></div>
</div></section>

{faq([
    ("Это больно?", "Нет. Ощущения как от плотного массажа. Мастер спрашивает, комфортно ли вам, и меняет интенсивность."),
    ("Какой массаж выбрать?", "Любой из трёх стоит 1 290 ₽. Если не знаете, что ближе, — мастер подскажет на месте, исходя из ваших ожиданий."),
    ("Будут ли уговаривать на курс?", f"Нет. Мастер расскажет о курсе, только если вы спросите. Если решите оформить абонемент в течение {P['trial_free_days']} дней, пробный визит станет бесплатным — его стоимость вычтем."),
    ("Сколько процедур нужно?", "Зависит от вашей задачи. Мастер честно скажет после первой процедуры."),
    ("Я уже была у вас. Акция для меня?", "Цена действует для первого посещения студии. Для постоянных гостей есть абонементы и программа «для подруг»: 1 000 ₽ на баланс за каждую приглашённую."),
    ("Как прийти вдвоём с подругой?", f"Выберите в форме «Вдвоём с подругой» — два массажа лица за {rub(o['pair_price'])}. Акция для двух гостей, которые приходят в студию впервые."),
    ("Можно подарить?", "Да, у нас есть подарочный сертификат на любой номинал."),
    ("Как перенести запись?", "Напишите или позвоните нам не позже чем за 24 часа."),
])}

{lead_form('Записаться на массаж лица', [('Массаж лица — 1290', f"Массаж лица — {rub(o['price'])}"), ('Вдвоём с подругой — 2290', f"Вдвоём с подругой — {rub(o['pair_price'])}")], f"Записаться за {rub(o['price'])}")}

{contacts_block()}

<section><div class="wrap">
  <div class="cross">
    <div><span class="eyebrow" style="color:#e6b9c0">Для тела</span><h3>LPG-массаж за {rub(O['lpg']['price'])}</h3>
    <p>{O['lpg']['duration'].capitalize()} аппаратного массажа тела. Тоже для первого посещения, до {P['until']}.</p>
    <p style="margin-top:16px"><a class="btn" href="/{O['lpg']['slug']}/">Подробнее</a></p></div>
    {img('lpg-hero', 'LPG-массаж в студии')}
  </div>
</div></section>
</main>
"""
    return h + body + footer(f"Записаться за {rub(o['price'])}")


# ---------- LPG ----------
def page_lpg():
    o = O["lpg"]
    h = head("LPG-массаж за 890 ₽ в Сыктывкаре — Velvet Laser",
             f"LPG-массаж 40 минут за 890 ₽ для первого посещения, до {P['until']}. Или вакуумный массаж всего тела без костюма. Центр Сыктывкара, {S['address']}.",
             "/lpg/")
    body = f"""
<main>
<section class="hero"><div class="wrap">
  <div>
    <span class="eyebrow">Для первого посещения · до {P['until']}</span>
    <h1>LPG-массаж за&nbsp;{rub(o['price'])}</h1>
    <p class="lead">{o['duration'].capitalize()} аппаратного массажа тела — ощущение лёгкости и время, которое вы посвящаете себе.</p>
    <div class="price-line"><span class="price-now">{rub(o['price'])}</span><span class="price-old">обычно <s>{o['price_regular']}</s></span></div>
    <div class="hero-cta">
      <a class="btn" href="#zapis">Записаться за {rub(o['price'])}</a>
      <a class="btn btn-ghost" href="#vybor">Без костюма — вакуумный массаж за {rub(o['vacuum_price'])}</a>
    </div>
    <div class="hero-note">Для LPG нужен личный костюм — <b>{rub(o['suit_price'])}</b>. Он остаётся у вас и пригодится на курсе. Оформите абонемент в течение {P['trial_free_days']} дней — пробный визит станет бесплатным.</div>
    <div class="facts"><span>центр, {S['address']}</span><span>с 09:00 до 21:00</span><span>чай после процедуры</span></div>
    <p class="warning-line">{L['warning']}</p>
  </div>
  <div class="hero-photo">{img('lpg-hero', 'LPG-массаж в студии Velvet Laser', big=True, eager=True)}</div>
</div></section>

<section id="vybor" class="alt"><div class="wrap">
  <div class="sec-head"><span class="eyebrow">Два варианта</span><h2>LPG или вакуум</h2>
  <p class="muted">Оба — по {rub(o['price'])} для первого посещения. Выберите, что ближе.</p></div>
  <ol class="steps">
    <li><b>LPG-массаж · {o['duration']}</b><span>Аппарат с роликами работает по телу через специальный костюм. Обычно {o['price_regular']}, по акции — {rub(o['price'])} + личный костюм {rub(o['suit_price'])}.</span></li>
    <li><b>Вакуумный массаж всего тела</b><span>Аппаратный массаж без костюма. Обычно {o['vacuum_regular']}, по акции — {rub(o['vacuum_price'])}.</span></li>
  </ol>
</div></section>

<section><div class="wrap split rev">
  <div class="split-photo">{img('lpg-process', 'Мастер проводит LPG-массаж', big=True)}</div>
  <div><span class="eyebrow">Как проходит визит</span><h2>Спокойно и без спешки</h2>{visit_steps()}</div>
</div></section>

{studio_block([('tea', 'Кофе и чай в зоне отдыха', ''), ('lpg-arc', 'Аппарат для LPG-массажа', ''), ('decor', 'Интерьер студии', ''), ('room', 'Кабинет студии', ''), ('outside', 'Вход в студию Velvet Laser с улицы', 'wide'), ('reception', 'Стойка администратора', ''), ('art', 'Картина в студии', '')])}

{team_block()}

<section id="ceny" class="alt"><div class="wrap">
  <div class="sec-head"><span class="eyebrow">Цены</span><h2>Сколько стоит</h2></div>
  <table class="price-table">
    <thead><tr><th>Что</th><th>Обычно</th><th>По акции</th></tr></thead>
    <tbody>
      <tr><td>LPG-массаж, {o['duration']}</td><td class="num"><s>{o['price_regular']}</s></td><td class="num accent">{rub(o['price'])}</td></tr>
      <tr><td>Личный костюм для LPG — остаётся у вас</td><td class="num" colspan="2">{rub(o['suit_price'])}</td></tr>
      <tr><td>Вакуумный массаж всего тела, без костюма</td><td class="num"><s>{o['vacuum_regular']}</s></td><td class="num accent">{rub(o['vacuum_price'])}</td></tr>
      <tr><td>Курс LPG после пробного: 10 процедур</td><td class="num" colspan="2">16&nbsp;000&nbsp;₽</td></tr>
      <tr><td>Курс вакуумного массажа всего тела: 10 процедур</td><td class="num" colspan="2">14&nbsp;900&nbsp;₽</td></tr>
    </tbody>
  </table>
  {rules_list(["Акционная цена — на LPG-массаж или на вакуумный массаж всего тела, на выбор."])}
</div></section>

<section><div class="wrap two-col">
  <div><span class="eyebrow">Важно</span><h2>Кому процедура не подойдёт</h2>
  <p class="muted">Если сомневаетесь — напишите нам до записи, мы подскажем.</p></div>
  <div class="contra"><b>LPG-массаж</b> не проводится при заболеваниях крови и склонности к тромбообразованию, туберкулёзе, опухолях, индивидуальной непереносимости массажа, нарушениях психики. Процедуру откладываем при лихорадке, острых заболеваниях и инфекциях, интоксикации, заболеваниях кожи, кровотечениях, во время беременности и менструации.
  <p style="margin:12px 0 0"><b>Вакуумный массаж</b> — противопоказания администратор уточнит при записи.</p>
  <span class="warn">{L['warning']}</span></div>
</div></section>

{faq([
    ("Это больно?", "Нет. Ощущения как от плотного массажа. Мастер спрашивает, комфортно ли вам, и меняет интенсивность."),
    ("Зачем костюм?", f"LPG-массаж проводится через специальный костюм. Он личный, стоит {rub(o['suit_price'])} и остаётся у вас — на курсе его не нужно покупать снова. Не хотите костюм — выберите вакуумный массаж всего тела по той же цене."),
    ("Что выбрать — LPG или вакуум?", "Обе процедуры — аппаратный массаж тела. Если сомневаетесь, расскажите администратору о своих ожиданиях — подскажем."),
    ("Будут ли уговаривать на курс?", f"Нет. Мастер расскажет о курсе, только если вы спросите. Если решите оформить абонемент в течение {P['trial_free_days']} дней, пробный визит станет бесплатным — его стоимость вычтем."),
    ("Сколько процедур нужно?", "Зависит от вашей задачи. Мастер честно скажет после первой процедуры."),
    ("Я уже была у вас. Акция для меня?", "Цена действует для первого посещения студии. Для постоянных гостей есть абонементы и программа «для подруг»: 1 000 ₽ на баланс за каждую приглашённую."),
    ("Как перенести запись?", "Напишите или позвоните нам не позже чем за 24 часа."),
])}

{lead_form('Записаться на LPG или вакуум', [('LPG — 890 + костюм 300', f"LPG — {rub(o['price'])} + костюм {rub(o['suit_price'])}"), ('Вакуум всего тела — 890', f"Вакуум всего тела — {rub(o['vacuum_price'])}")], f"Записаться за {rub(o['price'])}")}

{contacts_block()}

<section><div class="wrap">
  <div class="cross">
    <div><span class="eyebrow" style="color:#e6b9c0">Для лица</span><h3>Массаж лица за {rub(O['face']['price'])}</h3>
    <p>Классический, скульптурный или буккальный — на выбор. Тоже для первого посещения, до {P['until']}.</p>
    <p style="margin-top:16px"><a class="btn" href="/{O['face']['slug']}/">Подробнее</a></p></div>
    {img('face-hero', 'Массаж лица в студии')}
  </div>
</div></section>
</main>
"""
    return h + body + footer(f"Записаться за {rub(o['price'])}")


# ---------- Главная ----------
def page_index():
    h = head("Velvet Laser — студия в центре Сыктывкара",
             f"Массаж лица за 1 290 ₽ и LPG-массаж за 890 ₽ для первого посещения, до {P['until']}. {S['address']}.", "/")
    body = f"""
<main><section class="hero"><div class="wrap" style="grid-template-columns:1fr">
  <div><span class="eyebrow">Для первого посещения · до {P['until']}</span>
  <h1>Время для себя — в центре Сыктывкара</h1>
  <p class="lead">Выберите процедуру, чтобы узнать подробности и записаться.</p></div>
  <div class="hub">
    <a href="/{O['face']['slug']}/"><img src="/assets/img/face-hero-s.webp" alt="Массаж лица" loading="lazy"><span><b>Массаж лица — {rub(O['face']['price'])}</b><span class="muted">обычно {O['face']['price_regular']}</span></span></a>
    <a href="/{O['lpg']['slug']}/"><img src="/assets/img/lpg-hero-s.webp" alt="LPG-массаж" loading="lazy"><span><b>LPG-массаж — {rub(O['lpg']['price'])}</b><span class="muted">обычно {O['lpg']['price_regular']}</span></span></a>
  </div>
  <p class="warning-line">{L['warning']}</p>
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
