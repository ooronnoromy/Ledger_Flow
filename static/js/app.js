(()=>{
  'use strict';
  const $=(s,root=document)=>root.querySelector(s);
  const menu=$('#menu-toggle'),side=$('#sidebar'),overlay=$('#sidebar-overlay');
  function closeMenu(){side?.classList.remove('open');overlay?.classList.remove('show')}
  menu?.addEventListener('click',()=>{side?.classList.toggle('open');overlay?.classList.toggle('show')});
  overlay?.addEventListener('click',closeMenu);
  document.querySelectorAll('form.confirm-delete').forEach(form=>form.addEventListener('submit',e=>{if(!confirm(form.dataset.confirm||'Delete this item? / রেকর্ডটি মুছে ফেলবেন?'))e.preventDefault()}));

  // Canvas chart: draw locally with no third-party API, CDN, or data transmission.
  const canvas=$('#spending-chart'),dataNode=$('#chart-data');
  if(canvas && dataNode){
    try{
      const d=JSON.parse(dataNode.textContent),series=[
        {key:'fuel',color:'#008a61'}, {key:'maintenance',color:'#eeae38'}, {key:'other',color:'#4e8aec'}
      ];
      // The dashboard reference presents total monthly spend as one green series.
      const dashboard = !!document.querySelector('.dashboard-title');
      if (dashboard) {
        d.total = d.labels.map((_, i) => ['fuel','maintenance','other'].reduce((sum,key) => sum + Number(d[key]?.[i] || 0), 0));
        series.splice(0, series.length, {key:'total', color:'#008653'});
      }
      const draw=()=>{
        const box=canvas.getBoundingClientRect(),ratio=Math.min(window.devicePixelRatio||1,2);
        if(box.width<1||box.height<1)return;
        canvas.width=Math.floor(box.width*ratio);canvas.height=Math.floor(box.height*ratio);
        const ctx=canvas.getContext('2d');ctx.scale(ratio,ratio);
        const w=box.width,h=box.height,L=dashboard?58:49,R=12,T=14,B=31;
        let max=Math.max(1,...series.flatMap(s=>d[s.key]||[]));
        const magnitude=10**Math.floor(Math.log10(max));const step=Math.max(1,Math.ceil(max/magnitude/4))*magnitude;
        max=dashboard ? Math.max(60000, Math.ceil(max/15000)*15000) : Math.ceil(max/step)*step;
        const mobileBars=dashboard && window.matchMedia('(max-width:620px)').matches;
        const x=i=>mobileBars ? L+(w-L-R)/d.labels.length*(i+.5) : L+(w-L-R)*(d.labels.length===1?.5:i/(d.labels.length-1));
        const y=v=>T+(h-T-B)*(1-v/max);
        ctx.font='11px DM Sans, sans-serif';ctx.textBaseline='middle';ctx.lineWidth=1;
        for(let i=0;i<=4;i++){
          const v=max*i/4,yy=y(v);
          ctx.strokeStyle='#eaf0ef';ctx.beginPath();ctx.moveTo(L,yy);ctx.lineTo(w-R,yy);ctx.stroke();
          ctx.fillStyle='#75808e';ctx.textAlign='right';ctx.fillText(dashboard ? (v ? '৳ '+Math.round(v).toLocaleString('en-US') : '0') : v>=1000?(v/1000).toFixed(v%1000?1:0)+'k':String(Math.round(v)),L-9,yy);
        }
        ctx.textAlign='center';ctx.fillStyle='#91a6a0';
        d.labels.forEach((name,i)=>ctx.fillText(name,x(i),h-9));
        for(const s of series){
          const values=d[s.key]||[];if(!values.length)continue;
          if (dashboard) {
            d.labels.forEach((_,i)=>{ctx.strokeStyle='#eef1f5';ctx.lineWidth=.7;ctx.beginPath();ctx.moveTo(x(i),T);ctx.lineTo(x(i),h-B);ctx.stroke()});
            const fill=ctx.createLinearGradient(0,T,0,h-B);fill.addColorStop(0,'#00a76727');fill.addColorStop(1,'#00a76703');
            ctx.beginPath();ctx.moveTo(x(0),h-B);values.forEach((v,i)=>ctx.lineTo(x(i),y(v)));ctx.lineTo(x(values.length-1),h-B);ctx.closePath();ctx.fillStyle=fill;ctx.fill();
          }
          if (dashboard && window.matchMedia('(max-width:620px)').matches) {
            ctx.clearRect(L,T,w-L,h-T-B);
            for(let i=0;i<=4;i++){ctx.strokeStyle='#edf1f4';ctx.lineWidth=.7;ctx.beginPath();ctx.moveTo(L,y(max*i/4));ctx.lineTo(w-R,y(max*i/4));ctx.stroke()}
            const space=(w-L-R)/values.length;
            values.forEach((v,i)=>{const bar=ctx.createLinearGradient(0,y(v),0,h-B);bar.addColorStop(0,'#008a61');bar.addColorStop(1,'#69b99a');ctx.fillStyle=bar;ctx.fillRect(L+space*i+space*.25,y(v),space*.5,h-B-y(v))});
            continue;
          }
          ctx.lineWidth=2.3;ctx.strokeStyle=s.color;ctx.lineJoin='round';ctx.lineCap='round';
          ctx.beginPath();values.forEach((v,i)=>i?ctx.lineTo(x(i),y(v)):ctx.moveTo(x(i),y(v)));ctx.stroke();
          values.forEach((v,i)=>{ctx.beginPath();ctx.fillStyle=s.color;ctx.arc(x(i),y(v),3,0,Math.PI*2);ctx.fill();ctx.beginPath();ctx.strokeStyle='#fff';ctx.lineWidth=1.2;ctx.arc(x(i),y(v),3,0,Math.PI*2);ctx.stroke()});
        }
      };
      if('ResizeObserver' in window)new ResizeObserver(draw).observe(canvas);else window.addEventListener('resize',draw);
      draw();
    }catch(err){console.warn('Chart could not render',err)}
  }
  const donut=$('#fuel-donut'),fuelData=$('#fuel-data');
  if(donut&&fuelData){
    try{
      const d=JSON.parse(fuelData.textContent);let sum=d.reduce((acc,r)=>acc+r.value,0),current=0;
      const parts=d.map(row=>{let from=current;current+=row.value/sum*360;return `${row.color} ${from.toFixed(2)}deg ${current.toFixed(2)}deg`});
      donut.style.background=sum>0?`conic-gradient(${parts.join(',')})`:'conic-gradient(#dfebe5 0deg 360deg)';
    }catch(err){console.warn('Donut could not render',err)}
  }
  // Fuel-only extra fields are hidden for other expense categories.
  const category=$('[data-field="category"] select');
  if(category){
    const fuelOnly=['fuel_type','quantity','meter_photo'];
    const update=()=>{const isFuel=category.value==='FUEL';fuelOnly.forEach(name=>{const e=$(`[data-field="${name}"]`);if(e)e.style.display=isFuel?'':'none'})};
    category.addEventListener('change',update);update();
  }

  // Install button follows browser capabilities; iOS has a manual fallback.
  let deferredPrompt=null;
  const installBtn=$('#install-app'),info=$('#install-info');
  window.addEventListener('beforeinstallprompt',event=>{
    event.preventDefault();deferredPrompt=event;
    if(info)info.textContent='Ready to install on this device.';
  });
  window.addEventListener('appinstalled',()=>{
    deferredPrompt=null;if(info)info.textContent='AutoLedger BD installed successfully.';
  });
  installBtn?.addEventListener('click',async()=>{
    if(deferredPrompt){
      const prompt=deferredPrompt;deferredPrompt=null;prompt.prompt();
      const result=await prompt.userChoice;
      if(info)info.textContent=result.outcome==='accepted'?'Installation accepted.':'You can install later from the browser menu.';
      return;
    }
    const isIOS=/iphone|ipad|ipod/i.test(navigator.userAgent);
    if(info)info.textContent=isIOS?'On iPhone: use Safari → Share → Add to Home Screen.':'In Chrome/Edge: browser menu → Install App or Add to Home Screen. Requires HTTPS or localhost.';
  });
  if('serviceWorker' in navigator && (location.protocol==='https:' || location.hostname==='localhost' || location.hostname==='127.0.0.1')){
    window.addEventListener('load',()=>navigator.serviceWorker.register('/sw.js').catch(()=>{}));
  }
})();
