/* Small, dependency-free controls for the pre-rendered sightings archive. */
(() => {
  'use strict';
  const data = JSON.parse(document.getElementById('sighting-data').textContent);
  const byId = new Map(data.entries.map(entry => [entry.id, entry]));
  const $ = id => document.getElementById(id);
  const el = (tag, text, className) => {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    if (className) node.className = className;
    return node;
  };
  const link = (text, href, external = false) => {
    const node = el('a', text); node.href = href;
    if (external) { node.target = '_blank'; node.rel = 'noopener noreferrer'; }
    return node;
  };
  const formatDate = value => value ? new Date(value + 'T12:00:00').toLocaleDateString('en-US', {month:'long',day:'numeric',year:'numeric'}) : 'Flight date unconfirmed';
  const reportURL = entry => {
    const url = new URL('https://github.com/danahmadi/whosflyingoversf/issues/new');
    url.search = new URLSearchParams({template:'sighting.yml',date:entry.date || '',brand:entry.brand === 'Unknown' ? '' : data.brands[entry.brand].label});
    return url.href;
  };
  let view = 'calendar';
  const dated = data.entries.filter(entry => entry.date);
  const undated = data.entries.filter(entry => !entry.date);
  const byDate = new Map();
  for (const entry of dated) {
    if (!byDate.has(entry.date)) byDate.set(entry.date, []);
    byDate.get(entry.date).push(entry);
  }
  let selectedDate = new URLSearchParams(location.search).get('date') || '';
  if (!/^\d{4}-\d{2}-\d{2}$/.test(selectedDate)) selectedDate = '';
  const trackDates = new Set(data.flights.map(flight => flight.date));
  const months = [];
  if (dated.length) {
    const allDates = [...dated.map(entry => entry.date), ...trackDates, ...(selectedDate ? [selectedDate] : [])].sort();
    const first = allDates[0].slice(0,7);
    const last = allDates.at(-1).slice(0,7);
    let [year, month] = first.split('-').map(Number);
    while (`${year}-${String(month).padStart(2,'0')}` <= last) {
      const value = `${year}-${String(month).padStart(2,'0')}`;
      months.push(value);
      const option = el('option', new Date(year, month - 1, 1).toLocaleDateString('en-US', {month:'long',year:'numeric'}));
      option.value = value; $('month').append(option);
      month++; if (month === 13) {month = 1; year++;}
    }
  }
  $('month').value = selectedDate ? selectedDate.slice(0,7) : months.at(-1) || '';
  function badge(entry) {
    const brand = data.brands[entry.brand];
    if (brand.logo) {
      const image = el('img'); image.src = '/' + brand.logo; image.alt = ''; image.className = 'logo';
      return image;
    }
    const node = el('span', entry.brand === 'Unknown' ? '?' : brand.label[0], 'badge');
    node.style.backgroundColor = brand.color;
    return node;
  }
  function openEvidence(entry, updateHash = true) {
    if (!entry) return;
    if (entry.date) selectDate(entry.date);
    const brand = data.brands[entry.brand];
    const body = $('evidence-body'); body.replaceChildren();
    $('evidence-date').textContent = formatDate(entry.date);
    const title = el('h2', entry.texts[0] || brand.label); title.id = 'evidence-title'; body.append(title);
    body.append(el('p', brand.label + (entry.brand === 'Pylon' ? ' · drone airship' : ''), 'sighting-brand'));
    if (entry.texts.length > 1) body.append(el('p', 'Other wording in the sources: ' + entry.texts.slice(1).join(' / '), 'small'));
    body.append(el('p', brand.description));
    if (brand.url) body.append(link('Brand website', brand.url, true));
    body.append(el('h3', 'The sources'));
    entry.sources.forEach(source => {
      const article = el('article', undefined, 'source');
      article.append(el('h4', source.source + (source.author ? ' · @' + source.author : '')));
      const labels = [source.photo ? 'Source includes a photo' : 'Text report'];
      if (source.posted) labels.push('Posted ' + formatDate(source.posted));
      article.append(el('p', labels.join(' · '), 'small'));
      if (source.note) article.append(el('p', source.note));
      if (source.url) article.append(link('Open original source ↗', source.url, true));
      else article.append(el('p', 'Submitted directly. No public source link is available.', 'small'));
      body.append(article);
    });
    if (!entry.date) body.append(el('p', 'We have not established the flight date. This report is excluded from the calendar and day counts.', 'notice'));
    const flights = entry.date && data.flights.filter(flight => flight.date === entry.date);
    if (flights && flights.length) {
      const note = el('p', `${flights.length} possible banner-tow track${flights.length === 1 ? '' : 's'} on this date. The flight data does not identify the banner or advertiser. `, 'notice');
      note.append(link('See the flight map', '/map?date=' + entry.date)); body.append(note);
    }
    const actions = el('p', undefined, 'evidence-actions');
    actions.append(link('Link to this sighting', '/#sighting=' + entry.id), link('Add evidence or correct this entry', reportURL(entry)));
    body.append(actions);
    if (!$('evidence').open) $('evidence').showModal();
    if (updateHash) history.replaceState(null, '', '#sighting=' + entry.id);
  }
  function card(entry) {
    const brand = data.brands[entry.brand];
    const article = el('article', undefined, 'sighting');
    const date = el('div', formatDate(entry.date), 'sighting-date');
    date.append(el('span', entry.sources.some(source => source.photo) ? 'Photo linked' : entry.sources.every(source => !source.url) ? 'Reader report' : 'Text report'));
    const content = el('div');
    const button = el('button', undefined, 'sighting-open');
    button.append(badge(entry), el('span', entry.texts[0] || brand.label));
    button.addEventListener('click', () => openEvidence(entry));
    const heading = el('h3'); heading.append(button); content.append(heading);
    content.append(el('p', `${brand.label}${entry.brand === 'Pylon' ? ' · drone airship' : ''} · ${entry.sources.length} source${entry.sources.length === 1 ? '' : 's'}`, 'sighting-brand'));
    article.append(date, content); return article;
  }
  function drawCalendar() {
    const grid = $('grid'); grid.replaceChildren();
    const value = $('month').value;
    if (!value) { grid.append(el('p','No dated sightings yet.')); return; }
    const [year, month] = value.split('-').map(Number);
    const index = months.indexOf(value);
    $('prev').disabled = index <= 0; $('next').disabled = index >= months.length - 1;
    ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'].forEach(day => grid.append(el('div',day,'dow')));
    for (let i=0; i<new Date(year,month-1,1).getDay(); i++) grid.append(el('div',undefined,'day empty'));
    for (let day=1; day<=new Date(year,month,0).getDate(); day++) {
      const key = `${value}-${String(day).padStart(2,'0')}`;
      const box = el('div', undefined, 'day'); box.dataset.date = key;
      const dayButton = el('button', String(day), 'num day-select');
      dayButton.setAttribute('aria-label', `${formatDate(key)}. Show flight tracks${trackDates.has(key) ? ', tracks available' : ''}.`);
      dayButton.setAttribute('aria-pressed', String(selectedDate === key));
      box.classList.toggle('selected', selectedDate === key);
      if (trackDates.has(key)) dayButton.classList.add('has-tracks');
      box.append(dayButton);
      box.addEventListener('click', event => {
        if (event.target.closest('.day-entry')) return;
        selectDate(key);
        if (window.matchMedia('(max-width: 1000px)').matches) $('map-title').scrollIntoView({block:'start'});
      });
      (byDate.get(key) || []).forEach(entry => {
        box.classList.add('has');
        const button = el('button', undefined, 'day-entry');
        button.setAttribute('aria-label', `${data.brands[entry.brand].label}, ${formatDate(key)}. View evidence.`);
        button.title = data.brands[entry.brand].label;
        button.append(badge(entry)); button.addEventListener('click', () => openEvidence(entry)); box.append(button);
      });
      grid.append(box);
    }
  }
  function showSelectedDay() {
    $('selected-day').hidden = !selectedDate || view !== 'calendar';
    if (!selectedDate) return;
    $('selected-day-title').textContent = 'Sightings on ' + formatDate(selectedDate);
    const entries = byDate.get(selectedDate) || [];
    $('selected-day-results').replaceChildren(...entries.map(card));
    if (!entries.length) $('selected-day-results').append(el('p', 'No sighting reports for this date yet.', 'small'));
  }
  function selectDate(date) {
    document.dispatchEvent(new CustomEvent('sighting-date-selected', {detail:{date}}));
  }
  document.addEventListener('sighting-date-selected', event => {
    selectedDate = event.detail.date || '';
    const url = new URL(location.href);
    if (selectedDate) url.searchParams.set('date', selectedDate); else url.searchParams.delete('date');
    history.replaceState(null, '', url);
    document.querySelectorAll('.day[data-date]').forEach(day => {
      const selected = day.dataset.date === selectedDate;
      day.classList.toggle('selected', selected);
      day.querySelector('.day-select').setAttribute('aria-pressed', String(selected));
    });
    showSelectedDay();
  });
  function render() {
    const count = view === 'calendar' ? dated.filter(entry => entry.date.startsWith($('month').value)).length : dated.length;
    $('result-count').textContent = `${count} dated sighting${count === 1 ? '' : 's'}${view === 'calendar' ? ' this month' : ''} · one entry per brand per day`;
    drawCalendar();
    showSelectedDay();
  }
  function setView(nextView) {
    view = nextView;
    $('recent').hidden = view !== 'list'; $('calendar').hidden = view !== 'calendar';
    $('list-view').setAttribute('aria-pressed', String(view === 'list'));
    $('calendar-view').setAttribute('aria-pressed', String(view === 'calendar'));
    render();
  }
  // Archive data is immutable; month and view changes update the calendar and selection.
  $('results').replaceChildren(...dated.map(card));
  if (!dated.length) {
    const empty = el('div', undefined, 'empty-state');
    empty.append(el('h2','No dated sightings yet.'),el('p','Report a banner you saw to start the archive.'),link('Report a sighting',reportURL({date:'',brand:'Unknown'})));
    $('results').append(empty);
  }
  $('undated-results').replaceChildren(...undated.map(card));
  $('undated').hidden = !undated.length;
  $('undated').querySelector('summary').textContent = `Reports without a confirmed flight date (${undated.length})`;
  $('viewbar').hidden = false;
  $('list-view').addEventListener('click', () => setView('list'));
  $('calendar-view').addEventListener('click', () => setView('calendar'));
  $('month').addEventListener('change', render);
  $('prev').addEventListener('click', () => {$('month').value=months[months.indexOf($('month').value)-1];render();});
  $('next').addEventListener('click', () => {$('month').value=months[months.indexOf($('month').value)+1];render();});
  $('close-evidence').addEventListener('click', () => $('evidence').close());
  $('evidence').addEventListener('click', event => {if(event.target === $('evidence')) {const r=$('evidence').getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)$('evidence').close();}});
  $('evidence').addEventListener('close', () => {if(location.hash.startsWith('#sighting='))history.replaceState(null,'',location.pathname+location.search);});
  function fromHash() {
    const params = new URLSearchParams(location.hash.slice(1));
    if (params.has('sighting')) openEvidence(byId.get(params.get('sighting')),false);
    // Keep links generated by the original calendar usable.
    const legacy = location.hash.match(/^#(\d{4}-\d{2}-\d{2}):(.+)$/);
    if (legacy) {try {openEvidence(data.entries.find(entry => entry.date===legacy[1] && entry.brand===decodeURIComponent(legacy[2])),false);} catch { /* malformed fragment */ }}
  }
  setView('calendar');
  fromHash(); window.addEventListener('hashchange',fromHash);
})();
