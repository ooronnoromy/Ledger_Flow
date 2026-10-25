// Preview-only interactions. Live records continue to use Django's forms.
(() => {
  document.querySelector('[data-account-logout]')?.addEventListener('submit', event => {
    event.preventDefault();
    const notice = document.createElement('div');
    notice.className = 'preview-notice'; notice.setAttribute('role','status');
    notice.textContent = 'Design preview — sign out is available in the running app.';
    document.body.append(notice); setTimeout(() => notice.remove(), 4000);
    document.querySelector('.account-panel').hidden = true;
    document.querySelector('.account-trigger').setAttribute('aria-expanded', 'false');
  });
  const dialog = document.createElement('dialog');
  dialog.className = 'preview-dialog';
  dialog.innerHTML = `<form id="demo-expense"><h2>খরচ যোগ করুন</h2><p>Design preview · Sample records are kept for this session.</p><label>গাড়ি<select name="vehicle"><option>Toyota Axio</option><option>Toyota Corolla</option><option>Toyota Hiace</option></select></label><label>বিবরণ<input name="description" required placeholder="e.g. Octane (Fuel Refill)" maxlength="80"></label><label>মোট খরচ (৳)<input name="amount" type="number" min="1" step="0.01" required placeholder="3,000"></label><label>পাম্প / লোকেশন<input name="location" placeholder="Dhaka" maxlength="80"></label><div class="dialog-actions"><button class="btn btn-secondary" type="button" data-close>Cancel</button><button class="btn btn-primary" type="submit">সংরক্ষণ করুন</button></div></form>`;
  document.body.append(dialog);
  document.querySelectorAll('[data-preview-add]').forEach(button => button.addEventListener('click', () => dialog.showModal()));
  dialog.querySelector('[data-close]').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => { if(event.target === dialog) { const r=dialog.getBoundingClientRect(); if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom) dialog.close(); }});
  dialog.querySelector('form').addEventListener('submit', event => {
    event.preventDefault();
    const form = event.currentTarget, data = new FormData(form), amount = Number(data.get('amount'));
    const row = document.createElement('a'); row.className = 'transaction';
    row.innerHTML = '<div class="transaction-symbol symbol-fuel">৳</div><div class="transaction-label"><b></b><small></small></div><div class="transaction-cost"><b></b><small>Just now</small></div>';
    row.querySelector('.transaction-label b').textContent = data.get('description');
    row.querySelector('.transaction-label small').textContent = data.get('location') || data.get('vehicle');
    row.querySelector('.transaction-cost b').textContent = '৳ '+amount.toLocaleString('en-US');
    document.querySelector('.transaction-list').prepend(row);
    const total = document.querySelector('.stat-red strong');
    total.textContent = '৳ '+(Number(total.textContent.replace(/[^0-9.]/g,''))+amount).toLocaleString('en-US');
    dialog.close(); form.reset();
    const notice = document.createElement('div'); notice.className='preview-notice';notice.setAttribute('role','status');notice.textContent='Expense added to this preview';document.body.append(notice);setTimeout(()=>notice.remove(),3500);
  });
  const search = document.querySelector('.global-search');
  search.addEventListener('submit', e => e.preventDefault());
  search.querySelector('input').addEventListener('input', event => {
    const query=event.target.value.trim().toLowerCase();
    document.querySelectorAll('.transaction').forEach(row => row.hidden = !row.textContent.toLowerCase().includes(query));
  });
})();
