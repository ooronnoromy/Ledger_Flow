(() => {
  const panel=document.querySelector('[data-push-settings]');
  if(!panel)return;
  const enable=panel.querySelector('[data-push-enable]'),disable=panel.querySelector('[data-push-disable]'),status=panel.querySelector('[data-push-status]');
  const csrf=document.querySelector('[name=csrfmiddlewaretoken]')?.value;
  const message=text=>status.textContent=text;
  let key,registration;
  const supported=window.isSecureContext&&'serviceWorker'in navigator&&'PushManager'in window&&'Notification'in window;
  const post=async(url,data)=>{
    const response=await fetch(url,{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json','X-CSRFToken':csrf||''},body:JSON.stringify(data)});
    if(response.redirected){location.assign('/login/');throw Error('Please sign in again.')}
    const result=await response.json();if(!response.ok)throw Error(result.error||'Could not update notification settings.');return result;
  };
  const refresh=async()=>{
    const subscription=await registration.pushManager.getSubscription();
    enable.disabled=!!subscription||Notification.permission==='denied';disable.hidden=!subscription;
    message(subscription?'Expense notifications are enabled on this device.':Notification.permission==='denied'?'Notifications are blocked. Allow notifications in your browser settings, then reload.':'Get a phone alert when an expense is recorded.');
    return subscription;
  };
  if(!supported){message('Use the HTTPS app in a supported browser. On iPhone, first add it to your Home Screen.');return}
  fetch(panel.dataset.pushConfig,{credentials:'same-origin'}).then(async response=>{
    if(response.redirected)throw Error('Sign in again to manage notifications.');
    const config=await response.json();if(!config.ready)throw Error('Notification signing keys need to be configured on the server.');
    key=config.publicKey;registration=await navigator.serviceWorker.register('/sw.js');await navigator.serviceWorker.ready;
    const subscription=await refresh();
    if(subscription)await post(panel.dataset.pushSubscribe,subscription.toJSON());
  }).catch(error=>message(error.message));
  enable.addEventListener('click',async()=>{
    if(!key||!registration)return;
    try{
      const permission=await Notification.requestPermission();
      if(permission!=='granted'){message('Notification permission was not granted.');return}
      enable.disabled=true;
      const padded=key+'='.repeat((4-key.length%4)%4);
      const bytes=Uint8Array.from(atob(padded.replace(/-/g,'+').replace(/_/g,'/')),c=>c.charCodeAt(0));
      const subscription=await registration.pushManager.subscribe({userVisibleOnly:true,applicationServerKey:bytes});
      try{await post(panel.dataset.pushSubscribe,subscription.toJSON())}catch(error){await subscription.unsubscribe();throw error}
      await refresh();
    }catch(error){enable.disabled=false;message(error.message||'Notifications could not be enabled.')}
  });
  disable.addEventListener('click',async()=>{
    disable.disabled=true;
    try{
      const subscription=await registration.pushManager.getSubscription();
      if(subscription){await post(panel.dataset.pushUnsubscribe,{endpoint:subscription.endpoint});await subscription.unsubscribe()}
      await refresh();
    }catch(error){message(error.message)}finally{disable.disabled=false}
  });
})();
