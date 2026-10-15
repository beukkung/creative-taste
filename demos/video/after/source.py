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

# Source path remains portable after this folder moves to demos/video/after.
ASSET=HERE/'../../assets/coffee-source.mp4'
if not ASSET.exists():ASSET=HERE.parents[3]/'outputs/creative-taste/demos/assets/coffee-source.mp4'
if not ASSET.exists():ASSET=Path.cwd()/'outputs/creative-taste/demos/assets/coffee-source.mp4'
CLIPS=[(5,4),(18,4),(35,5),(46,3),(53,4)]
def audio():
 sr=48000;t=np.arange(20*sr)/sr;rng=np.random.default_rng(73)
 noise=rng.standard_normal(t.size);freq=np.fft.rfftfreq(t.size,1/sr);noise=np.fft.irfft(np.fft.rfft(noise)/np.sqrt(1+(freq/2200)**4),n=t.size)
 # Self-created filtered air/pour texture, with understated glass resonances.
 bed=.006*noise+.004*np.sin(2*np.pi*73.42*t)
 pour=smooth_array((t-8)/.6)*smooth_array((13-t)/.8)
 bloom=smooth_array((t-13)/.2)*smooth_array((16-t)/.4)
 bed+=noise*(.026*pour+.014*bloom)*(1+.16*np.sin(2*np.pi*4.3*t))
 for onset,gain in [(3,.045),(16,.06)]:
  q=np.maximum(0,t-onset);tick=sum(np.sin(2*np.pi*freq*q)*np.exp(-q*decay) for freq,decay in [(1390,12),(2245,18),(3110,23)])
  bed+=gain*tick*(t>=onset)
 bed*=smooth_array(t/.5)*smooth_array((20-t)/1.1)
 stereo=np.stack([bed,np.roll(bed,83)*.96],axis=1)
 with wave.open(str(HERE/'sound-bed.wav'),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes((stereo*32767).clip(-32768,32767).astype('<i2').tobytes())
 return {'peak_dbfs':float(20*np.log10(np.max(np.abs(stereo)))),'rms_dbfs':float(20*np.log10(np.sqrt(np.mean(stereo**2))))}
def smooth_array(v):v=np.clip(v,0,1);return v*v*(3-2*v)
def render():
 start=time.perf_counter();audio_stats=audio()
 filters=[]
 for i,(s,dur) in enumerate(CLIPS):
  filters.append(f'[0:v]trim=start={s}:duration={dur},setpts=PTS-STARTPTS,crop=600:540:270:0,scale=720:648,setsar=1[v{i}]')
 filters.append(''.join(f'[v{i}]' for i in range(5))+'concat=n=5:v=1:a=0,fps=24[out]')
 dec=subprocess.Popen(['ffmpeg','-v','error','-i',str(ASSET),'-filter_complex',';'.join(filters),'-map','[out]','-frames:v','480','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
 enc=encoder(HERE/'video.mp4',HERE/'sound-bed.wav')
 captions=[shape('ก่อนวันจะเริ่ม',62),shape('ค่อย ๆ เท',66),shape('ค่อย ๆ ตื่น',66),shape('ชงช้า',92)]
 for f in range(480):
  t=f/FPS;raw=dec.stdout.read(720*648*3);assert len(raw)==720*648*3,(f,len(raw))
  im=Image.new('RGB',(720,1280),(17,26,24));frame=Image.frombytes('RGB',(720,648),raw)
  # A near full-width aperture keeps both filter rim and drink intact.
  im.paste(frame,(0,338));d=ImageDraw.Draw(im)
  d.line((44,1030,676,1030),fill=(80,86,70),width=1)
  # Small brewing-progress line resolves exactly on the final cup.
  d.line((44,1030,44+632*min(1,t/16),1030),fill=(178,139,90),width=2)
  if t<8:idx=0;a=0;b=8
  elif t<13:idx=1;a=8;b=13
  elif t<16:idx=2;a=13;b=16
  else:idx=3;a=16;b=20
  alpha=smooth((t-a)/.35)
  if idx<3:alpha*=1-smooth((t-(b-.25))/.25)
  paste(im,captions[idx],360,218 if idx<3 else 206,alpha)
  # No extra copy; the ending breathes over the actual final brewed drink.
  if t>=16:d.ellipse((347,1130,373,1156),outline=(178,139,90),width=2)
  if f==444:im.save(HERE/'poster.jpg',quality=96)
  enc.stdin.write(im.tobytes())
 enc.stdin.close();assert enc.wait()==0;dec.stdout.close();assert dec.wait()==0
 (HERE/'render.json').write_text(json.dumps({'render_seconds':time.perf_counter()-start,'frames':480,'audio':audio_stats},indent=2))
if __name__=='__main__':render()
