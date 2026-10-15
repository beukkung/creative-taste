"""Original 20-second coffee bed. Python 3 + numpy; no sampled instruments.

python compose.py --output . --narration ../../assets/narration.wav
All defaults are relative to this source file, never the working directory.
"""
from pathlib import Path
import argparse
import json
import wave
import numpy as np

SR = 48000
DURATION = 20.0
N = int(SR * DURATION)
BEAT = 60 / 72
RNG = np.random.default_rng(16872)


def hz(note):
    return 440 * 2 ** ((note - 69) / 12)


def lowpass(x, cutoff):
    # Zero-padded, zero-phase two-pole spectral filter, implemented without SciPy imports.
    size = 1 << (2*len(x)-1).bit_length()
    f = np.fft.rfftfreq(size,1/SR)
    response = 1/np.sqrt(1+(f/cutoff)**4)
    if x.ndim==2:
        response=response[:,None]
    return np.fft.irfft(np.fft.rfft(x,n=size,axis=0)*response,n=size,axis=0)[:len(x)]


def key(note, length, velocity=1):
    t = np.arange(int(length * SR)) / SR
    f = hz(note)
    # Soft struck tine: rounded attack, fundamental bloom, short felt upper modes.
    attack = 1 - np.exp(-t / .014)
    body = np.zeros_like(t)
    for k, weight in [(1, 1), (2, .30), (3, .12), (4, .045), (6, .012)]:
        decay = 1.55 / (k ** .58)
        body += weight * np.sin(2*np.pi*f*k*(1 + .00003*k*k)*t) * np.exp(-t/decay)
    body += .12 * np.sin(2*np.pi*f*1.0014*t) * np.exp(-t/1.6)
    return body * attack * np.minimum(1, np.maximum(0, (length-t)/.18)) * velocity


def pluck(note, length, velocity=1):
    t = np.arange(int(length*SR))/SR
    f = hz(note)
    y = np.zeros_like(t)
    for k in range(1, 9):
        y += np.cos(2*np.pi*f*k*(1+.000018*k*k)*t + .15*k) * np.exp(-t/(1.0/(k**.7))) / k**1.9
    y *= (1-np.exp(-t/.007)) * np.minimum(1, np.maximum(0,(length-t)/.12))
    return lowpass(y, 4200) * velocity


def bass(note, length):
    t = np.arange(int(length*SR))/SR
    y = np.sin(2*np.pi*hz(note)*t) + .14*np.sin(4*np.pi*hz(note)*t)
    return y * (1-np.exp(-t/.03))*np.exp(-t/1.1)*np.minimum(1,(length-t)/.2)


def place(track, sound, at, gain, pan=0):
    start = int(at*SR)
    if start >= N:
        return
    if start < 0:
        sound = sound[-start:]
        start = 0
    sound = sound[:N-start]
    track[start:start+len(sound),0] += sound*gain*np.sqrt((1-pan)/2)
    track[start:start+len(sound),1] += sound*gain*np.sqrt((1+pan)/2)


def space(x):
    # Quiet, asymmetric room taps; high frequencies die faster in the room.
    wet = np.zeros_like(x)
    dark = lowpass(x, 3400)
    for delay, level in [(.063,.12),(.097,.10),(.157,.073),(.229,.052),(.337,.035),(.481,.023),(.647,.012)]:
        d = int(delay*SR)
        wet[d:,0] += dark[:-d,1]*level
        wet[d:,1] += dark[:-d,0]*level*.94
    return x + wet


