# Détourage propre des logos : matte doux + suppression des fonds enfermés + défringe
import numpy as np, sys
from PIL import Image, ImageFilter
from scipy import ndimage as nd
SRC='/root/.claude/uploads/5a1e4201-da67-58f8-8fd4-bf8d5dca5448/185968a3-image.jpg'
def cut(box,out,keep_box=None,global_white=False,scale=3,keep_poly=None):
    im=Image.open(SRC).convert('RGB').crop(box)
    im=im.resize((im.width*scale,im.height*scale),Image.LANCZOS)
    a=np.asarray(im).astype(float); h,w,_=a.shape
    mn=a.min(2)
    white=mn>228
    lab,nlab=nd.label(white)
    bg=np.zeros((h,w),bool)
    border=set(np.unique(np.r_[lab[0],lab[-1],lab[:,0],lab[:,-1]]))-{0}
    for i in border: bg|=lab==i
    # fonds enfermés (intérieur des lettres, entre les feuilles…)
    for i in range(1,nlab+1):
        if i in border: continue
        comp=lab==i
        if global_white: bg|=comp; continue
        ys,xs=np.nonzero(comp); cy,cx=ys.mean()/scale,xs.mean()/scale
        inside=keep_box and keep_box[0]<=cx<=keep_box[2] and keep_box[1]<=cy<=keep_box[3]
        if not inside: bg|=comp
    if keep_poly:
        from PIL import ImageDraw
        pm=Image.new('L',(w,h),0); ImageDraw.Draw(pm).polygon([(x*scale,y*scale) for x,y in keep_poly],fill=255)
        bg&=~(np.asarray(pm)>0)
    # bande de bord : alpha doux par "color-to-alpha" relatif à la couleur intérieure voisine
    near=nd.binary_dilation(bg,iterations=3*scale//2+1)&~bg
    ref=nd.minimum_filter(mn,size=4*scale+1)        # couleur la plus foncée à proximité
    alpha=np.ones((h,w)); alpha[bg]=0
    ea=np.clip((255-mn)/np.maximum(255-ref,25),0,1)
    alpha[near]=ea[near]
    alpha=np.clip(alpha,0,1)
    # dé-contamination du blanc
    A=np.maximum(alpha,1e-3)[...,None]
    col=np.clip((a-(1-A)*255)/A,0,255)
    col[alpha<.02]=0
    rgba=np.dstack([col,alpha*255]).astype('uint8')
    img=Image.fromarray(rgba,'RGBA')
    img=img.crop(img.getbbox())
    img.save(out); print(out,img.size)
# AE-GMPE : on garde les blancs dans le bouclier (pages du livre, pioche)
cut((440,676,970,1234),'aegmpe_t.png',keep_box=(98,118,425,415),keep_poly=[(132,156),(262,152),(394,156),(418,300),(400,350),(355,392),(265,418),(175,392),(128,350),(108,300)])
# FIFEM : aucun blanc voulu dans le logo
cut((50,18,476,318),'fifem_t.png',global_white=True)
