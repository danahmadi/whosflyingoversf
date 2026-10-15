// Exercise the shipped scripts through their DOM events without a browser dependency.
// The small DOM/Leaflet doubles cover state; real rendering is checked in a browser.
const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const path = require('node:path');
const {test} = require('node:test');
const vm = require('node:vm');
const site = path.join(__dirname, '../site');

class Element {
  constructor(tag = 'div') {
    this.tag = tag; this.children = []; this.events = {}; this.attrs = {};
    this.dataset = {}; this.style = {}; this.value = ''; this.textContent = '';
    this.className = ''; this.hidden = false; this.checked = false;
    this.classList = {
      add: name => this.classList.toggle(name, true),
      toggle: (name, on) => {
        const classes = new Set(this.className.split(' ').filter(Boolean));
        if (on) classes.add(name); else classes.delete(name);
        this.className = [...classes].join(' ');
      }
    };
  }
  append(...nodes) { this.children.push(...nodes); }
  replaceChildren(...nodes) { this.children = nodes; }
  setAttribute(name, value) { this.attrs[name] = value; }
  addEventListener(type, handler) { (this.events[type] ||= []).push(handler); }
  dispatchEvent(event) {
    event.target ||= this; event.preventDefault ||= () => {};
    for (const handler of this.events[event.type] || []) handler(event);
  }
  all() { return this.children.flatMap(node => [node, ...node.all()]); }
  querySelector(selector) {
    return this.all().find(node => selector.startsWith('.')
      ? node.className.split(' ').includes(selector.slice(1)) : node.tag === selector);
  }
  showModal() { this.open = true; }
  close() { this.open = false; this.dispatchEvent({type:'close'}); }
  scrollIntoView() {}
}

