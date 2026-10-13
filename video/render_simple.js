const { chromium } = require('playwright'); const path=require('path');
const P=[['s1',1080,1080,'01_carre'],['s2',1080,1350,'02_portrait_4x5'],['s3',1080,1920,'03_story'],['s4',1080,1080,'04_carre_fond_sombre']];
(async()=>{const b=await chromium.launch();
 for(const [id,w,h,name] of P){const pg=await b.newPage({viewport:{width:w,height:h},deviceScaleFactor:2});
  await pg.goto('file://'+path.resolve('simple.html')+'#'+id); await pg.evaluate(()=>window.ready);
  await pg.screenshot({path:`affiches_simples/AE-GMPE_x_FIFEM_${name}.png`}); await pg.close();}
 await b.close();})();
