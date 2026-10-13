// node render_range.js page W H startFrame endFrame outdir
const { chromium } = require('playwright'); const path=require('path'),fs=require('fs');
(async()=>{const [,,page,W,H,a,b,dir]=process.argv;fs.mkdirSync(dir,{recursive:true});
 const br=await chromium.launch();const pg=await br.newPage({viewport:{width:+W,height:+H}});
 pg.on('pageerror',e=>console.error('PAGEERR',e.message));
 await pg.goto('file://'+path.resolve(page));await pg.evaluate(()=>window.ready);
 for(let i=+a;i<+b;i++){await pg.evaluate(t=>render(t),i/30);await pg.screenshot({path:`${dir}/f${String(i).padStart(4,'0')}.jpg`,type:'jpeg',quality:93});}
 await br.close();})();
