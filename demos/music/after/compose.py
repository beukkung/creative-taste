"""Original 20-second coffee bed, deterministic synthesis only.
Run: python compose.py [--narration ../../assets/narration.wav] [--out .]
Dependencies: numpy; optional FFmpeg for loudness reports.
"""
from pathlib import Path
import argparse, hashlib, json, subprocess, wave
import numpy as np

SR = 48000
N = SR * 20
RNG = np.random.default_rng(315)

def frequency(midi):
    return 440 * 2 ** ((midi-69)/12)

def lowpass(x, hz):
    # Zero-padded frequency-domain smooth lowpass; avoids optional DSP imports.
    count=len(x); size=1 << (2*count-1).bit_length()
    frequencies=np.fft.rfftfreq(size,1/SR)
    transfer=1/np.sqrt(1+(frequencies/hz)**4)
    if x.ndim==2:transfer=transfer[:,None]
    return np.fft.irfft(np.fft.rfft(x,n=size,axis=0)*transfer,n=size,axis=0)[:count]

def smooth(x, samples):
    total=np.concatenate(([0.],np.cumsum(np.pad(x,(samples//2,samples-samples//2-1),mode='edge'))))
    return (total[samples:]-total[:-samples])/samples

def pan(x, position):
    angle = (position+1)*np.pi/4
    return x[:,None] * np.array([np.cos(angle), np.sin(angle)])

def key(midi, duration, velocity=1):
    """A felt-like synthesized plucked key; no sampled instrument."""
    t = np.arange(round(duration*SR))/SR
    f = frequency(midi)
    y = np.zeros(len(t))
    for harmonic, amp, decay in [(1,1,2.1),(2,.30,1.1),(3,.11,.58),(4,.045,.28),(6,.018,.12)]:
        # Slight stretched partials imply a small resonant physical object.
        y += amp*np.sin(2*np.pi*f*harmonic*(1+0.00013*(harmonic-1)**2)*t)*np.exp(-t/decay)
    y *= (1-np.exp(-t/.006)) * velocity
    y *= np.minimum(1,np.maximum(0,(duration-t)/.12))
    return y*.24

def pad(midi, duration):
    t = np.arange(round(duration*SR))/SR
    f = frequency(midi)
    y = (.72*np.sin(2*np.pi*f*t+.004*np.sin(2*np.pi*.27*t))+
         .18*np.sin(2*np.pi*f*2*t)+.06*np.sin(2*np.pi*f*3*t))
    env = np.minimum(t/.60,1)*np.minimum(np.maximum((duration-t)/1.30,0),1)
    return y*env*.045

def bass(midi,duration):
    t=np.arange(round(duration*SR))/SR
    y=np.sin(2*np.pi*frequency(midi)*t)+.17*np.sin(4*np.pi*frequency(midi)*t)
    env=(1-np.exp(-t/.025))*np.exp(-t/1.15)*np.minimum(1,(duration-t)/.12)
    return y*env*.22

def write_wav(path, audio):
    with wave.open(str(path),'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR)
        w.writeframes(np.round(np.clip(audio,-1,1)*32767).astype('<i2').tobytes())

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=Path(__file__).parent)
    parser.add_argument('--narration',type=Path,default=Path(__file__).parent/'../../assets/narration.wav')
    args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    keys=np.zeros((N,2)); harmony=np.zeros((N,2)); bottom=np.zeros((N,2)); brush=np.zeros((N,2))
    events=[]
    def add(track, sound, start, position=0):
        i=round(start*SR);j=min(N,i+len(sound))
        if j>i: track[i:j]+=pan(sound[:j-i],position)
    # 72 BPM, six 4/4 measures. The last measure is a sustained tonic landing.
    bar=10/3
    chords=[(0,[50,57,61,64,69],38), (bar,[49,57,61,64,68],37),
            (2*bar,[47,54,57,61,66],35),(3*bar,[43,54,57,62,66],31),
            (4*bar,[52,55,59,62,66],40),(15,[45,55,59,61,66],33),
            (5*bar,[50,57,59,64,66],38)]
    for index,(start,notes,root) in enumerate(chords):
        end=chords[index+1][0] if index+1<len(chords) else 19.8
        for j,note in enumerate(notes):
            add(harmony,pad(note,end-start+1.2),start,(-.68+j*.34))
        add(bottom,bass(root,min(end-start+.4,3.8)),start+.035,0)
        # Sparse broken inner voices, separate from the upper motif.
        for j,note in enumerate(notes[1:4]):
            add(keys,key(note,2.5,.15 if start<14.2 else .23),start+.25+j*.24,(-.38+j*.35))
    # A small falling third / rising second signature, placed in speech gaps.
    motif=[(.22,78,.28),(.72,76,.20),(3.48,78,.39),(3.77,74,.31),
           (8.08,78,.37),(8.38,76,.28),(11.27,74,.25),
           (14.45,78,.48),(14.87,76,.36),(15.29,74,.43),(15.91,76,.30),
           (16.76,78,.43),(17.38,76,.32),(17.80,74,.47)]
    for start,note,vel in motif:
        add(keys,key(note,min(2.7,19.85-start),vel),start,.19)
        events.append({'time_seconds':start,'midi':note,'velocity':vel,'role':'motif'})
    # Low, sand-like half-time motion. No snare or bright hat above consonants.
    for beat in range(1,19):
        start=beat*(5/6)+.05
        if start>15.6:break
        t=np.arange(int(.13*SR))/SR
        noise=lowpass(RNG.normal(0,1,len(t)),2400)
        noise-=lowpass(noise,700)
        noise*=np.exp(-t/.029)*(1-np.exp(-t/.004))*.016*(.65 if beat%2 else 1)
        add(brush,noise,start,-.35 if beat%2 else .35)
    # Timbre, rather than only level, creates space in the speech presence band.
    keys=lowpass(keys,3400);harmony=lowpass(harmony,1800)
    dry=keys+harmony+bottom+brush
    room=np.zeros_like(dry)
    for delay,gain in [(.073,.16),(.113,.12),(.181,.08),(.263,.05),(.367,.03)]:
        offset=round(delay*SR)
        room[offset:]+=lowpass(dry[:-offset,::-1],2300)*gain
    music=dry+room
    # Full musical cadence at 16.67, then decay. Boundary fade only shapes tail.
    music*=np.minimum(np.arange(N)/(.025*SR),1)[:,None]
    tail=np.ones(N);tail[int(18.15*SR):]=np.cos(np.linspace(0,np.pi/2,N-int(18.15*SR)))**2
    music*=tail[:,None]
    music*=.105/np.sqrt(np.mean(music**2))
    write_wav(args.out/'music.wav',music)
    checks={'composition':{'duration_seconds':20,'tempo_bpm':72,'meter':'4/4','bars':6,'tonic':'D major','motif_events':events},'source':'Original deterministic additive/subtractive synthesis; no prerecorded music.'}
    voice=None
    if args.narration.exists():
        source=args.narration.read_bytes()
        with wave.open(str(args.narration),'rb') as w:
            if w.getframerate()!=SR or w.getsampwidth()!=2 or w.getnchannels()!=2 or w.getnframes()!=N:
                raise ValueError('Narration must be exact 20 second 48k stereo PCM16; source is never modified.')
            voice=np.frombuffer(w.readframes(N),'<i2').reshape(-1,2).astype(float)/32768
        envelope=np.sqrt(smooth(np.mean(voice**2,axis=1),4800).clip(0))
        # Duck only music: voice samples keep unity gain and exact original timing.
        activity=np.clip((envelope-.003)/.022,0,1)
        duck=smooth(activity,12000)
        bed=music*(.38-.15*duck[:,None])
        mix=voice+bed
        if np.max(np.abs(mix))>=.98:raise ValueError('Mix headroom exceeded; repair arrangement gain, never voice.')
        write_wav(args.out/'mix.wav',mix)
        checks['narration']={'sha256':hashlib.sha256(source).hexdigest(),'gain':1.0,'timing_shift_samples':0,'unchanged_input':True,'speech_windows_seconds':[[0,3.4],[3.9,7.9],[8.7,11.2],[11.6,14.2]],'music_gain_active_speech':.23,'music_gain_gaps':.38}
    for filename in ['music.wav','mix.wav']:
        path=args.out/filename
        if not path.exists():continue
        with wave.open(str(path),'rb') as w:
            data=np.frombuffer(w.readframes(w.getnframes()),'<i2').reshape(-1,2)/32768
            spec={'sample_rate':w.getframerate(),'channels':w.getnchannels(),'sample_width_bytes':w.getsampwidth(),'frames':w.getnframes(),'duration_seconds':w.getnframes()/w.getframerate()}
        peak=float(np.max(np.abs(data))); rms=float(np.sqrt(np.mean(data**2)))
        over=np.fft.irfft(np.fft.rfft(data,axis=0),n=4*len(data),axis=0)*4
        mono=data.mean(axis=1)
        spec.update(finite=bool(np.isfinite(data).all()),peak_dbfs=float(20*np.log10(peak+1e-15)),true_peak_4x_dbfs=float(20*np.log10(np.max(np.abs(over))+1e-15)),rms_dbfs=float(20*np.log10(rms+1e-15)),clipped_samples=int(np.sum(np.abs(data)>=32767/32768)),stereo_correlation=float(np.corrcoef(data.T)[0,1]),mono_vs_stereo_rms_db=float(20*np.log10(np.sqrt(np.mean(mono**2))/rms)),first_sample=data[0].tolist(),last_sample=data[-1].tolist(),last_100ms_rms=float(np.sqrt(np.mean(data[-4800:]**2))))
        try:
            result=subprocess.run(['ffmpeg','-hide_banner','-i',str(path),'-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True)
            spec['ffmpeg_ebur128_summary']=result.stderr[result.stderr.rfind('Summary:'):].strip()
        except FileNotFoundError:spec['ffmpeg_ebur128_summary']='FFmpeg unavailable'
        checks[filename]=spec
    (args.out/'audio-checks.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in checks.items() if k.endswith('.wav')},indent=2))

if __name__=='__main__':main()
