const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {test} = require('node:test');
const vm = require('node:vm');
const path = require('node:path');
const script = readFileSync(path.join(__dirname, '../site/outbound.js'), 'utf8');
const fixtures = JSON.parse(readFileSync(path.join(__dirname, 'outbound_urls.json'), 'utf8'));

class Element {
  constructor(tag, attrs = {}, children = []) { this.tag = tag; this.attrs = {...attrs}; this.children = children; this.nodeType = 1; this.writes = 0; }
  hasAttribute(key) { return Object.hasOwn(this.attrs, key); }
  getAttribute(key) { return this.attrs[key] ?? null; }
  setAttribute(key, value) { this.attrs[key] = value; this.writes++; }
  matches() { return this.tag === 'a' && this.hasAttribute('href'); }
  querySelectorAll() { return this.children.flatMap(node => [...(node.matches() ? [node] : []), ...node.querySelectorAll()]); }
  closest() { return this.matches() ? this : this.parent?.closest(); }
}
const anchor = (href, attrs = {}) => new Element('a', {href, ...attrs});
function runtime(children = [], hostname = 'whosflyingoversf.com') {
  const root = new Element('html', {}, children), events = {};
  let notify, observed;
  const document = {documentElement: root, addEventListener: (type, callback, capture) => { events[type] = callback; assert.equal(capture, true); }};
  const MutationObserver = class {
    constructor(callback) { notify = callback; }
    observe(target, options) { observed = {target, options}; }
  };
  vm.runInNewContext(script, {document, MutationObserver, URL, location: new URL(`https://${hostname}/`)});
  assert.equal(observed.target, root);
  assert.equal(observed.options.subtree, true);
  assert.equal(observed.options.attributeFilter.join(','), 'href');
  return {notify, events};
}

test('shared URL cases and repeat scans preserve existing tracking exactly', () => {
  const anchors = fixtures.map(([raw]) => anchor(raw));
  const {notify} = runtime(anchors);
  anchors.forEach((node, i) => assert.equal(node.getAttribute('href'), fixtures[i][1] ?? fixtures[i][0]));
  const writes = anchors.map(node => node.writes);
  notify(anchors.map(target => ({type: 'attributes', target})));
  anchors.forEach((node, i) => assert.equal(node.writes, writes[i]));
});

test('dynamic anchors, nested popups and changed hrefs receive attribution', () => {
  const {notify} = runtime();
  const direct = anchor('https://example.org/direct#proof');
  const nested = anchor('https://github.com/org/repo/issues/new?template=sighting.yml');
  notify([{type: 'childList', addedNodes: [direct, new Element('div', {}, [nested]), {nodeType: 3}]}]);
  assert.equal(direct.getAttribute('href'), 'https://example.org/direct?utm_source=whosflyingoversf.com#proof');
  assert.equal(nested.getAttribute('href'), 'https://github.com/org/repo/issues/new?template=sighting.yml&utm_source=whosflyingoversf.com');
  direct.setAttribute('href', 'https://example.org/changed');
  notify([{type: 'attributes', target: direct}]);
  assert.equal(direct.getAttribute('href'), 'https://example.org/changed?utm_source=whosflyingoversf.com');
});

test('download, explicit opt-out, assets and current preview host stay untouched', () => {
  const nodes = [anchor('https://example.org/export', {download: ''}), anchor('https://example.org/opaque', {'data-no-referral': ''}), anchor('https://preview.example.test/map'), new Element('link', {href: 'https://cdn.test/style'}), new Element('img', {src: 'https://cdn.test/image'})];
  runtime(nodes, 'preview.example.test');
  nodes.forEach(node => assert.equal(node.writes, 0));
});

test('activation before mutation delivery covers clicks, middle clicks and context menus', () => {
  const {events} = runtime();
  for (const type of ['click', 'auxclick', 'contextmenu']) {
    const node = anchor('https://example.org/instant');
    const child = new Element('span'); child.parent = node;
    events[type]({target: child});
    assert.equal(node.getAttribute('href'), 'https://example.org/instant?utm_source=whosflyingoversf.com');
  }
});
