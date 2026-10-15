"""Render: python source.py (Pillow, NumPy, uharfbuzz, freetype-py; FFmpeg on PATH).
System font is read locally, never bundled. All animation is frame-deterministic.
"""
import sys, pathlib, os
if sys.flags.no_site:
    sys.path.append(os.path.join(sys.base_prefix,'Lib','site-packages'))
import numpy as np, uharfbuzz as hb, freetype, subprocess, math, json, datetime, time
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

def render():
    start=datetime.datetime.now(datetime.timezone.utc);timer=time.monotonic()
    rng=np.random.default_rng(41);noise=rng.normal(0,.65,(H,W,1))
    bg=Image.fromarray(np.uint8(np.clip(np.array(PAPER)[None,None,:]+noise,0,255))).convert('RGBA')
    copy=[text_image('หยุดสักนิด',92),text_image('ให้กาแฟ',77),text_image('ค่อย ๆ เล่า',77),text_image('ชงช้า',124)]
    proc=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-movflags','+faststart',str(ROOT/'video.mp4')],stdin=subprocess.PIPE)
    stills=[]
    for frame in range(192):
        t=frame/FPS;im=bg.copy();d=ImageDraw.Draw(im)
        # A slow circle resembles the rim of a cup. Its growth is a timekeeper.
        r=230+32*ease(t/8);cy=1045
        d.ellipse((360-r,cy-r,360+r,cy+r),outline=(189,169,141),width=2)
        d.ellipse((360-r+15,cy-r+15,360+r-15,cy+r-15),outline=(213,197,173),width=1)
        a=-math.pi/2+t/8*math.pi*2
        px=360+r*math.cos(a);py=cy+r*math.sin(a)
        d.ellipse((px-5,py-5,px+5,py+5),fill=ACCENT)
        d.line((360,122,360,181),fill=(190,169,141),width=1)
        if t<2.5:
            op=min(ease(t/.65),ease((2.5-t)/.4));paste(im,copy[0],360,515+25*(1-ease(t/.9)),op)
        elif t<5.5:
            u=t-2.5;op=min(ease(u/.6),ease((5.5-t)/.4))
            paste(im,copy[1],360,465+22*(1-ease(u/.8)),op)
            paste(im,copy[2],360,570+22*(1-ease((u-.14)/.8)),op)
        else:
            u=t-5.5;paste(im,copy[3],360,510+22*(1-ease(u/.8)),ease(u/.6))
            d.line((310,634,310+100*ease(u/1.3),634),fill=ACCENT,width=2)
        rgb=im.convert('RGB');proc.stdin.write(rgb.tobytes())
        if frame in (24,82,156):stills.append(rgb.resize((360,640)))
        if frame==156:rgb.save(ROOT/'poster.jpg',quality=95)
    proc.stdin.close();assert proc.wait()==0
    sheet=Image.new('RGB',(1080,640));[sheet.paste(s,(i*360,0)) for i,s in enumerate(stills)];sheet.save(ROOT/'verification.jpg',quality=95)
    result={'started_utc':start.isoformat(),'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_seconds':round(time.monotonic()-timer,3),'repair_passes':0,'frames':192,'duration_seconds':8,'fps':24,'resolution':[720,1280],'skills_read':['superpowers:using-superpowers (subagent exemption)','remotion:remotion-markup (not applied; Python brief)'],'checks':['HarfBuzz Thai shaping with FreeType rasterization','192 deterministic frames encoded'],'playback_status':'not played; sampled frames inspected separately','listening_status':'silent brief; no audio stream'}
    (ROOT/'run.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':render()
