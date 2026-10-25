import {writeFile} from 'node:fs/promises';
const pages = await (await fetch('http://127.0.0.1:9227/json')).json();
const target = pages.find(p => p.url === 'about:blank') || pages.find(p => p.url.startsWith('file:'));
if (!target) throw new Error('No preview tab found');
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((resolve,reject) => {ws.onopen=resolve;ws.onerror=reject});
let id=0;const pending=new Map();
ws.onmessage=e=>{const message=JSON.parse(e.data);if(message.id){const p=pending.get(message.id);pending.delete(message.id);message.error?p.reject(message.error):p.resolve(message.result)}};
function send(method,params={}){return new Promise((resolve,reject)=>{const key=++id;pending.set(key,{resolve,reject});ws.send(JSON.stringify({id:key,method,params}))})}
async function evaluate(expression){const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw new Error(JSON.stringify(r.exceptionDetails));return r.result.value}
await send('Page.enable');
await send('Page.navigate',{url:new URL('../design_preview.html',import.meta.url).href});
await evaluate('new Promise(resolve => {if(document.readyState === "complete")resolve();else addEventListener("load",resolve,{once:true})})');
await evaluate('document.fonts.ready.then(()=>true)');
for(const width of [1440,1280,1150,1024,900,768,390,360]){
  await send('Emulation.setDeviceMetricsOverride',{width,height:900,deviceScaleFactor:1,mobile:width<620});
  await evaluate('new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))');
  const dimensions=await evaluate('({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,images:[...document.images].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src)})');
  console.log(width,JSON.stringify(dimensions));
  const brandFits=await evaluate('(()=>{const brand=document.querySelector(".sidebar .brand"),text=brand.querySelector("b"),range=document.createRange();range.selectNodeContents(text);return range.getBoundingClientRect().right<=brand.getBoundingClientRect().right+1})()');
  if(!brandFits)throw new Error('Sidebar wordmark overflows at '+width);
  if(dimensions.scrollWidth>width) console.log('Overflow',await evaluate('JSON.stringify([...document.querySelectorAll("body *")].filter(e=>getComputedStyle(e).position!=="fixed"&&e.getBoundingClientRect().right>innerWidth+1).map(e=>({tag:e.tagName,class:e.className,right:e.getBoundingClientRect().right})).slice(0,12))'));
  if(width===390||width===1440){const shot=await send('Page.captureScreenshot',{format:'png'});await writeFile(new URL(width===390?'../preview-mobile.png':'../preview-desktop.png',import.meta.url),Buffer.from(shot.data,'base64'))}
  await evaluate('document.querySelector(".account-trigger").click()');
  const menu = await evaluate('(()=>{const panel=document.querySelector(".account-panel"),rect=panel.getBoundingClientRect();return {open:!panel.hidden,left:rect.left,right:rect.right,bottom:rect.bottom}})()');
  if(!menu.open || menu.left<0 || menu.right>width || menu.bottom>900)throw new Error('Account menu does not fit at '+width);
  if(width===390||width===1440){const shot=await send('Page.captureScreenshot',{format:'png'});await writeFile(new URL(`../preview-account-${width}.png`,import.meta.url),Buffer.from(shot.data,'base64'))}
  await evaluate('document.dispatchEvent(new KeyboardEvent("keydown",{key:"Escape",bubbles:true}))');
  if(!await evaluate('document.querySelector(".account-panel").hidden && document.activeElement===document.querySelector(".account-trigger")'))throw new Error('Account menu keyboard close failed');
  await evaluate('document.querySelector(".account-trigger").click();document.querySelector(".page-content").click()');
  if(!await evaluate('document.querySelector(".account-panel").hidden'))throw new Error('Outside click close failed');
}
await evaluate('document.querySelector("[data-preview-add]").click()');
if(!await evaluate('document.querySelector("dialog").open'))throw new Error('Expense dialog did not open');
await evaluate('document.querySelector("[name=description]").value="Preview verification";document.querySelector("[name=amount]").value="500";document.querySelector("#demo-expense").requestSubmit()');
if(!await evaluate('document.querySelector(".transaction-list").textContent.includes("Preview verification")'))throw new Error('Preview save failed');
if(!await evaluate('document.querySelector(".stat-red strong").textContent.includes("39,150")'))throw new Error('Preview total failed');
await evaluate('document.querySelector(".global-search input").value="Preview verification";document.querySelector(".global-search input").dispatchEvent(new Event("input"))');
if(!await evaluate('[...document.querySelectorAll(".transaction")].filter(e=>getComputedStyle(e).display!=="none").length===1'))throw new Error('Search failed');
console.log('PASS: expense modal, save, total update, search, account menu, keyboard dismissal, outside click');
for (const [width,height] of [[1440,900],[1366,768],[1366,600],[1024,480],[390,667],[844,390]]) {
  await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:width<620});
  await evaluate('new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))');
  const fit = await evaluate('(()=>{const side=document.querySelector(".sidebar"),nav=side.querySelector(".side-nav"),banner=side.querySelector(".bd-banner-reference"),s=side.getBoundingClientRect(),n=nav.getBoundingClientRect(),b=banner.getBoundingClientRect();return {overflow:getComputedStyle(side).overflowY,scrollHeight:side.scrollHeight,height:side.clientHeight,navFits:n.bottom<=s.bottom,bannerFits:!b.height||b.bottom<=s.bottom+1}})()');
  if(fit.scrollHeight>fit.height+1 || !fit.navFits || !fit.bannerFits || ['auto','scroll'].includes(fit.overflow))throw new Error('Sidebar does not fit '+JSON.stringify({width,height,...fit}));
  console.log('Sidebar fits',width,height);
}
for(const fixture of ['driver','driver-form','notifications','push-settings']){
  await send('Page.navigate',{url:new URL(`../preview-${fixture}.html`,import.meta.url).href});
  await evaluate('new Promise(resolve=>{if(document.readyState==="complete")resolve();else addEventListener("load",resolve,{once:true})})');
  await evaluate('document.fonts.ready.then(()=>true)');
  for(const width of [1440,390]){
    await send('Emulation.setDeviceMetricsOverride',{width,height:1000,deviceScaleFactor:1,mobile:width<620});
    await evaluate('new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))');
    const layout=await evaluate('({width:innerWidth,scrollWidth:document.documentElement.scrollWidth})');
    if(layout.scrollWidth>width)throw new Error('Role screen overflow '+JSON.stringify({fixture,...layout}));
    const shot=await send('Page.captureScreenshot',{format:'png'});
    await writeFile(new URL(`../preview-role-${fixture}-${width}.png`,import.meta.url),Buffer.from(shot.data,'base64'));
  }
}
console.log('PASS: driver dashboard, create-account form, notifications, and notification settings at desktop and mobile widths');
await send('Page.navigate',{url:new URL('../design_preview.html',import.meta.url).href});
ws.close();
