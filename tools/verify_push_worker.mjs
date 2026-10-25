import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFile} from 'node:fs/promises';
const code=await readFile(new URL('../static/js/service-worker.js',import.meta.url),'utf8');
const handlers={},shown=[],opened=[],navigated=[],cached=[];
const context={URL,location:{origin:'https://autoledger.test'},fetch:async()=>{},
  caches:{open:async()=>({addAll:async items=>cached.push(...items)}),keys:async()=>['autoledger-bd-old','other-app'],delete:async key=>{assert.equal(key,'autoledger-bd-old')}},
  self:{addEventListener:(name,fn)=>handlers[name]=fn,registration:{showNotification:async(title,options)=>shown.push({title,options})},skipWaiting:async()=>{}},
  clients:{claim:async()=>{},matchAll:async()=>[],openWindow:async url=>opened.push(url)}};
context.self.clients=context.clients;
vm.runInNewContext(code,context);
async function event(name,props={}){let done;handlers[name]({...props,waitUntil:promise=>done=promise});await done}
await event('install');assert(cached.every(url=>url.startsWith('/static/')));
await event('activate');
await event('push',{data:{json:()=>({url:'/notifications/12/open/',tag:'expense-12',body:'Sensitive amount'})}});
assert.equal(shown[0].title,'New expense recorded');assert(!shown[0].options.body.includes('Sensitive'));
assert.equal(shown[0].options.data.url,'/notifications/12/open/');
await event('notificationclick',{notification:{close(){},data:{url:'/notifications/12/open/'}}});
assert.equal(opened.at(-1),'https://autoledger.test/notifications/12/open/');
await event('notificationclick',{notification:{close(){},data:{url:'https://attacker.test/'}}});
assert.equal(opened.at(-1),'https://autoledger.test/notifications/');
context.clients.matchAll=async()=>[{url:'https://autoledger.test/',navigate:async url=>navigated.push(url),focus:async()=>{}}];
await event('notificationclick',{notification:{close(){},data:{url:'/notifications/12/open/'}}});
assert.equal(navigated[0],'https://autoledger.test/notifications/12/open/');
console.log('PASS: push display, private lock-screen text, safe notification URLs, existing-window focus, public-only cache');
