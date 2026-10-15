"""Locally synthesize the original Thai test copy with eSpeak NG (no web service).

Requires espeakng-loader, or --engine-root pointing to its extracted package
directory. The engine is not bundled. Outputs speech, not a natural-voice claim.
"""
import argparse
import ctypes
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import tempfile
import wave

ROOT=Path(__file__).resolve().parent.parent
SEGMENTS=[(0.0,3.4,'บางเช้า เราไม่จำเป็นต้องรีบไปไหน'),(3.9,4.0,'แค่ค่อย ๆ เทน้ำ รอให้กลิ่นกาแฟลอยขึ้นมา'),(8.7,2.5,'แล้วให้เวลาตัวเองอีกสักนิด'),(11.6,2.6,'ชงช้า กาแฟดี ไม่ต้องรีบ')]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine-root',type=Path)
    args=parser.parse_args()
    if args.engine_root:
        module_path=args.engine_root/'__init__.py'
        spec=importlib.util.spec_from_file_location('local_espeak_loader',module_path)
        engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
    else:
        import espeakng_loader as engine
    text=(ROOT/'demos/assets/narration.txt').read_text(encoding='utf-8').strip()
    if re.sub(r'\s','',text)!=re.sub(r'\s','',''.join(s[2] for s in SEGMENTS)):
        raise ValueError('Original narration text changed; review segments rather than silently replacing it')
    lib=ctypes.CDLL(engine.get_library_path())
    lib.espeak_Initialize.argtypes=[ctypes.c_int,ctypes.c_int,ctypes.c_char_p,ctypes.c_int]
    lib.espeak_Initialize.restype=ctypes.c_int
    sr=lib.espeak_Initialize(2,0,str(engine.get_data_path()).encode(),0)
    if sr<=0:raise RuntimeError('eSpeak initialization failed')
    lib.espeak_SetVoiceByName.argtypes=[ctypes.c_char_p]
    if lib.espeak_SetVoiceByName(b'th')!=0:raise RuntimeError('Thai voice unavailable')
    lib.espeak_SetParameter(1,155,0)  # rate; local formant synthesis, no recording
    chunks=[]
    CALLBACK=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.POINTER(ctypes.c_short),ctypes.c_int,ctypes.c_void_p)
    @CALLBACK
    def callback(samples,count,events):
        if samples and count>0:chunks.append(ctypes.string_at(samples,count*2))
        return 0
    lib.espeak_SetSynthCallback.argtypes=[CALLBACK];lib.espeak_SetSynthCallback(callback)
    lib.espeak_Synth.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_uint,ctypes.c_int,ctypes.c_uint,ctypes.c_uint,ctypes.c_void_p,ctypes.c_void_p]
    result=bytearray(20*48000*4)
    import array
    records=[]
    with tempfile.TemporaryDirectory() as tmp:
        for i,(onset,duration,phrase) in enumerate(SEGMENTS):
            chunks.clear(); encoded=phrase.encode('utf-8')+b'\0'
            buf=ctypes.create_string_buffer(encoded)
            code=lib.espeak_Synth(buf,len(encoded),0,1,0,1,None,None)
            if code!=0:raise RuntimeError('Speech synthesis failed')
            raw=b''.join(chunks)
            if not raw:raise RuntimeError('No speech samples')
            wav=Path(tmp)/f'{i}.wav';converted=Path(tmp)/f'{i}-48k.wav'
            with wave.open(str(wav),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(raw)
            ratio=(len(raw)/2/sr)/duration
            factors=[]
            while ratio<.5:factors.append(.5);ratio/=.5
            while ratio>2:factors.append(2);ratio/=2
            factors.append(ratio)
            filters=','.join(f'atempo={v:.8f}' for v in factors)+',apad'
            subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(wav),'-af',filters,'-t',str(duration),'-ar','48000','-ac','2',str(converted)],check=True)
            with wave.open(str(converted),'rb') as w:data=array.array('h',w.readframes(w.getnframes()))
            # Consistent voice headroom and a tiny click-free boundary envelope.
            peak=max(abs(v) for v in data);gain=.45*32767/max(peak,1)
            frame_count=len(data)//2
            for n in range(frame_count):
                envelope=min(1,n/240,(frame_count-1-n)/240)
                data[2*n]=round(data[2*n]*gain*envelope);data[2*n+1]=round(data[2*n+1]*gain*envelope)
            start=round(onset*48000)*4;payload=data.tobytes();result[start:start+len(payload)]=payload
            records.append({'start':onset,'duration':duration,'text':phrase})
    destination=ROOT/'demos/assets/narration.wav'
    with wave.open(str(destination),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(48000);w.writeframes(result)
    info={'engine':'eSpeak NG via espeakng-loader 0.2.4','voice':'th (formant synthesis; no prerecorded voice)','engine_library_sha256':hashlib.sha256(Path(engine.get_library_path()).read_bytes()).hexdigest(),'text_sha256':hashlib.sha256(text.encode()).hexdigest(),'speech_sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),'frames':960000,'sample_rate':48000,'segments':records,'license':'Original narration text and synthesized comparison fixture MIT; engine GPL-3.0, not bundled'}
    (ROOT/'evaluation/narration-provenance.json').write_text(json.dumps(info,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({'status':'locally synthesized','seconds':20,'engine_rate':sr,'sha256':info['speech_sha256']}))


if __name__=='__main__':main()
