// Theme resolution: explicit theme → ancestor data-theme/.dark|.light class → prefers-color-scheme.

function ancestorTheme(el) {
  let node = el;
  while (node) {
    if (node.getAttribute) {
      const attr = node.getAttribute('data-theme');
      if (attr === 'dark') return true;
      if (attr === 'light') return false;
      if (node.classList.contains('dark')) return true;
      if (node.classList.contains('light')) return false;
    }
    node = node.parentElement;
  }
  return null;
}

function systemDark() {
  return typeof matchMedia !== 'undefined' && matchMedia('(prefers-color-scheme: dark)').matches;
}

export function isDarkTheme(el, theme = 'auto') {
  if (theme === 'dark') return true;
  if (theme === 'light') return false;
  const fromTree = ancestorTheme(el);
  if (fromTree !== null) return fromTree;
  return systemDark();
}

export function isReducedMotion() {
  return typeof matchMedia !== 'undefined' && matchMedia('(prefers-reduced-motion: reduce)').matches;
}
