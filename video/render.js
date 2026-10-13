const { chromium } = require('playwright');
const path=require('path'),fs=require('fs');
(async()=>{
  const [,,mode,...args]=process.argv;
  const b=await chromium.launch();
  const pg=await b.newPage({viewport:{width:1080,height:1920}});
  await pg.goto('file://'+path.resolve('index.html'));
  await pg.evaluate(()=>window.ready);
  if(mode==='stills'){
    for(const t of args){await pg.evaluate(t=>render(t),+t);await pg.screenshot({path:`/tmp/claude-0/still_${t}.jpg`,quality:70});}
  }else{
    const fps=30,N=19*fps,dir='frames';fs.mkdirSync(dir,{recursive:true});
    for(let i=0;i<N;i++){await pg.evaluate(t=>render(t),i/fps);await pg.screenshot({path:`${dir}/f${String(i).padStart(4,'0')}.jpg`,type:'jpeg',quality:95});}
  }
  await b.close();
})();
