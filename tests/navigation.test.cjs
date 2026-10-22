const test = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const { runInNewContext } = require('node:vm');

const source = readFileSync(join(__dirname, '../assets/site.js'), 'utf8');

function setup({ observers = true } = {}) {
  const sections = [{ id: 'about' }, { id: 'publications' }];
  const links = sections.map(({ id }) => {
    const attributes = new Map([['href', `#${id}`]]);
    return {
      hash: `#${id}`,
      getAttribute: name => attributes.get(name),
      setAttribute: (name, value) => attributes.set(name, value),
      removeAttribute: name => attributes.delete(name),
    };
  });
  const header = { offsetHeight: 64 };
  const properties = new Map();
  const observed = { sections: [], headers: [], observers: [] };
  let intersectionCallback;
  let resizeCallback;
  class IntersectionObserver {
    constructor(callback, options) {
      intersectionCallback = callback;
      this.options = options;
      this.disconnected = false;
      observed.observers.push(this);
    }
    observe(section) { observed.sections.push(section); }
    disconnect() { this.disconnected = true; }
  }
  class ResizeObserver {
    constructor(callback) { resizeCallback = callback; }
    observe(element) { observed.headers.push(element); }
  }
  const available = observers ? { IntersectionObserver, ResizeObserver } : {};
  runInNewContext(source, {
    ...available,
    window: available,
    document: {
      querySelectorAll: () => links,
      querySelector: selector => selector === '.site-header'
        ? header
        : sections.find(section => selector === `#${section.id}`),
      documentElement: { style: { setProperty: (name, value) => properties.set(name, value) } },
    },
  });
  return { links, sections, header, properties, observed,
    intersect: entries => intersectionCallback(entries),
    resize: () => resizeCallback(),
  };
}

const entry = (target, isIntersecting) => ({ target, isIntersecting });
const current = links => links.map(link => link.getAttribute('aria-current'));

test('incremental observer entries retain another section that is still visible', () => {
  const page = setup();
  const [about, publications] = page.sections;
  assert.deepEqual(page.observed.sections, page.sections);
  page.intersect([entry(about, true), entry(publications, true)]);
  assert.deepEqual(current(page.links), ['location', undefined]);
  page.intersect([entry(about, false)]);
  assert.deepEqual(current(page.links), [undefined, 'location']);
});

test('returning to the hero clears the active navigation link', () => {
  const page = setup();
  page.intersect([entry(page.sections[0], true)]);
  page.intersect([entry(page.sections[0], false)]);
  assert.deepEqual(current(page.links), [undefined, undefined]);
});

test('header resizing updates the anchor offset for wrapped navigation', () => {
  const page = setup();
  assert.deepEqual(page.observed.headers, [page.header]);
  const initial = page.observed.observers[0];
  assert.equal(initial.options.rootMargin, '-81px 0px 0px 0px');
  page.resize();
  assert.equal(page.properties.get('--header-height'), '64px');
  assert.equal(page.observed.observers.length, 1, 'unchanged height keeps the observer');
  page.intersect([entry(page.sections[0], true)]);
  page.header.offsetHeight = 118;
  page.resize();
  assert.equal(page.properties.get('--header-height'), '118px');
  assert.equal(page.observed.observers.length, 2);
  assert.equal(initial.disconnected, true);
  const latest = page.observed.observers.at(-1);
  assert.equal(latest.options.rootMargin, '-135px 0px 0px 0px');
  assert.equal(latest.disconnected, false);
  for (const observer of page.observed.observers) {
    assert.deepEqual(observer.options.rootMargin.split(' ').slice(1), ['0px', '0px', '0px']);
    assert.ok(!observer.options.rootMargin.includes('%'));
  }
  page.intersect([entry(page.sections[1], true)]);
  assert.deepEqual(current(page.links), [undefined, 'location'], 'recreation clears prior visible sections');
  page.resize();
  assert.equal(page.observed.observers.length, 2, 'same resized height does not recreate again');
});

test('native anchors remain intact when browser observers are unavailable', () => {
  let page;
  assert.doesNotThrow(() => { page = setup({ observers: false }); });
  assert.deepEqual(page.links.map(link => link.getAttribute('href')), ['#about', '#publications']);
  assert.deepEqual(current(page.links), [undefined, undefined]);
});
