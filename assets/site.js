// A native anchor remains functional when JavaScript is unavailable.
const links = [...document.querySelectorAll('.section-nav a')];
const sections = links.map(link => document.querySelector(link.getAttribute('href'))).filter(Boolean);
const header = document.querySelector('.site-header');
let headerHeight = header?.offsetHeight || 0;
let observer;
const visible = new Set();

function observeSections() {
  observer?.disconnect();
  visible.clear();
  observer = new IntersectionObserver(entries => {
    for (const entry of entries) {
      if (entry.isIntersecting) visible.add(entry.target);
      else visible.delete(entry.target);
    }
    const current = sections.find(section => visible.has(section));
    for (const link of links) {
      if (current && link.hash === `#${current.id}`) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    }
  // Exclude the sticky header and the 16px anchor gap, including its edge.
  }, { rootMargin: `-${headerHeight + 17}px 0px 0px 0px` });
  sections.forEach(section => observer.observe(section));
}
if ('IntersectionObserver' in window) observeSections();

// Wrapped navigation must not cover anchor headings when text is enlarged.
if (header && 'ResizeObserver' in window) {
  new ResizeObserver(() => {
    const height = header.offsetHeight;
    document.documentElement.style.setProperty('--header-height', `${height}px`);
    if (height !== headerHeight) {
      headerHeight = height;
      if ('IntersectionObserver' in window) observeSections();
    }
  }).observe(header);
}

const toggle = document.querySelector('.menu-toggle');
const navigation = document.querySelector('.section-nav');
if (header && toggle && navigation) {
  const compact = window.matchMedia('(max-width: 60rem)');
  const isOpen = () => toggle.getAttribute('aria-expanded') === 'true';
  const setOpen = open => {
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
  };

  toggle.addEventListener('click', () => setOpen(!isOpen()));
  header.addEventListener('keydown', event => {
    if (event.key === 'Escape' && isOpen()) {
      setOpen(false);
      toggle.focus();
    }
  });
  for (const link of links) {
    link.addEventListener('click', event => {
      if (!compact.matches || !isOpen() || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      setOpen(false);
      const target = document.querySelector(link.hash);
      target?.setAttribute('tabindex', '-1');
      target?.focus({ preventScroll: true });
    });
  }
  document.addEventListener('pointerdown', event => {
    if (isOpen() && !header.contains(event.target)) {
      setOpen(false);
      if (navigation.contains(document.activeElement)) toggle.focus();
    }
  });
  document.addEventListener('focusin', event => {
    if (isOpen() && !header.contains(event.target)) setOpen(false);
  });
  compact.addEventListener('change', () => {
    setOpen(false);
    if (!compact.matches && document.activeElement === toggle) links[0]?.focus();
    else if (compact.matches && navigation.contains(document.activeElement)) toggle.focus();
  });

  // Progressive enhancement: without JavaScript, every navigation link stays visible.
  toggle.hidden = false;
  header.classList.add('menu-enabled');
}
