(function () {
  var C = window.VL || {};

  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }
  function goal(name, details) {
    try { if (C.metrika && window.ym) window.ym(C.metrika, 'reachGoal', name, details || {}); } catch (e) {}
    try { if (window.VK && window.VK.Goal) window.VK.Goal(name === 'lead' ? 'lead' : 'conversion'); } catch (e) {}
  }

  // UTM-метки: запоминаем на время визита, чтобы отправить вместе с заявкой
  var utmKeys = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'yclid'];
  var params = new URLSearchParams(location.search);
  var utm = {};
  utmKeys.forEach(function (k) {
    var v = params.get(k);
    try { if (v) sessionStorage.setItem(k, v); utm[k] = v || sessionStorage.getItem(k) || ''; } catch (e) { utm[k] = v || ''; }
  });

  // Липкая кнопка на телефоне
  var sticky = document.querySelector('.sticky-cta');
  var hero = document.querySelector('.hero');
  var form = document.getElementById('zapis');
  if (sticky && hero && 'IntersectionObserver' in window) {
    var heroVisible = true, formVisible = false;
    var upd = function () { sticky.classList.toggle('show', !heroVisible && !formVisible); };
    new IntersectionObserver(function (e) { heroVisible = e[0].isIntersecting; upd(); }).observe(hero);
    if (form) new IntersectionObserver(function (e) { formVisible = e[0].isIntersecting; upd(); }).observe(form);
  }

  // Цели на клики
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a');
    if (!a) return;
    var h = a.getAttribute('href') || '';
    if (h.indexOf('tel:') === 0) goal('phone');
    else if (h.indexOf('vk.com') > -1) goal('vk');
    else if (h.indexOf('yandex.ru/maps') > -1) goal('maps');
    else if (h === '#zapis') {
      goal('cta');
      var targetForm = document.querySelector('form.lead-form');
      if (targetForm) {
        e.preventDefault();
        var requested = a.getAttribute('data-book-offer');
        if (requested) {
          var option = targetForm.querySelector('input[name=offer][data-book-offer="' + requested + '"]');
          if (option) option.checked = true;
        }
        targetForm.style.scrollMarginTop = '82px';
        targetForm.scrollIntoView({ behavior: 'instant', block: 'start' });
      }
    }
  });

  // Прокрутка до цены
  var priceSec = document.getElementById('ceny') || document.getElementById('zapis');
  if (priceSec && 'IntersectionObserver' in window) {
    var seen = false;
    new IntersectionObserver(function (e) { if (e[0].isIntersecting && !seen) { seen = true; goal('price'); } }).observe(priceSec);
  }

  // Форма записи
  var f = document.querySelector('form.lead-form');
  if (f) {
    var msg = f.querySelector('.form-msg');
    var phone = f.querySelector('input[name=phone]');
    var started = false;
    phone.addEventListener('input', function () {
      var raw = phone.value;
      var cursor = phone.selectionStart;
      var atEnd = cursor === raw.length;
      var digitsBefore = raw.slice(0, cursor).replace(/\D/g, '').length;
      var d = raw.replace(/\D/g, '');
      if (d[0] === '8') d = '7' + d.slice(1);
      if (d && d[0] !== '7') { d = '7' + d; digitsBefore++; }
      d = d.slice(0, 11);
      var out = '+7';
      if (d.length > 1) out += ' (' + d.slice(1, 4);
      if (d.length > 4) out += ') ' + d.slice(4, 7);
      if (d.length > 7) out += '-' + d.slice(7, 9);
      if (d.length > 9) out += '-' + d.slice(9, 11);
      phone.value = d.length ? out : '';
      if (phone.setSelectionRange) {
        var pos = atEnd ? phone.value.length : 0, count = 0;
        if (!atEnd) {
          while (pos < phone.value.length && count < digitsBefore) {
            if (/\d/.test(phone.value[pos])) count++;
            pos++;
          }
        }
        phone.setSelectionRange(pos, pos);
      }
      if (!started && d.length > 1) { started = true; goal('form_start'); }
    });
    if ('IntersectionObserver' in window) {
      var viewed = false;
      new IntersectionObserver(function (entries) {
        if (!viewed && entries[0].isIntersecting) { viewed = true; goal('form_view'); }
      }, { threshold: 0.5 }).observe(phone);
    }
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      msg.className = 'form-msg';
      var data = new FormData(f);
      var digits = (data.get('phone') || '').replace(/\D/g, '');
      if (digits.length !== 11 || digits[0] !== '7') {
        goal('form_error', { reason: 'phone' });
        msg.className = 'form-msg err'; msg.textContent = 'Проверьте номер телефона — он должен начинаться с +7 и содержать 11 цифр.'; return;
      }
      if (!data.get('agree')) {
        goal('form_error', { reason: 'consent' });
        msg.className = 'form-msg err'; msg.textContent = 'Отметьте согласие на обработку персональных данных — без него мы не можем принять заявку.'; return;
      }
      var payload = {
        name: (data.get('name') || '').trim() || 'Имя не указано', phone: '+' + digits, time: data.get('time') || '',
        offer: data.get('offer') || '', page: location.pathname, sent_at: new Date().toISOString(),
        website: data.get('website') || ''
      };
      utmKeys.forEach(function (k) { payload[k] = utm[k]; });
      var btn = f.querySelector('button[type=submit]');
      if (!C.endpoint) {
        msg.className = 'form-msg err';
        msg.innerHTML = 'Онлайн-запись скоро заработает. Пока позвоните нам: <a href="tel:' + C.phoneLink + '">' + C.phone + '</a> или <a href="' + C.vkWrite + '" target="_blank" rel="noopener">напишите в ВК</a>.';
        return;
      }
      goal('form_submit');
      btn.disabled = true; btn.textContent = 'Отправляем…';
      // text/plain avoids a preflight; CORS lets us verify the server acknowledgement.
      fetch(C.endpoint, { method: 'POST', mode: 'cors', credentials: 'omit', headers: { 'Content-Type': 'text/plain;charset=utf-8' }, body: JSON.stringify(payload) })
        .then(function (r) {
          if (!r.ok || r.type === 'opaque') throw new Error('delivery_unconfirmed');
          return r.json();
        })
        .then(function (result) {
          if (!result || result.ok !== true) throw new Error('delivery_rejected');
        })
        .then(function () {
          goal('lead');
          f.reset();
          msg.className = 'form-msg ok';
          msg.innerHTML = 'Спасибо! Администратор позвонит в течение ' + C.callback + ' минут с 09:00 до 21:00. Если удобнее переписка — <a href="' + C.vkWrite + '" target="_blank" rel="noopener">напишите нам в ВК</a>.';
        })
        .catch(function () {
          goal('form_error', { reason: 'delivery' });
          msg.className = 'form-msg err';
          msg.innerHTML = 'Не удалось подтвердить отправку заявки. Данные остались в форме. Позвоните нам: <a href="tel:' + C.phoneLink + '">' + C.phone + '</a> — запишем по телефону.';
        })
        .then(function () { btn.disabled = false; btn.textContent = btn.getAttribute('data-label'); });
    });
  }

  // Уведомление о cookie
  var ck = document.querySelector('.cookie');
  if (ck && store('vl_cookie') !== '1') {
    ck.classList.add('show');
    if (sticky) sticky.style.bottom = '96px';
    ck.querySelector('button').addEventListener('click', function () {
      store('vl_cookie', '1'); ck.classList.remove('show'); if (sticky) sticky.style.bottom = '';
    });
  }
})();
