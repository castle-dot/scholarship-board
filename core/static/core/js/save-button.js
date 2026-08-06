/**
 * Handles every "SAVE" button on the page via event delegation, so this
 * works for buttons rendered inside cards that get re-paginated, etc.
 * No <form>, no page reload -- just a fetch() call + a CSS class toggle
 * that triggers the pop/fill animation defined in style.css.
 */

function getCookie(name) {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? decodeURIComponent(match[2]) : null;
}

document.addEventListener('click', function (event) {
  const btn = event.target.closest('.js-save-btn');
  if (!btn) return;

  event.preventDefault();
  if (btn.classList.contains('is-loading')) return; // ignore double-clicks mid-request

  const url = btn.dataset.saveUrl;
  const csrftoken = getCookie('csrftoken');

  btn.classList.add('is-loading');

  fetch(url, {
    method: 'POST',
    headers: {
      'X-CSRFToken': csrftoken,
      'X-Requested-With': 'XMLHttpRequest',
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: '',
  })
    .then((response) => {
      if (!response.ok) throw new Error('Save request failed');
      return response.json();
    })
    .then((data) => {
      btn.classList.remove('is-loading');
      btn.classList.toggle('is-saved', data.is_saved);
      btn.setAttribute('aria-pressed', data.is_saved ? 'true' : 'false');
      btn.setAttribute('aria-label', data.is_saved ? 'Remove from saved' : 'Save this scholarship');

      const label = btn.querySelector('.stamp-label');
      if (label) label.textContent = data.is_saved ? 'SAVED' : 'SAVE';

      // retrigger the pop animation even on repeated clicks
      btn.classList.remove('stamp-pop');
      // reflow so the browser re-runs the animation next time the class is added
      void btn.offsetWidth;
      btn.classList.add('stamp-pop');

      // On the profile page's "itinerary" list, unsaving should remove the
      // whole row rather than leave a stray SAVE button sitting there.
      const row = btn.closest('.stub-row');
      if (row && !data.is_saved) {
        row.style.transition = 'opacity 0.25s ease, max-height 0.25s ease';
        row.style.maxHeight = row.offsetHeight + 'px';
        requestAnimationFrame(() => {
          row.style.opacity = '0';
          row.style.maxHeight = '0';
          row.style.overflow = 'hidden';
        });
        setTimeout(() => row.remove(), 260);
      }
    })
    .catch(() => {
      btn.classList.remove('is-loading');
      // Something went wrong (e.g. session expired) -- reload so the user
      // sees the real, current state rather than a button stuck mid-animation.
      window.location.reload();
    });
});