def write_wav(path, y):
    # Seeded triangular dither at the 16-bit quantization floor.
    noise = (RNG.random(y.shape)-RNG.random(y.shape))/65536
    pcm = np.round(np.clip(y+noise,-1,1)*32767).astype('<i2')
    with wave.open(str(path),'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def read_voice(path):
    with wave.open(str(path),'rb') as w:
        channels, width, rate = w.getnchannels(), w.getsampwidth(), w.getframerate()
        data = w.readframes(w.getnframes())
    if width == 2:
        y = np.frombuffer(data, '<i2').astype(float)/32768
    elif width == 3:
        b = np.frombuffer(data,np.uint8).reshape(-1,3)
        z = b[:,0].astype(np.int32) | (b[:,1].astype(np.int32)<<8) | (b[:,2].astype(np.int32)<<16)
        y = ((z ^ 0x800000)-0x800000)/8388608
    elif width == 4:
        y = np.frombuffer(data,'<i4').astype(float)/2147483648
    else:
        raise ValueError('Narration must be 16/24/32-bit integer PCM WAV')
    y = y.reshape(-1,channels).mean(axis=1)
    if rate != SR:
        # Common recording is 48 kHz. Other rates use FFmpeg for proper bandlimited resampling.
        import subprocess
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            converted=Path(tmp)/'voice.wav'
            subprocess.run(['ffmpeg','-v','error','-y','-i',str(path),'-ar',str(SR),'-ac','1','-c:a','pcm_s16le',str(converted)],check=True)
            return read_voice(converted)
    if len(y) > N:
        raise ValueError(f'Narration duration {len(y)/SR:.3f}s exceeds 20s; source was not cut.')
    voice_duration = len(y)/SR
    return np.pad(y,(0,N-len(y))), voice_duration


def checks(y):
    mono = y.mean(axis=1)
    return {'frames':len(y), 'sample_rate':SR, 'channels':2, 'duration_seconds':len(y)/SR,
            'sample_peak_dbfs':float(20*np.log10(np.max(np.abs(y))+1e-12)),
            'rms_dbfs':float(20*np.log10(np.sqrt(np.mean(y*y))+1e-12)),
            'stereo_correlation':float(np.corrcoef(y.T)[0,1]),
            'dc_offset':float(np.mean(y)),
            'first_10ms_peak':float(np.max(np.abs(y[:480]))),
            'last_10ms_peak':float(np.max(np.abs(y[-480:]))),
            'clipped_samples':int(np.sum(np.abs(y)>=1)),
            'finite':bool(np.isfinite(y).all())}


def compose():
    keys = np.zeros((N,2))
    strings = np.zeros_like(keys)
    low = np.zeros_like(keys)
    rhythm = np.zeros_like(keys)
    # Six bars, D major. Upper voices retain common notes as the bass changes.
    voicings = [[54,61,64,69],[54,57,61,66],[54,57,62,69],
                [52,57,59,64],[54,61,64,69],[54,59,62,64,69]]
    roots = [38,35,31,33,38,38]
    for bar, notes in enumerate(voicings):
        start = bar*4*BEAT
        # Slight rolled attack makes a human gesture without a busy arpeggio.
        for j,n in enumerate(notes):
            place(keys,key(n,3.1),start+.045*j,.115 if bar<5 else .10,(-.24+j*.14))
        place(low,bass(roots[bar],2.45),start+.012,.15)
        if bar < 5:
            for beat,n,g in [(1.45,notes[1]+12,.043),(2.55,notes[2]+12,.055),(3.25,notes[-1],.035)]:
                place(strings,pluck(n,1.65),start+beat*BEAT,g,-.38 if beat<2 else .38)
            # Soft hand pulse, deliberately no sibilant hat competing with Thai speech.
            for beat in [0,2]:
                t = np.arange(int(.19*SR))/SR
                pulse = np.sin(2*np.pi*(65*t+10*.028*(1-np.exp(-t/.028))))*np.exp(-t/.048)*(1-np.exp(-t/.004))
                place(rhythm,pulse,start+beat*BEAT,.030)
            for beat in [1,3]:
                noise = lowpass(RNG.standard_normal(int(.13*SR)),1800)
                t = np.arange(len(noise))/SR
                noise *= (1-np.exp(-t/.008))*np.exp(-t/.027)
                place(rhythm,noise,start+beat*BEAT+.015,.016,.18)
    # A restrained motif: D E F# / E C# B / A F# E D. Plenty of rests.
    melody=[(.55,74,.055),(1.45,76,.043),(2.15,78,.050),
            (5.10,76,.043),(6.02,73,.043),(8.15,71,.052),
            (11.35,69,.048),(13.80,66,.039),(15.10,64,.035),(16.78,62,.057)]
    for at,n,g in melody:
        place(strings,pluck(n,2.2),at,g,.23*np.sin(at))
    # Soft, slow pad behind the keys; low partials only, with a restrained stereo drift.
    pad = np.zeros_like(keys)
    for bar,notes in enumerate(voicings):
        at = bar*4*BEAT
        dur = min(4.1,DURATION-at)
        t=np.arange(int(dur*SR))/SR
        env=(1-np.exp(-t/.42))*np.exp(-t/3.0)*np.minimum(1,np.maximum(0,(dur-t)/.8))
        for j,n in enumerate(notes):
            f=hz(n)
            y=(np.sin(2*np.pi*f*t)+.11*np.sin(4*np.pi*f*t))*env
            place(pad,y,at,.009,-.5 if j%2 else .5)
    y = space(keys+strings)+low+rhythm+pad
    # Gentle tone shaping and a deliberately composed final decay (last chord at 16.667).
    y=y-lowpass(y,38)
    y=lowpass(y,10500)
    y *= np.minimum(1,np.arange(N)/(SR*.025))[:,None]
    release=np.ones(N)
    start=int(18.45*SR)
    release[start:]=np.cos(np.linspace(0,np.pi/2,N-start))**2
    y *= release[:,None]
    # Keep the standalone bed warm and dynamic, with speech-mix headroom.
    y *= 10**(-23.5/20)/np.sqrt(np.mean(y*y))
    return y


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--narration',type=Path,default=Path(__file__).resolve().parent/'../../assets/narration.wav')
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    y=compose()
    write_wav(args.output/'music.wav',y)
    report={'music':checks(y),'composition':{'tempo_bpm':72,'meter':'4/4','bars':6,'key':'D major','seed':16872},'narration_available':args.narration.exists()}
    if args.narration.exists():
        voice,vd=read_voice(args.narration)
        # Look-ahead speech envelope. Gain affects only the bed, leaving source voice intact.
        frame=480
        env=np.sqrt(np.mean(voice.reshape(-1,frame)**2,axis=1))
        active=env>.012
        control=np.repeat(active.astype(float),frame)
        window=14401
        padded=np.pad(control,(window//2,window//2))
        total=np.concatenate(([0.],np.cumsum(padded)))
        control=(total[window:]-total[:-window])/window
        control=np.clip(control*1.8,0,1)
        bedgain=10**((-3.5-4.0*control)/20)
        voicegain=min(10**(-3.5/20)/(np.max(np.abs(voice))+1e-9),2.0)
        mixed=y*bedgain[:,None]+voice[:,None]*voicegain
        if np.max(np.abs(mixed))>.96:
            mixed *= .96/np.max(np.abs(mixed))
        write_wav(args.output/'mix.wav',mixed)
        report['mix']=checks(mixed)
        report['narration_duration_seconds']=vd
        report['narration_gain_db']=float(20*np.log10(voicegain))
        report['bed_gain_db_range']=[-7.5,-3.5]
    (args.output/'audio_checks.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
