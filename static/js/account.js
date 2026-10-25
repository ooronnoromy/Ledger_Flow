(() => {
  const menu = document.querySelector('[data-account-menu]');
  if (!menu) return;
  const trigger = menu.querySelector('.account-trigger');
  const panel = menu.querySelector('.account-panel');
  const setOpen = open => { panel.hidden = !open; trigger.setAttribute('aria-expanded', String(open)); };
  trigger.addEventListener('click', () => setOpen(panel.hidden));
  trigger.addEventListener('keydown', event => {
    if (event.key === 'ArrowDown') { event.preventDefault(); setOpen(true); panel.querySelector('a').focus(); }
  });
  document.addEventListener('click', event => { if (!menu.contains(event.target)) setOpen(false); });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && !panel.hidden) { setOpen(false); trigger.focus(); }
  });
  menu.addEventListener('focusout', event => { if (!menu.contains(event.relatedTarget)) setOpen(false); });
})();
