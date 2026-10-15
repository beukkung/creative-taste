"""Verify the distributable package and actual demo media using stdlib + FFmpeg."""
import array
import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote
import wave

ROOT=Path(__file__).resolve().parent.parent


def main():
    checks=[]; media=[]
    def require(condition, name, detail=''):
        checks.append({'check':name,'passed':bool(condition),'detail':detail})
    skill=ROOT/'skills/creative-taste/SKILL.md'
    text=skill.read_text(encoding='utf-8')
    require(text.startswith('---\n') and '\nname: creative-taste\n' in text,'skill frontmatter/name')
    desc=re.search(r'^description: (.+)$',text,re.M)
    require(desc and len(desc.group(1))<=1024,'ZCode description size')
    require(len(text.encode('utf-8'))<100_000,'ZCode body size')
    lock=json.loads((ROOT/'evaluation/input-lock.json').read_text())
    for name,digest in lock['files'].items():
        path=ROOT/name
        require(path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==digest,'input unchanged: '+name)
    for path in ROOT.rglob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
            if re.match(r'^(?:https?:|mailto:|#)',target):continue
            target=unquote(target.split('#')[0].strip('<>'))
            require((path.parent/target).exists(),'markdown link',path.relative_to(ROOT).as_posix()+': '+target)
    for domain in ['frontend','music','motion','video']:
        for condition in ['before','after']:
            folder=ROOT/'demos'/domain/condition
            required={'frontend':['index.html','desktop.png','mobile.png'],'music':['compose.py','music.wav','mix.wav','music-preview.mp3','mix-preview.mp3'],'motion':['source.py','video.mp4','poster.jpg'],'video':['source.py','video.mp4','poster.jpg']}[domain]+['decisions.md','run.json']
            for filename in required:require((folder/filename).is_file(),'demo file: '+str((folder/filename).relative_to(ROOT)))
            if domain=='music':
                for filename in ['music.wav','mix.wav']:
                    path=folder/filename
                    if not path.exists():continue
                    with wave.open(str(path),'rb') as audio:
                        samples=array.array('h',audio.readframes(audio.getnframes()))
                        if sys.byteorder!='little':samples.byteswap()
                        info={'path':path.relative_to(ROOT).as_posix(),'rate':audio.getframerate(),'channels':audio.getnchannels(),'width':audio.getsampwidth(),'frames':audio.getnframes(),'sample_peak':max(abs(v) for v in samples)/32768,'clipped_samples':sum(v in [-32768,32767] for v in samples)}
                    require(info['rate']==48000 and info['channels']==2 and info['width']==2 and info['frames']==960000,'PCM format: '+info['path'])
                    require(info['clipped_samples']==0,'no clipped PCM samples: '+info['path'])
                    media.append(info)
            elif domain in ['motion','video']:
                path=folder/'video.mp4'
                if not path.exists():continue
                probe=subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)],capture_output=True,text=True,check=True)
                data=json.loads(probe.stdout); video=next(s for s in data['streams'] if s['codec_type']=='video')
                audio=[s for s in data['streams'] if s['codec_type']=='audio']
                expected=8 if domain=='motion' else 20
                require(video['width']==720 and video['height']==1280 and video['codec_name']=='h264' and video['pix_fmt']=='yuv420p' and video['r_frame_rate']=='24/1' and int(video['nb_frames'])==expected*24,'video format: '+str(path.relative_to(ROOT)))
                require(abs(float(data['format']['duration'])-expected)<.05,'video duration: '+str(path.relative_to(ROOT)))
                require(len(audio)==(1 if domain=='video' else 0),'audio stream count: '+str(path.relative_to(ROOT)))
                if audio:require(audio[0]['codec_name']=='aac' and int(audio[0]['sample_rate'])==48000 and audio[0]['channels']==2,'video audio format: '+str(path.relative_to(ROOT)))
                decode=subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(path),'-f','null','-'],capture_output=True,text=True)
                require(decode.returncode==0,'complete decode: '+str(path.relative_to(ROOT)),decode.stderr[:300])
                media.append({'path':path.relative_to(ROOT).as_posix(),'seconds':float(data['format']['duration']),'frames':int(video['nb_frames']),'full_decode':decode.returncode==0})
    preview=json.loads((ROOT/'evaluation/preview-loudness.json').read_text())
    for item in preview['files']:require(abs(item['preview_lufs']-item['target_lufs'])<=.15 and item['preview_true_peak_dbtp']<=-2,'matched loudness: '+item['path'])
    for path in ROOT.rglob('*'):
        if not path.is_file() or '.git' in path.parts or '__pycache__' in path.parts:continue
        require(path.stat().st_size<90_000_000,'GitHub file limit: '+str(path.relative_to(ROOT)))
        if path.suffix in ['.md','.json','.py','.html','.js','.cjs','.yaml','.css']:
            content=path.read_text(encoding='utf-8-sig')
            require(not re.search(r'gh[pousr]_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9]{28,}',content),'no token pattern: '+str(path.relative_to(ROOT)))
            require(not re.search(r'C:[/\\]+Users[/\\]+\d',content),'no private user path: '+str(path.relative_to(ROOT)))
    failures=[c for c in checks if not c['passed']]
    report={'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':not failures,'check_count':len(checks),'failures':failures,'media':media,'checks':checks,'perceptual_scope':'File/format/decode checks only. See browser-qa.json for real playback functionality; subjective listening and owner preference remain separate.'}
    (ROOT/'evaluation/technical-checks.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({'passed':not failures,'check_count':len(checks),'failures':failures},ensure_ascii=False,indent=2))
    raise SystemExit(bool(failures))


if __name__=='__main__':main()
