// usage: node render.js <page.html> <W> <H> <dur> stills t1 t2 ... | frames <outdir>
const { chromium } = require('playwright');
const path=require('path'),fs=require('fs');
(async()=>{
  const [,,page,W,H,dur,mode,...args]=process.argv;
  const b=await chromium.launch();
  const pg=await b.newPage({viewport:{width:+W,height:+H}});
  pg.on('pageerror',e=>console.error('PAGEERR',e.message));
  await pg.goto('file://'+path.resolve(page));
  await pg.evaluate(()=>window.ready);
  if(mode==='stills'){
    for(const t of args){await pg.evaluate(t=>render(t),+t);await pg.screenshot({path:`/tmp/claude-0/still_${t}.jpg`,quality:70});}
  }else{
    const fps=30,N=Math.round(+dur*fps),dir=args[0]||'frames';fs.mkdirSync(dir,{recursive:true});
    for(let i=0;i<N;i++){await pg.evaluate(t=>render(t),i/fps);await pg.screenshot({path:`${dir}/f${String(i).padStart(4,'0')}.jpg`,type:'jpeg',quality:93});}
  }
  await b.close();
})();
