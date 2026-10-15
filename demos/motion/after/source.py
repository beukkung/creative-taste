import io,json,math,subprocess,time,wave
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
import uharfbuzz as hb
import freetype
W,H,FPS=720,1280,24
HERE=Path(__file__).resolve().parent
FONT=Path('C:/Windows/Fonts/tahoma.ttf')
def shape(text,size,color=(239,234,216)):
 data=FONT.read_bytes(); face=hb.Face(data);font=hb.Font(face);font.scale=(size*64,size*64);hb.ot_font_set_funcs(font)
 buf=hb.Buffer();buf.add_str(text);buf.guess_segment_properties();hb.shape(font,buf)
 ft=freetype.Face(str(FONT));ft.set_pixel_sizes(0,size)
 pieces=[];x=y=0
 for info,pos in zip(buf.glyph_infos,buf.glyph_positions):
  ft.load_glyph(info.codepoint,freetype.FT_LOAD_RENDER);g=ft.glyph;b=g.bitmap
  if b.width and b.rows:
   arr=np.array(b.buffer,dtype=np.uint8).reshape(b.rows,abs(b.pitch))[:,:b.width]
   pieces.append((round((x+pos.x_offset)/64)+g.bitmap_left,round(-(y+pos.y_offset)/64)-g.bitmap_top,Image.fromarray(arr)))
  x+=pos.x_advance;y+=pos.y_advance
 minx=min(p[0] for p in pieces);miny=min(p[1] for p in pieces);maxx=max(p[0]+p[2].width for p in pieces);maxy=max(p[1]+p[2].height for p in pieces)
 mask=Image.new('L',(maxx-minx,maxy-miny))
 for px,py,b in pieces:mask.paste(b,(px-minx,py-miny),b)
 layer=Image.new('RGBA',mask.size,color+(255,));layer.putalpha(mask);return layer

def paste(im,layer,cx,cy,opacity=1):
 if opacity<=0:return
 if opacity<1:layer=layer.copy();layer.putalpha(layer.getchannel('A').point(lambda a:int(a*opacity)))
 im.paste(layer,(round(cx-layer.width/2),round(cy-layer.height/2)),layer)
def smooth(x):return (lambda v:v*v*(3-2*v))(max(0,min(1,x)))
def ffprobe(path):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
def encoder(path,audio=None):
 cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size','720x1280','-framerate','24','-i','-']
 if audio:cmd+=['-i',str(audio)]
 cmd+=['-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p']
 if audio:cmd+=['-c:a','aac','-b:a','160k','-ar','48000','-t','20']
 else:cmd+=['-an']
 return subprocess.Popen(cmd+['-movflags','+faststart',str(path)],stdin=subprocess.PIPE)

def render():
 start=time.perf_counter();frames=192
 layers=[shape('หยุดสักนิด',81),shape('ให้กาแฟค่อย ๆ เล่า',61),shape('ชงช้า',118)]
 enc=encoder(HERE/'video.mp4')
 yy,xx=np.mgrid[0:H,0:W];glow=np.exp(-(((xx-360)/620)**2+((yy-720)/900)**2))
 bg=np.zeros((H,W,3),dtype=np.uint8)
 for k,(base,amp) in enumerate([(14,9),(27,12),(25,8)]):bg[:,:,k]=base+amp*glow
 for f in range(frames):
  t=f/FPS;im=Image.fromarray(bg);d=ImageDraw.Draw(im)
  # A single copper surface breathes. It opens gradually; no decorative burst.
  for j in range(3):
   phase=max(0,t-.35-j*.35);r=70+phase*15+j*15
   alpha=max(.1,.75-j*.18)
   c=tuple(int(a*alpha+b*(1-alpha)) for a,b in zip((178,130,82),(19,34,30)))
   d.ellipse((360-r,930-r*.25,360+r,930+r*.25),outline=c,width=2)
  for idx,(a,b) in enumerate([(0,2.45),(2.45,5.65),(5.65,8)]):
   if a<=t<b:
    local=t-a;opacity=smooth(local/.48)
    # Clear hold before the line yields the shared stage.
    if idx<2:opacity*=1-smooth((t-(b-.34))/.34)
    y=573+25*(1-smooth(local/.72))
    paste(im,layers[idx],360,y,opacity)
  # Persistent vertical axis connects type with the coffee surface.
  d.line((360,760,360,817),fill=(119,108,79),width=1)
  if f==160:im.save(HERE/'poster.jpg',quality=96)
  enc.stdin.write(im.tobytes())
 enc.stdin.close();assert enc.wait()==0
 (HERE/'render.json').write_text(json.dumps({'render_seconds':time.perf_counter()-start,'frames':frames},indent=2))
if __name__=='__main__':render()
