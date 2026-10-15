"""Render: python source.py [--input ../../assets/coffee-source.mp4]
System font is read locally, never bundled. All animation is frame-deterministic.
"""
import sys, pathlib, os
if sys.flags.no_site:
    sys.path.append(os.path.join(sys.base_prefix,'Lib','site-packages'))
import numpy as np, uharfbuzz as hb, freetype, subprocess, math, json, datetime, time, argparse, wave
from PIL import Image, ImageDraw
ROOT=pathlib.Path(__file__).resolve().parent
FONT=pathlib.Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts'/'tahoma.ttf'
W,H,FPS=720,1280,24
INK=(63,43,32); PAPER=(237,228,208); ACCENT=(165,104,64)

def text_image(text,size,color=INK):
    data=FONT.read_bytes(); font=hb.Font(hb.Face(data));font.scale=(size*64,size*64)
    hb.ot_font_set_funcs(font); buf=hb.Buffer();buf.add_str(text);buf.guess_segment_properties();hb.shape(font,buf)
    face=freetype.Face(str(FONT));face.set_pixel_sizes(0,size)
    glyphs=[];x=0; minx=0;miny=0;maxx=0;maxy=0
    for info,pos in zip(buf.glyph_infos,buf.glyph_positions):
        face.load_glyph(info.codepoint,freetype.FT_LOAD_RENDER)
        b=face.glyph.bitmap;gx=round(x+pos.x_offset/64)+face.glyph.bitmap_left;gy=-round(pos.y_offset/64)-face.glyph.bitmap_top
        if b.width and b.rows:
            a=np.array(b.buffer,dtype=np.uint8).reshape(b.rows,b.pitch)[:,:b.width].copy();glyphs.append((gx,gy,Image.fromarray(a)))
            minx=min(minx,gx);miny=min(miny,gy);maxx=max(maxx,gx+b.width);maxy=max(maxy,gy+b.rows)
        x+=pos.x_advance/64
    mask=Image.new('L',(max(maxx,round(x))-minx+8,maxy-miny+8))
    for gx,gy,g in glyphs: mask.paste(g,(gx-minx+4,gy-miny+4),g)
    out=Image.new('RGBA',mask.size,color+(0,));out.putalpha(mask);return out

def ease(x):
    x=max(0,min(1,x));return 1-(1-x)**3

def paste(im,layer,cx,cy,alpha=1):
    layer=layer.copy();layer.putalpha(layer.getchannel('A').point(lambda p:int(p*max(0,min(1,alpha)))))
    im.alpha_composite(layer,(round(cx-layer.width/2),round(cy-layer.height/2)))

def sound_bed():
    sr=48000;t=np.arange(sr*20)/sr;rng=np.random.default_rng(83)
    env=np.minimum(np.clip(t/1.5,0,1),np.clip((20-t)/2,0,1))
    pad=sum(np.sin(2*np.pi*f*t+.15*np.sin(2*np.pi*.06*t))*a for f,a in [(130.81,.025),(196,.017),(261.63,.012),(293.66,.009)])
    frequencies=np.fft.rfftfreq(len(t),1/sr)
    spectrum=np.fft.rfft(rng.normal(0,1,len(t)))
    band=(frequencies/450)**2/(1+(frequencies/450)**2)/(1+(frequencies/3500)**4)
    noise=np.fft.irfft(spectrum*band,n=len(t))
    pour=(np.clip((t-6)/.8,0,1)*np.clip((13-t)/1.3,0,1))*.023*(.8+.2*np.sin(t*8))
    sound=(pad+noise*pour)*env
    for sec in [0.3,6.1,13.1,16.1]:
        u=t-sec; e=np.where(u>=0,np.exp(-np.maximum(u,0)*8),0)
        sound+=.022*e*(np.sin(2*np.pi*1568*u)+.4*np.sin(2*np.pi*2637*u))
    stereo=np.stack((sound,np.roll(sound,27)*.98),1)
    with wave.open(str(ROOT/'sound-bed.wav'),'wb') as out:
        out.setnchannels(2);out.setsampwidth(2);out.setframerate(sr);out.writeframes(np.int16(np.clip(stereo,-1,1)*32767).tobytes())
    return {'sample_peak':float(np.max(np.abs(stereo))),'rms':float(np.sqrt(np.mean(stereo**2))),'sample_rate':sr,'provenance':'original procedural oscillators and seeded filtered noise'}

