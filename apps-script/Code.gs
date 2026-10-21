/**
 * Velvet Laser — приём заявок с сайта.
 * Получает заявку из формы, записывает её строкой в таблицу и шлёт сообщение в Telegram-группу.
 *
 * Свойства скрипта (Настройки проекта → Свойства скрипта):
 *   TG_TOKEN — токен бота от @BotFather
 *   TG_CHAT  — номер группы «Заявки Velvet»: -5376920455
 */

var SHEET_ID = '1RsepwU00Z3D6Ww7scYP6Am7HZ4bqlAKo9PV8jEcuI70'; // таблица «Заявки Velvet — сайт»
var SHEET_NAME = 'Заявки';
var HEADERS = ['Дата и время', 'Имя', 'Телефон', 'Процедура', 'Когда удобно', 'Страница',
  'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'yclid', 'Telegram'];

function doPost(e) {
  try {
    var d = JSON.parse((e && e.postData && e.postData.contents) || '{}');

    // Ловушка для ботов: скрытое поле, которое человек не заполняет
    if (d.website) return json_({ ok: true });

    var name = clean_(d.name, 60);
    var phone = String(d.phone || '').replace(/\D/g, '');
    if (phone.length === 11 && phone.charAt(0) === '8') phone = '7' + phone.slice(1);
    if (!name || phone.length !== 11 || phone.charAt(0) !== '7') return json_({ ok: false, error: 'bad_input' });
    phone = '+' + phone;

    // Защита от повторной отправки: одна заявка с номера раз в 2 минуты
    var cache = CacheService.getScriptCache();
    if (cache.get('p' + phone)) return json_({ ok: true, duplicate: true });
    cache.put('p' + phone, '1', 120);

    var lead = {
      at: Utilities.formatDate(new Date(), 'Europe/Moscow', 'dd.MM.yyyy HH:mm'),
      name: name,
      phone: phone,
      offer: clean_(d.offer, 80),
      time: clean_(d.time, 20),
      page: clean_(d.page, 80),
      utm_source: clean_(d.utm_source, 80),
      utm_medium: clean_(d.utm_medium, 80),
      utm_campaign: clean_(d.utm_campaign, 120),
      utm_content: clean_(d.utm_content, 120),
      utm_term: clean_(d.utm_term, 120),
      yclid: clean_(d.yclid, 60)
    };

    var sent = sendTelegram_(lead);
    appendRow_(lead, sent ? 'отправлено' : 'ошибка');
    return json_({ ok: true });
  } catch (err) {
    console.error(err);
    return json_({ ok: false, error: 'server' });
  }
}

function doGet() {
  return json_({ ok: true, service: 'velvet-leads' });
}

function sendTelegram_(l) {
  var p = PropertiesService.getScriptProperties();
  var token = p.getProperty('TG_TOKEN'), chat = p.getProperty('TG_CHAT') || '-5376920455';
  if (!token || !chat) return false;

  var source = l.utm_source
    ? [l.utm_source, l.utm_medium, l.utm_campaign].filter(String).join(' / ')
    : 'прямой заход или без меток';
  var lines = [
    '<b>Новая заявка с сайта</b>',
    '',
    '<b>' + esc_(l.offer || 'процедура не выбрана') + '</b>',
    'Имя: ' + esc_(l.name),
    'Телефон: ' + esc_(l.phone),
    'Когда удобно: ' + esc_(l.time || 'не указано'),
    '',
    'Страница: ' + esc_(l.page),
    'Источник: ' + esc_(source)
  ];
  if (l.utm_term) lines.push('Запрос: ' + esc_(l.utm_term));
  lines.push('Получена: ' + l.at + ' (мск)');

  var res = UrlFetchApp.fetch('https://api.telegram.org/bot' + token + '/sendMessage', {
    method: 'post',
    contentType: 'application/json',
    muteHttpExceptions: true,
    payload: JSON.stringify({ chat_id: chat, text: lines.join('\n'), parse_mode: 'HTML', disable_web_page_preview: true })
  });
  if (res.getResponseCode() !== 200) console.error('Telegram: ' + res.getContentText());
  return res.getResponseCode() === 200;
}

function appendRow_(l, tgStatus) {
  var ss = SpreadsheetApp.openById(SHEET_ID);
  var sh = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);
  if (sh.getLastRow() === 0) {
    sh.appendRow(HEADERS);
    sh.setFrozenRows(1);
    sh.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold');
  }
  // Телефон записываем как текст, чтобы таблица не превратила его в число
  sh.appendRow([l.at, l.name, "'" + l.phone, l.offer, l.time, l.page,
    l.utm_source, l.utm_medium, l.utm_campaign, l.utm_content, l.utm_term, l.yclid, tgStatus]);
}

function clean_(v, max) {
  return String(v == null ? '' : v).replace(/[\u0000-\u001f]/g, ' ').trim().slice(0, max);
}

function esc_(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function json_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}

/** Запустите вручную из редактора, чтобы проверить отправку в Telegram. */
function testTelegram() {
  var ok = sendTelegram_({
    at: Utilities.formatDate(new Date(), 'Europe/Moscow', 'dd.MM.yyyy HH:mm'),
    name: 'Тест', phone: '+70000000000', offer: 'Проверка связи', time: 'день',
    page: '/test/', utm_source: '', utm_medium: '', utm_campaign: '', utm_term: ''
  });
  Logger.log(ok ? 'Сообщение отправлено' : 'Не отправлено — проверьте TG_TOKEN и TG_CHAT');
}
