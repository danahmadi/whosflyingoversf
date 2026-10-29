const assert = require('node:assert/strict');
const {readFileSync, readdirSync} = require('node:fs');
const {test} = require('node:test');
const vm = require('node:vm');
const path = require('node:path');
const site = path.join(__dirname, '../site');
const script = readFileSync(path.join(site, 'analytics.js'), 'utf8');

function runtime({url = 'https://whosflyingoversf.com/fly', navigator = {}, referrer = '', window = {}} = {}) {
  const tags = [];
  const context = vm.createContext({URL, location: new URL(url), navigator, window,
    document: {referrer, createElement: () => ({}), head: {appendChild: tag => tags.push(tag)}}});
  const run = () => vm.runInContext(script, context);
  run();
  return {window, tags, run, commands: () => (window.dataLayer || []).map(args => Array.from(args))};
}

test('production loads once and queues one page view with advertising disabled', () => {
  const app = runtime();
  app.run();
  assert.equal(app.tags.length, 1);
  assert.equal(app.tags[0].src, 'https://www.googletagmanager.com/gtag/js?id=G-B3NX9EE5BM');
  assert.equal(app.tags[0].async, true);
  const commands = app.commands();
  assert.equal(commands.filter(command => command[0] === 'config').length, 1);
  assert.equal(commands.find(command => command[0] === 'config')[1], 'G-B3NX9EE5BM');
  assert.equal(commands[0][1].allow_google_signals, false);
  assert.equal(commands[0][1].allow_ad_personalization_signals, false);
  assert.equal(commands[1][2].ad_storage, 'denied');
  assert.equal(commands[1][2].ad_user_data, 'denied');
  assert.equal(commands[1][2].ad_personalization, 'denied');
});

test('preview, localhost and HTTP never initialize Google Analytics', () => {
  for (const url of ['https://preview.vercel.app/fly', 'http://localhost:8000/', 'http://whosflyingoversf.com/', 'https://whosflyingoversf.com.example.org/']) {
    const app = runtime({url});
    assert.equal(app.tags.length, 0);
    assert.equal(app.window.dataLayer, undefined);
  }
});

test('browser privacy signals prevent loading and event initialization', () => {
  for (const navigator of [{globalPrivacyControl: true}, {doNotTrack: '1'}, {doNotTrack: 'yes'}, {msDoNotTrack: '1'}]) {
    const app = runtime({navigator});
    assert.equal(app.tags.length, 0);
    assert.equal(app.window.dataLayer, undefined);
  }
  assert.equal(runtime({window: {doNotTrack: '1'}}).tags.length, 0);
});

test('only campaign parameters survive and referrer is reduced to origin', () => {
  const app = runtime({url: 'https://whosflyingoversf.com/map?email=private%40example.org&utm_source=newsletter&filter=one&filter=two&utm_campaign=launch#private',
    referrer: 'https://example.org/private/path?email=private%40example.org#secret'});
  const settings = app.commands()[0][1];
  assert.equal(settings.page_location, 'https://whosflyingoversf.com/map?utm_source=newsletter&utm_campaign=launch');
  assert.equal(settings.page_referrer, 'https://example.org/');
  assert.equal(runtime({referrer: 'not a URL'}).commands()[0][1].page_referrer, '');
});

test('every generated page includes the shared loader exactly once', () => {
  for (const file of readdirSync(site).filter(file => file.endsWith('.html'))) {
    const html = readFileSync(path.join(site, file), 'utf8');
    assert.equal(html.split('<script defer src="/analytics.js"></script>').length - 1, 1, file);
  }
});
