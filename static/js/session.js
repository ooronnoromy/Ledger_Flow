// Keep active forms signed in, then sign out after the configured idle interval.
(() => {
  const config = document.body.dataset;
  const timeout = Number(config.sessionTimeout) * 1000;
  if (!timeout || !config.sessionActivity) return;
  const csrf = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
  const channel = 'BroadcastChannel' in window ? new BroadcastChannel('autoledger-session') : null;
  let timer, changed = false, lastBroadcast = 0, signingOut = false;
  const login = () => location.replace(config.sessionLogin);
  const signOut = () => {
    if (signingOut) return;
    signingOut = true;
    channel?.postMessage('logout');
    fetch(config.sessionLogout, {method:'POST',credentials:'same-origin',headers:{'X-CSRFToken':csrf || ''}}).finally(login);
  };
  const reset = (local = true) => {
    clearTimeout(timer); timer = setTimeout(signOut, timeout);
    if (local) {
      changed = true;
      if (Date.now() - lastBroadcast > 1000) { channel?.postMessage('activity'); lastBroadcast = Date.now(); }
    }
  };
  channel?.addEventListener('message', event => {
    if (event.data === 'logout') login();
    else if (event.data === 'activity') reset(false);
  });
  ['pointerdown','keydown','wheel','touchstart'].forEach(name => document.addEventListener(name, () => reset(), {passive:true}));
  setInterval(async () => {
    if (!changed || signingOut) return;
    changed = false;
    try {
      const response = await fetch(config.sessionActivity, {method:'POST',credentials:'same-origin',headers:{'X-CSRFToken':csrf || ''}});
      if (response.redirected || response.status === 401 || response.status === 403) login();
    } catch { /* The server still enforces expiry when connectivity returns. */ }
  }, 30000);
  window.addEventListener('pageshow', event => { if (event.persisted) location.reload(); });
  reset(false);
})();
