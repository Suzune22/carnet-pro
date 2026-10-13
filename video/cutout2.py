# Détourage des logos depuis logos_src.jpg (damier de transparence incrusté)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as nd
SRC='assets/logos_src.jpg'
def cut(box,out,keep_poly=None,scale=3,extra=None):
    im=Image.open(SRC).convert('RGB').crop(box)
    im=im.resize((im.width*scale,im.height*scale),Image.LANCZOS)
    a=np.asarray(im).astype(float); h,w,_=a.shape
    mn,mx=a.min(2),a.max(2)
    bgish=(mn>186)&(mx-mn<22)
    lab,nl=nd.label(bgish)
    border=set(np.unique(np.r_[lab[0],lab[-1],lab[:,0],lab[:,-1]]))-{0}
    bg=np.isin(lab,list(border))
    keep=np.zeros((h,w),bool)
    if keep_poly:
        pm=Image.new('L',(w,h),0); ImageDraw.Draw(pm).polygon([((x-box[0])*scale,(y-box[1])*scale) for x,y in keep_poly],fill=255)
        keep=np.asarray(pm)>0
    # fonds enfermés (intérieur des lettres, entre les feuilles) hors zone protégée
    sizes=nd.sum(np.ones_like(lab),lab,index=np.arange(1,nl+1))
    for i in range(1,nl+1):
        if i in border: continue
        comp=lab==i
        if (comp&keep).sum()>comp.sum()*.5: continue
        bg|=comp
    bg&=~keep
    fg=~bg
    fg=nd.binary_opening(fg,iterations=1)
    bgm=~fg
    core=nd.binary_erosion(fg,iterations=scale)
    _,(fy,fx)=nd.distance_transform_edt(~core,return_indices=True)   # couleur logo la plus proche
    _,(by,bx)=nd.distance_transform_edt(fg,return_indices=True)      # couleur fond la plus proche
    F=a[fy,fx]; B=a[by,bx]
    band=nd.binary_dilation(fg,iterations=2)&~core
    d=F-B; den=(d*d).sum(2)
    al=np.clip(((a-B)*d).sum(2)/np.maximum(den,1),0,1)
    al=np.where(den<900,fg.astype(float),al)
    alpha=np.where(core,1.0,np.where(band,al,0.0))
    a=np.where(band[...,None],F,a)
    alpha=np.asarray(Image.fromarray((alpha*255).astype('uint8')).filter(ImageFilter.GaussianBlur(.6))).astype(float)/255
    rgba=np.dstack([a,alpha*255]).clip(0,255).astype('uint8')
    img=Image.fromarray(rgba,'RGBA')
    if extra: extra(img,box,scale)
    img=img.crop(img.getbbox()); img.save(out); print(out,img.size)
def fifem_line(img,box,scale):     # filet gris vertical du logo FIFEM
    d=ImageDraw.Draw(img); x=(136-box[0])*scale
    d.line([(x,(332-box[1])*scale),(x,(548-box[1])*scale)],fill=(190,190,190,255),width=max(2,scale))
cut((612,262,968,636),'assets/aegmpe_t.png',
    keep_poly=[(694,350),(787,345),(882,350),(886,440),(870,482),(830,516),(787,536),(744,516),(704,482),(690,440)])
cut((55,315,418,572),'assets/fifem_t.png',extra=fifem_line)
