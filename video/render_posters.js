const { chromium } = require('playwright'); const path=require('path');
const P=[['p1',1080,1080,2,'01_carre_nouveau_partenariat'],['p2',1080,1350,2,'02_portrait_partenaire'],['p3',1080,1920,2,'03_story_officiel'],['p4',794,1123,3.125,'04_A4_impression']];
(async()=>{const b=await chromium.launch();
 for(const [id,w,h,dpr,name] of P){
  const pg=await b.newPage({viewport:{width:w,height:h},deviceScaleFactor:dpr});
  pg.on('pageerror',e=>console.error(e.message));
  await pg.goto('file://'+path.resolve('posters.html')+'#'+id); await pg.evaluate(()=>window.ready);
  await pg.screenshot({path:`affiches/${name}.png`,clip:{x:0,y:0,width:w,height:h}});
  if(id==='p4'){await pg.emulateMedia({media:'screen'});await pg.pdf({path:`affiches/${name}.pdf`,width:'210mm',height:'297mm',printBackground:true,pageRanges:'1'});}
  await pg.close();}
 await b.close();})();
