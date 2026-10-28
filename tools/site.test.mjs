import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { readFile } from 'node:fs/promises';
import test from 'node:test';
import { runInNewContext } from 'node:vm';

const source = await readFile(new URL('../assets/js/site.js', import.meta.url), 'utf8');
const pages = ['index.html', '404.html', 'beta/index.html', 'privacy/index.html', 'support/index.html', 'terms/index.html', 'bigtable/index.html', 'suffice/index.html', 'sated/index.html', 'caloma/index.html', 'hearken/index.html', 'trove/index.html'];

function setup({ theme = 'light', saved = null, systemDark = false, reduce = false, storageBlocked = false, viewTransitions = false } = {}) {
  const root = new Map(theme ? [['data-theme', theme]] : []);
  const button = new Map();
  const meta = [new Map(), new Map()];
  const events = {};
  const storage = new Map(saved ? [['hearth-theme', saved]] : []);
  const animations = [];
  let transitionCount = 0;
  let onSystemChange;
  const mq = {
    matches: systemDark,
    addEventListener(type, handler) {
      assert.equal(type, 'change');
      onSystemChange = handler;
    },
  };
  const doc = {
    getAttribute: (name) => root.get(name),
    setAttribute: (name, value) => root.set(name, value),
    animate: (keyframes, options) => { animations.push({ keyframes, options }); },
  };
  runInNewContext(source, {
    document: {
      documentElement: doc,
      startViewTransition: viewTransitions ? (update) => {
        transitionCount++;
        update();
        return { ready: Promise.resolve() };
      } : undefined,
      querySelector: (selector) => selector === '.theme-btn' ? {
        setAttribute: (name, value) => button.set(name, value),
        addEventListener: (type, handler) => { events[type] = handler; },
        getBoundingClientRect: () => ({ left: 100, top: 10, width: 60, height: 44 }),
      } : null,
      querySelectorAll: (selector) => selector === 'meta[name="theme-color"]'
        ? meta.map((attributes) => ({ setAttribute: (name, value) => attributes.set(name, value) })) : [],
    },
    window: {
      matchMedia: (query) => query.includes('reduced-motion') ? { matches: reduce } : mq,
      innerWidth: 1200,
      innerHeight: 800,
    },
    localStorage: {
      getItem(name) {
        if (storageBlocked) throw new Error('Storage blocked');
        return storage.get(name) || null;
      },
      setItem(name, value) {
        if (storageBlocked) throw new Error('Storage blocked');
        storage.set(name, value);
      },
    },
  });
  return {
    click: () => events.click(),
    systemChange: (matches) => onSystemChange({ matches }),
    root, button, meta, storage,
    animations,
    transitionCount: () => transitionCount,
  };
}

function assertAppearance(state, theme) {
  assert.equal(state.root.get('data-theme'), theme);
  assert.equal(state.button.get('aria-checked'), String(theme === 'dark'));
  for (const meta of state.meta) {
    assert.equal(meta.get('content'), theme === 'dark' ? '#000000' : '#FBFBFD');
  }
}

test('initial appearance synchronizes the switch and browser theme color', () => {
  for (const theme of ['light', 'dark']) assertAppearance(setup({ theme }), theme);
  assertAppearance(setup({ theme: null, systemDark: true }), 'dark');
});

test('without View Transition support, rapid clicks apply immediately and persist the final choice', () => {
  const state = setup();
  for (let i = 0; i < 21; i++) {
    state.click();
    const theme = i % 2 === 0 ? 'dark' : 'light';
    assertAppearance(state, theme);
    assert.equal(state.storage.get('hearth-theme'), theme);
  }
});

test('full-page circular reveal preserves the original origin, coverage, duration and easing', async () => {
  const state = setup({ viewTransitions: true });
  for (const theme of ['dark', 'light']) {
    state.click();
    await Promise.resolve();
    assertAppearance(state, theme);
    assert.equal(state.storage.get('hearth-theme'), theme);
    const { keyframes, options } = state.animations.at(-1);
    assert.deepEqual(Array.from(keyframes.clipPath), [
      'circle(0px at 130px 32px)',
      `circle(${Math.hypot(1070, 768)}px at 130px 32px)`,
    ]);
    assert.equal(options.duration, 650);
    assert.equal(options.easing, 'cubic-bezier(.2, .8, .2, 1)');
    assert.equal(options.pseudoElement, '::view-transition-new(root)');
  }
  assert.equal(state.transitionCount(), 2);
  assert.equal(state.animations.length, 2);
  const css = await readFile(new URL('../assets/css/site.css', import.meta.url), 'utf8');
  assert.match(css, /::view-transition-old\(root\), ::view-transition-new\(root\) \{ animation: none; mix-blend-mode: normal; \}/);
});

test('system changes apply only until an explicit preference is saved', () => {
  const state = setup();
  state.systemChange(true);
  assertAppearance(state, 'dark');
  state.systemChange(false);
  assertAppearance(state, 'light');
  state.click();
  state.systemChange(false);
  assertAppearance(state, 'dark');
  const saved = setup({ theme: 'light', saved: 'light' });
  saved.systemChange(true);
  assertAppearance(saved, 'light');
});

test('switch works with reduced motion or unavailable storage', () => {
  for (const options of [{ reduce: true, viewTransitions: true }, { storageBlocked: true }]) {
    const state = setup(options);
    state.click();
    assertAppearance(state, 'dark');
    state.click();
    assertAppearance(state, 'light');
    assert.equal(state.transitionCount(), 0);
    assert.equal(state.animations.length, 0);
  }
});

test('every non-brand SVG is an accessible static Lucide icon on every page', async () => {
  let count = 0;
  for (const page of pages) {
    const html = await readFile(new URL(`../${page}`, import.meta.url), 'utf8');
    for (const [svg] of html.matchAll(/<svg\b[^>]*>[\s\S]*?<\/svg>/g)) {
      if (/class="mark(?:\s|")/.test(svg)) continue;
      assert.match(svg, /data-lucide="[A-Z][A-Za-z0-9]*"/, page);
      assert.match(svg, /class="lucide /, page);
      assert.match(svg, /aria-hidden="true"/, page);
      assert.match(svg, /focusable="false"/, page);
      assert.match(svg, /\swidth="(?:12|20|24|28|30)"/, page);
      assert.match(svg, /\sheight="(?:12|20|24|28|30)"/, page);
      count++;
    }
    assert.equal((html.match(/data-lucide="Sun"/g) || []).length, 2, page);
    assert.equal((html.match(/data-lucide="Moon"/g) || []).length, 2, page);
    assert.equal((html.match(/data-lucide="Menu"/g) || []).length, 1, page);
    assert.equal((html.match(/data-lucide="X"/g) || []).length, 1, page);
  }
  assert.equal(count, 247);
  execFileSync(process.execPath, [new URL('./render-icons.mjs', import.meta.url).pathname, '--check']);
});
