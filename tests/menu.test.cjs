const test = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const { runInNewContext } = require('node:vm');

const source = readFileSync(join(__dirname, '../assets/site.js'), 'utf8');

function eventTarget() {
  const listeners = new Map();
  return {
    addEventListener(type, callback) { listeners.set(type, callback); },
    emit(type, values = {}) {
      const event = { button: 0, defaultPrevented: false, ...values,
        preventDefault() { this.defaultPrevented = true; } };
      listeners.get(type)?.(event);
      return event;
    },
  };
}

function setup() {
  const document = { ...eventTarget(), activeElement: null };
  function element(initial = {}) {
    const attrs = new Map(Object.entries(initial));
    return {
      ...eventTarget(),
      getAttribute: name => attrs.get(name),
      setAttribute: (name, value) => attrs.set(name, value),
      removeAttribute: name => attrs.delete(name),
      focus(options) {
        this.focusOptions = options;
        document.activeElement = this;
        document.emit('focusin', { target: this });
      },
    };
  }
  const sections = [element(), element()];
  const links = ['about', 'publications'].map(id => Object.assign(element({ href: `#${id}` }), { hash: `#${id}` }));
  const toggle = Object.assign(element({ 'aria-expanded': 'false', 'aria-label': 'Open navigation' }), { hidden: true });
  const navigation = { contains: node => links.includes(node) };
  const classes = new Set();
  const header = { ...eventTarget(), offsetHeight: 76, classList: { add: name => classes.add(name) },
    contains: node => node === toggle || node === navigation || links.includes(node) };
  const compact = { ...eventTarget(), matches: true };
  const outside = element();
  const selectors = new Map([
    ['.site-header', header], ['.menu-toggle', toggle], ['.section-nav', navigation],
    ...links.map((link, index) => [link.hash, sections[index]]),
  ]);
  document.querySelector = selector => selectors.get(selector);
  document.querySelectorAll = () => links;
  runInNewContext(source, { document, window: { matchMedia: () => compact } });
  return { document, sections, links, toggle, navigation, header, classes, compact, outside,
    open: () => toggle.emit('click'),
    expanded: () => toggle.getAttribute('aria-expanded'),
  };
}

test('enhancement enables the toggle, which updates its expanded state and label', () => {
  const page = setup();
  assert.equal(page.toggle.hidden, false);
  assert.ok(page.classes.has('menu-enabled'));
  assert.equal(page.expanded(), 'false');
  page.open();
  assert.equal(page.expanded(), 'true');
  assert.equal(page.toggle.getAttribute('aria-label'), 'Close navigation');
  page.toggle.emit('click');
  assert.equal(page.expanded(), 'false');
  assert.equal(page.toggle.getAttribute('aria-label'), 'Open navigation');
});

test('Escape closes the disclosure and restores focus to its toggle', () => {
  const page = setup();
  page.open();
  page.links[0].focus();
  page.header.emit('keydown', { key: 'Escape' });
  assert.equal(page.expanded(), 'false');
  assert.equal(page.document.activeElement, page.toggle);
});

test('ordinary navigation closes and focuses the destination without cancelling its anchor', () => {
  const page = setup();
  page.open();
  const event = page.links[1].emit('click');
  assert.equal(event.defaultPrevented, false);
  assert.equal(page.links[1].getAttribute('href'), '#publications');
  assert.equal(page.expanded(), 'false');
  assert.equal(page.document.activeElement, page.sections[1]);
  assert.equal(page.sections[1].getAttribute('tabindex'), '-1');
  assert.equal(page.sections[1].focusOptions.preventScroll, true);
});

test('modified or non-primary clicks preserve native link behavior and the open menu', () => {
  for (const input of [{ metaKey: true }, { ctrlKey: true }, { shiftKey: true }, { altKey: true }, { button: 1 }]) {
    const page = setup();
    page.open();
    const event = page.links[0].emit('click', input);
    assert.equal(event.defaultPrevented, false);
    assert.equal(page.expanded(), 'true');
    assert.equal(page.document.activeElement, null);
  }
});

test('outside pointer dismissal prevents focus from remaining in the closed disclosure', () => {
  const page = setup();
  page.open();
  page.links[0].focus();
  page.document.emit('pointerdown', { target: page.links[0] });
  assert.equal(page.expanded(), 'true');
  page.document.emit('pointerdown', { target: page.outside });
  assert.equal(page.expanded(), 'false');
  assert.equal(page.document.activeElement, page.toggle);
});

test('tabbing outside dismisses the disclosure without stealing focus', () => {
  const page = setup();
  page.open();
  page.outside.focus();
  assert.equal(page.expanded(), 'false');
  assert.equal(page.document.activeElement, page.outside);
});

test('breakpoint changes close the menu and move focus out of controls that become hidden', () => {
  const page = setup();
  page.open();
  page.toggle.focus();
  page.compact.matches = false;
  page.compact.emit('change');
  assert.equal(page.expanded(), 'false');
  assert.equal(page.document.activeElement, page.links[0]);
  page.compact.matches = true;
  page.compact.emit('change');
  assert.equal(page.document.activeElement, page.toggle);
});
