// AutoLedger BD progressive enhancements. Works without external JavaScript libraries.
// Form values remain native HTML inputs and save through Django / CSRF protected POST.
document.addEventListener('DOMContentLoaded', () => {
  const select = document.querySelector('[data-field="fuel_type"] select');
  if (select) {
    const group = document.createElement('div');
    group.className = 'fuel-pill-options';
    group.setAttribute('role', 'group');
    group.setAttribute('aria-label', 'Choose fuel type');
    for (const option of Array.from(select.options).filter(o => o.value)) {
      const button = document.createElement('button');
      button.type = 'button';
      button.textContent = option.text.split('/')[0].trim();
      button.dataset.value = option.value;
      button.setAttribute('aria-pressed', String(select.value === option.value));
      button.addEventListener('click', () => {
        select.value = option.value;
        select.dispatchEvent(new Event('change', {bubbles:true}));
      });
      group.appendChild(button);
    }
    select.after(group);
    // Keep the native select for keyboard access and devices without JS.
    const update = () => group.querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', String(select.value === b.dataset.value)));
    select.addEventListener('change', update);
    update();
  }
  for (const input of document.querySelectorAll('input[type="file"]')) {
    const preview = document.createElement('img');
    preview.className = 'photo-preview';
    preview.alt = 'Selected image preview';
    input.after(preview);
    let lastURL = null;
    input.addEventListener('change', () => {
      if (lastURL) URL.revokeObjectURL(lastURL);
      const file = input.files?.[0];
      if (file && file.type.startsWith('image/')) {
        lastURL = URL.createObjectURL(file);
        preview.src = lastURL;
        preview.classList.add('has-image');
      } else {
        preview.removeAttribute('src');
        preview.classList.remove('has-image');
      }
    });
  }
});
