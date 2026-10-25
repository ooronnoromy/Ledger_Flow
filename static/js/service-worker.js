const CACHE='autoledger-bd-push-v7';
const ASSETS=['/static/css/app.css','/static/css/reference.css','/static/css/showcase.css','/static/css/account.css','/static/js/app.js','/static/js/reference.js','/static/js/account.js','/static/js/session.js','/static/js/push.js','/static/img/logo.svg?v=emblem1','/static/img/icon-192.png?v=emblem1','/static/img/icon-512.png?v=emblem1'];
self.addEventListener('install',event=>event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(ASSETS)).then(()=>self.skipWaiting())));
self.addEventListener('activate',event=>event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(key=>key.startsWith('autoledger-bd-')&&key!==CACHE).map(key=>caches.delete(key)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',event=>{
  const url=new URL(event.request.url);
  if(event.request.method!=='GET'||url.origin!==location.origin||!url.pathname.startsWith('/static/'))return;
  event.respondWith(caches.match(event.request).then(hit=>hit||fetch(event.request)));
});
self.addEventListener('push',event=>{
  let data={};try{data=event.data?.json()||{}}catch{}
  event.waitUntil(self.registration.showNotification('New expense recorded',{
    body:'A new car expense has been recorded. Open AutoLedger BD to view it.',
    icon:'/static/img/icon-192.png?v=emblem1',tag:typeof data.tag==='string'?data.tag:'expense',
    data:{url:typeof data.url==='string'?data.url:'/notifications/'}
  }));
});
self.addEventListener('notificationclick',event=>{
  event.notification.close();
  let target=new URL('/notifications/',location.origin);
  try{const url=new URL(event.notification.data?.url,location.origin);if(url.origin===location.origin&&/^\/notifications\/\d+\/open\/$/.test(url.pathname))target=url}catch{}
  event.waitUntil(clients.matchAll({type:'window',includeUncontrolled:true}).then(async windows=>{
    const window=windows.find(item=>new URL(item.url).origin===location.origin);
    if(window){await window.navigate(target.href);return window.focus()}
    return clients.openWindow(target.href);
  }));
});
