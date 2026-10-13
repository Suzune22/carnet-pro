import sys
from PIL import Image
ts=sys.argv[1:]; ims=[Image.open(f'/tmp/claude-0/still_{t}.jpg').resize((480,270)) for t in ts]
from PIL import ImageDraw
cols=3; rows=(len(ims)+cols-1)//cols; c=Image.new('RGB',(480*cols,270*rows),'black')
for i,(t,im) in enumerate(zip(ts,ims)):
    ImageDraw.Draw(im).text((6,4),t,fill='red'); c.paste(im,((i%cols)*480,(i//cols)*270))
c.save('/tmp/claude-0/sheet.jpg')
