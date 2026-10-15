"""Make equal-loudness listening previews; preserve original WAV exports."""
from pathlib import Path
import datetime
import json
import subprocess

ROOT=Path(__file__).resolve().parent.parent


def measure(path):
    result=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',str(path),'-af','loudnorm=I=-22:TP=-2:LRA=7:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
    start=result.stderr.rfind('{')
    return json.JSONDecoder().raw_decode(result.stderr[start:])[0]


def main():
    report={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'constant gain, then identical MP3 codec/bitrate; original WAVs unchanged','files':[]}
    for condition in ['before','after']:
        folder=ROOT/'demos'/'music'/condition
        for name,target in [('music',-22.0),('mix',-20.0)]:
            source=folder/(name+'.wav'); dest=folder/(name+'-preview.mp3')
            measured=measure(source)
            gain=target-float(measured['input_i'])
            # Constant gain preserves arrangement and dynamics. Leave codec headroom.
            if float(measured['input_tp'])+gain > -2:
                raise ValueError('Preview gain would exceed headroom; do not silently limit')
            for attempt in range(3):
                subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(source),'-af',f'volume={gain:.3f}dB','-c:a','libmp3lame','-b:a','160k',str(dest)],check=True)
                final=measure(dest)
                error=target-float(final['input_i'])
                if abs(error)<=.15:
                    break
                gain+=error
            if abs(float(final['input_i'])-target)>.15:
                raise ValueError(f'Encoded preview loudness missed target: {final}')
            report['files'].append({'path':dest.relative_to(ROOT).as_posix(),'source_lufs':float(measured['input_i']),'gain_db':round(gain,3),'target_lufs':target,'preview_lufs':float(final['input_i']),'preview_true_peak_dbtp':float(final['input_tp'])})
    (ROOT/'evaluation'/'preview-loudness.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