async function controls({page = 'index', query = '', entries, flights, failFetch = false} = {}) {
  const html = readFileSync(path.join(site, page + '.html'), 'utf8');
  const nodes = Object.fromEntries([...html.matchAll(/id="([^"]+)"/g)].map(([,id]) => [id, new Element()]));
  for (const [,id,json] of html.matchAll(/<script type="application\/json" id="([^"]+)">([\s\S]*?)<\/script>/g)) nodes[id].textContent = json;
  if (entries) {
    const data = JSON.parse(nodes['sighting-data'].textContent);
    data.entries = entries;
    nodes['sighting-data'].textContent = JSON.stringify(data);
  }
  if (page === 'index') nodes.undated.append(new Element('summary'));
  const document = new Element();
  document.getElementById = id => nodes[id] || null;
  document.createElement = tag => new Element(tag);
  document.querySelectorAll = () => nodes.grid.all().filter(node => node.dataset.date);
  const location = new URL('https://example.test/' + query);
  const history = {replaceState: (_, __, url) => { location.href = new URL(url, location).href; }};
  const panes = {}, layers = {lines: [], points: []};
  const map = {
    setView() { return this; }, getZoom: () => 11,
    createPane: name => { panes[name] = {style:{}}; }, getPane: name => panes[name],
    removeLayer() {}, invalidateSize() {}, fitBounds() {}, on() {}
  };
  const L = {
    map: () => map, tileLayer: () => ({addTo() {}}),
    layerGroup: () => ({addTo() { return this; }, clearLayers() { layers.lines = []; }}),
    heatLayer: points => { layers.points = points; return {addTo() { return this; }}; },
    polyline: points => ({bindPopup() { return this; }, addTo() { layers.lines.push(points); }})
  };
  const window = new Element(); window.L = L; window.matchMedia = () => ({matches:false});
  const context = vm.createContext({document, window, location, history, URL, URLSearchParams, L,
    Option: class extends Element { constructor(text, value) { super('option'); this.textContent = text; this.value = value; } },
    CustomEvent: class { constructor(type, options) { this.type = type; this.detail = options.detail; } },
    fetch: async () => ({ok: !failFetch, json: async () => flights ?? JSON.parse(readFileSync(path.join(site, 'data/flights.json'), 'utf8'))})
  });
  for (const file of page === 'index' ? ['calendar.js', 'map.js'] : ['map.js']) vm.runInContext(readFileSync(path.join(site, file), 'utf8'), context, {filename:file});
  await new Promise(resolve => setImmediate(resolve));
  return {nodes, layers, location,
    fire: (id, type, extra = {}) => nodes[id].dispatchEvent({type, ...extra}),
    day: date => document.dispatchEvent({type:'sighting-date-selected', detail:{date}})
  };
}

const sample = (date, tail, candidates) => ({date, tail, candidates, track:[[37.7,-122.4],[37.8,-122.4]]});
const flights = [sample('2026-10-05', 'N1', ['Apify']), sample('2026-10-05', 'N2', ['Monaco']), sample('2026-10-06', 'N1', ['Apify'])];
const status = app => app.nodes['map-status'].textContent;

test('archive cards survive month/view changes and date lookup retains source order', async () => {
  const original = JSON.parse(readFileSync(path.join(site, 'index.html'), 'utf8').match(/id="sighting-data">([^<]+)<\/script>/)[1]);
  const entries = original.entries.filter(entry => entry.date).slice(0,2).map(entry => ({...entry, date:'2026-10-05'}));
  const app = await controls({entries:[...entries, original.entries.find(entry => !entry.date)], flights});
  const undatedCards = [...app.nodes['undated-results'].children];
  app.nodes.undated.open = true;
  const cards = [...app.nodes.results.children];
  app.nodes.month.value = '2026-09'; app.fire('month', 'change');
  app.fire('list-view', 'click'); app.fire('calendar-view', 'click');
  assert.deepEqual(app.nodes.results.children, cards);
  assert.equal(app.nodes.results.children[0], cards[0]);
  assert.equal(app.nodes['undated-results'].children[0], undatedCards[0]);
  assert.equal(app.nodes.undated.open, true);
  app.nodes.month.value = '2026-10'; app.fire('month', 'change');
  app.day('2026-10-05');
  const day = app.nodes.grid.children.find(node => node.dataset.date === '2026-10-05');
  assert.deepEqual(day.children.filter(node => node.className === 'day-entry').map(node => node.title), entries.map(entry => original.brands[entry.brand].label));
  assert.equal(day.querySelector('.day-select').attrs['aria-pressed'], 'true');
  assert.equal(app.nodes['selected-day-results'].children.length, 2);
  assert.equal(app.location.searchParams.get('date'), '2026-10-05');
  app.fire('reset-map-day', 'click');
  assert.equal(app.location.searchParams.has('date'), false);
  assert.equal(app.nodes['selected-day'].hidden, true);
});

test('empty archive retains list guidance, calendar placeholder and hidden undated section', async () => {
  const app = await controls({entries:[], flights:[]});
  assert.equal(app.nodes.grid.children[0].textContent, 'No dated sightings yet.');
  app.fire('list-view', 'click');
  assert.equal(app.nodes.results.children[0].children[0].textContent, 'No dated sightings yet.');
  assert.equal(app.nodes.undated.hidden, true);
  assert.match(app.nodes['result-count'].textContent, /^0 dated sightings/);
});

test('full map composes filters, preserves unrelated URL state, validates range and resets', async () => {
  const app = await controls({page:'map', query:'?date=2026-10-05&brand=Apify&ref=keep#anchor', flights});
  assert.equal(status(app), '1 candidate track across 1 date.');
  assert.equal(app.nodes.tracks.checked, true);
  assert.equal(app.layers.lines.length, 1);
  app.nodes['map-brand'].value = ''; app.fire('map-brand', 'change');
  assert.equal(status(app), '2 candidate tracks across 1 date.');
  app.nodes.tail.value = 'N2'; app.fire('map-filters', 'change', {target:app.nodes.tail});
  assert.equal(status(app), '1 candidate track across 1 date.');
  app.nodes.from.value = '2026-10-06'; app.fire('map-filters', 'change', {target:app.nodes.from});
  assert.equal(status(app), 'Choose an end date on or after the start date.');
  assert.equal(app.layers.points.length, 0);
  app.fire('map-filters', 'reset');
  assert.equal(status(app), '3 candidate tracks across 2 dates.');
  assert.equal(app.nodes.tracks.checked, false);
  assert.equal(app.location.search, '?ref=keep'); assert.equal(app.location.hash, '#anchor');
  app.nodes.from.value = '2027-01-01'; app.nodes.to.value = ''; app.fire('map-filters', 'change', {target:app.nodes.from});
  assert.equal(status(app), 'No tracks match these filters. Try a wider date range.');
});

test('embedded map composes day/brand, empty-day messages and reset without full-map controls', async () => {
  const app = await controls({flights});
  app.nodes['map-brand'].value = 'Apify'; app.fire('map-brand', 'change');
  app.day('2026-10-05');
  assert.equal(status(app), '1 candidate track across 1 date.');
  assert.equal(app.layers.points.length, 0); assert.equal(app.layers.lines.length, 1);
  assert.equal(app.nodes['full-map-link'].href, '/map?date=2026-10-05&brand=Apify');
  app.day('2026-10-07'); assert.match(status(app), /^No tracks for this brand/);
  app.nodes['map-brand'].value = ''; app.fire('map-brand', 'change');
  assert.match(status(app), /^No recorded tracks for this date/);
  app.fire('reset-map-day', 'click');
  assert.equal(status(app), '3 candidate tracks across 2 dates.');
});

test('malformed URL date and unknown brand fall back; download failure retains retry', async () => {
  const app = await controls({page:'map', query:'?date=invalid&brand=missing', flights});
  assert.equal(status(app), '3 candidate tracks across 2 dates.');
  assert.equal(app.nodes.from.value, '2026-10-05'); assert.equal(app.nodes.to.value, '2026-10-06');
  const failed = await controls({page:'map', failFetch:true});
  assert.match(status(failed), /^The map could not load/);
  assert.equal(failed.nodes['retry-map'].hidden, false);
});