def render():
    start=datetime.datetime.now(datetime.timezone.utc);timer=time.monotonic()
    args=argparse.ArgumentParser();args.add_argument('--input',type=pathlib.Path,default=ROOT/'../../assets/coffee-source.mp4');src=args.parse_args().input.resolve()
    if not src.exists():raise FileNotFoundError('Supply --input path/to/coffee-source.mp4')
    rng=np.random.default_rng(41);noise=rng.normal(0,.65,(H,W,1))
    bg=Image.fromarray(np.uint8(np.clip(np.array(PAPER)[None,None,:]+noise,0,255))).convert('RGBA')
    copy=[text_image('ก่อนวันจะเริ่ม',64),text_image('ค่อย ๆ เท',72),text_image('ค่อย ๆ ตื่น',72),text_image('ชงช้า',106)]
    # Keep the complete brewing sequence. Only the supplied footage is decoded.
    # Slowed filter preparation and one-second final cup hold stop before source credits.
    clips=[(9,4,3),(18,2,1),(34,7,1),(42,3,1),(53.6,4,4)]
    frames=[]
    for seek,duration,slow in clips:
        vf=f'setpts={slow}*PTS,fps=24,scale=996:560,crop=664:560:166:0'
        raw=subprocess.check_output(['ffmpeg','-v','error','-ss',str(seek),'-i',str(src),'-t',str(duration),'-an','-vf',vf,'-f','rawvideo','-pix_fmt','rgb24','-'])
        arr=np.frombuffer(raw,dtype=np.uint8).reshape(-1,560,664,3)
        selected=list(arr[:duration*FPS])
        # A retimed segment can land between source frame timestamps. Hold its
        # last frame to keep the editorial duration frame-exact.
        while len(selected)<duration*FPS:selected.append(selected[-1])
        frames.extend(selected)
    assert len(frames)==480,len(frames)
    audio_stats=sound_bed()
    proc=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',str(ROOT/'sound-bed.wav'),'-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-t','20','-movflags','+faststart',str(ROOT/'video.mp4')],stdin=subprocess.PIPE)
    stills=[]
    for frame in range(480):
        t=frame/FPS;im=bg.copy()
        shot=Image.fromarray(frames[frame]).convert('RGB')
        # Subtle warm grade; no generative imagery or artificial camera movement.
        arr=np.array(shot,dtype=np.float32);arr[:,:,0]*=1.025;arr[:,:,2]*=.965
        shot=Image.fromarray(np.uint8(np.clip(arr,0,255))).convert('RGBA')
        im.alpha_composite(shot,(28,377));d=ImageDraw.Draw(im)
        d.line((360,119,360,167),fill=(190,169,141),width=1)
        idx=0 if t<6 else 1 if t<13 else 2 if t<16 else 3
        begin=[0,6,13,16][idx];end=[6,13,16,20][idx]
        op=min(ease((t-begin)/.5),ease((end-t)/.3)) if idx<3 else ease((t-begin)/.5)
        paste(im,copy[idx],360,252+14*(1-ease((t-begin)/.7)),op)
        d.line((290,1048,430,1048),fill=(200,179,151),width=1)
        d.line((290,1048,290+140*t/20,1048),fill=ACCENT,width=2)
        for k in range(4):
            x=336+k*16;d.ellipse((x-2,1117,x+2,1121),fill=ACCENT if k==idx else (205,187,162))
        rgb=im.convert('RGB');proc.stdin.write(rgb.tobytes())
        if frame in (48,120,216,336,444):stills.append(rgb.resize((288,512)))
        if frame==444:rgb.save(ROOT/'poster.jpg',quality=95)
    proc.stdin.close();assert proc.wait()==0
    sheet=Image.new('RGB',(1440,512));[sheet.paste(s,(i*288,0)) for i,s in enumerate(stills)];sheet.save(ROOT/'verification.jpg',quality=95)
    result={'started_utc':start.isoformat(),'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_seconds':round(time.monotonic()-timer,3),'repair_passes':0,'frames':480,'duration_seconds':20,'fps':24,'resolution':[720,1280],'skills_read':['superpowers:using-superpowers (subagent exemption)','remotion:remotion-markup (not applied; Python brief)'],'checks':['HarfBuzz Thai shaping with FreeType rasterization','480 deterministic frames encoded'],'audio':audio_stats,'playback_status':'not played; sampled frames inspected separately','listening_status':'not listened; procedural audio measured numerically'}
    (ROOT/'run.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':render()
