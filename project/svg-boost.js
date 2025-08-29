// project/svg-boost.js
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('img[src$=".svg"]').forEach(img => {
    // Lazy + decode async si non déjà définis
    if (!img.hasAttribute('loading')) img.loading = 'lazy';
    if (!img.hasAttribute('decoding')) img.decoding = 'async';

    // Chemin absolu: "images/x.svg" → "/images/x.svg"
    const src = img.getAttribute('src');
    if (src && !src.startsWith('/')) {
      img.setAttribute('src', '/' + src.replace(/^\/+/, ''));
    }
  });
});
