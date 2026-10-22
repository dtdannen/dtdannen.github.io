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
