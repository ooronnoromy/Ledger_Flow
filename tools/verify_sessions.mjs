import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFile} from 'node:fs/promises';
const source=await readFile(new URL('../static/js/session.js',import.meta.url),'utf8');
function setup(){
  const events={},timers=new Map(),intervals=[],requests=[],redirects=[],broadcasts=[];
  let next=0,channel;
  class Channel{constructor(){channel=this}postMessage(message){broadcasts.push(message)}addEventListener(name,fn){this.listener=fn}}
  const context={
    document:{body:{dataset:{sessionTimeout:'300',sessionActivity:'/account/activity/',sessionLogout:'/logout/',sessionLogin:'/login/'}},querySelector:()=>({value:'test-csrf'}),addEventListener:(name,fn)=>events[name]=fn},
    window:{BroadcastChannel:Channel,addEventListener:(name,fn)=>events[name]=fn},BroadcastChannel:Channel,
    location:{replace:url=>redirects.push(url),reload:()=>redirects.push('reload')},
    fetch:async(url,options)=>{requests.push({url,options});return {status:204,redirected:false}},
    setTimeout:(fn,delay)=>{timers.set(++next,{fn,delay});return next},clearTimeout:id=>timers.delete(id),
    setInterval:fn=>intervals.push(fn),Date,
  };
  vm.runInNewContext(source,context);
  return {events,timers,intervals,requests,redirects,broadcasts,channel};
}
const idle=setup();
assert.equal([...idle.timers.values()][0].delay,300000);
[...idle.timers.values()][0].fn();
await new Promise(resolve=>setImmediate(resolve));
assert.equal(idle.requests[0].url,'/logout/');
assert.equal(idle.requests[0].options.method,'POST');
assert.equal(idle.requests[0].options.headers['X-CSRFToken'],'test-csrf');
assert.deepEqual(idle.redirects,['/login/']);
assert.deepEqual(idle.broadcasts,['logout']);
const active=setup();
await active.intervals[0]();assert.equal(active.requests.length,0);
active.events.keydown();
assert.equal(active.timers.size,1);
await active.intervals[0]();
assert.equal(active.requests[0].url,'/account/activity/');
await active.intervals[0]();assert.equal(active.requests.length,1);
active.channel.listener({data:'activity'});assert.equal(active.timers.size,1);
active.channel.listener({data:'logout'});assert.deepEqual(active.redirects,['/login/']);
active.events.pageshow({persisted:true});assert.equal(active.redirects.at(-1),'reload');
console.log('PASS: five-minute timer, activity heartbeat, CSRF logout, cross-tab activity and logout, back-button refresh');
