/**
 * Toggles the mobile nav-links panel open/closed. Only visible/relevant
 * below the 640px breakpoint (see .mobile-nav-toggle in style.css) --
 * on desktop the button is hidden and .nav-links is always visible inline,
 * so this script simply has nothing to do there.
 */
document.addEventListener('DOMContentLoaded', function () {
  const toggle = document.getElementById('mobile-nav-toggle');
  const links = document.getElementById('nav-links');
  if (!toggle || !links) return;

  function closeMenu() {
    links.classList.remove('open');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.classList.remove('is-open');
  }

  function openMenu() {
    links.classList.add('open');
    toggle.setAttribute('aria-expanded', 'true');
    toggle.classList.add('is-open');
  }

  toggle.addEventListener('click', function (event) {
    event.stopPropagation();
    if (links.classList.contains('open')) {
      closeMenu();
    } else {
      openMenu();
    }
  });

  // Tapping a link closes the menu (otherwise it stays open after navigating back)
  links.addEventListener('click', function (event) {
    if (event.target.closest('.nav-link')) closeMenu();
  });

  // Tapping anywhere else on the page closes it too
  document.addEventListener('click', function (event) {
    if (links.classList.contains('open') && !links.contains(event.target) && event.target !== toggle) {
      closeMenu();
    }
  });

  // Resizing back to desktop width shouldn't leave a stale open panel
  window.addEventListener('resize', function () {
    if (window.innerWidth > 640) closeMenu();
  });
});