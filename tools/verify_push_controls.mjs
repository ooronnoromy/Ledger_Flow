import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFile} from 'node:fs/promises';
const source=await readFile(new URL('../static/js/push.js',import.meta.url),'utf8');
const flush=()=>new Promise(resolve=>setImmediate(resolve));
function setup(secure=true){
  const requests=[],enable={disabled:true,addEventListener:(_,fn)=>enable.click=fn},disable={hidden:true,addEventListener:(_,fn)=>disable.click=fn},status={};
  let subscription=null,permissions=0;
  const panel={dataset:{pushConfig:'/config',pushSubscribe:'/subscribe',pushUnsubscribe:'/unsubscribe'},querySelector:selector=>selector.includes('enable')?enable:selector.includes('disable')?disable:status};
  const Notification={permission:'default',requestPermission:async()=>{permissions++;Notification.permission='granted';return 'granted'}};
  const registration={pushManager:{getSubscription:async()=>subscription,subscribe:async options=>{assert.equal(options.userVisibleOnly,true);subscription={endpoint:'https://fcm.googleapis.com/demo',toJSON:()=>({endpoint:'https://fcm.googleapis.com/demo',keys:{}}),unsubscribe:async()=>{subscription=null;return true}};return subscription}}};
  const context={window:{isSecureContext:secure,PushManager:class{},Notification},Notification,
    navigator:{serviceWorker:{register:async()=>registration,ready:Promise.resolve(registration)}},
    document:{querySelector:selector=>selector==='[data-push-settings]'?panel:{value:'csrf-token'}},
    fetch:async(url,options)=>{requests.push({url,options});return {redirected:false,ok:true,json:async()=>url==='/config'?{ready:true,publicKey:Buffer.alloc(65,4).toString('base64url')}:{enabled:true}}},
    location:{assign:()=>{}},Uint8Array,atob,
  };
  vm.runInNewContext(source,context);
  return {enable,disable,status,requests,permissionCount:()=>permissions,subscription:()=>subscription};
}
const app=setup();await flush();
assert.equal(app.enable.disabled,false);assert.equal(app.permissionCount(),0);
await app.enable.click();assert.equal(app.permissionCount(),1);
assert.equal(app.enable.disabled,true);assert.equal(app.disable.hidden,false);
assert.equal(app.requests.find(r=>r.url==='/subscribe').options.headers['X-CSRFToken'],'csrf-token');
await app.disable.click();assert.equal(app.subscription(),null);assert.equal(app.enable.disabled,false);
assert(app.requests.some(r=>r.url==='/unsubscribe'));
const insecure=setup(false);await flush();assert(insecure.status.textContent.includes('HTTPS'));assert.equal(insecure.permissionCount(),0);
console.log('PASS: permission only on click, subscribe, CSRF protection, unsubscribe, unsupported-browser guidance');
