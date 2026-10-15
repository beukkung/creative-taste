> Release integration note: the shared narration was replaced with locally synthesized eSpeak NG after worker production. Instrumental music.wav is byte-identical; public mix.wav and audio checks were regenerated. Metrics/prose below describe the original worker stage unless stated otherwise; see evaluation/reproducibility.json and final technical checks.

# A little room in the morning

The governing relationship is **voice in front, music answering in the spaces**. A close, warm plucked-key sound carries a small falling-third/rising-second vocabulary. Sustained inner voices move gently beneath it. The speech remains at its original gain and timing.

## Composition

The original score is 72 BPM in D major: six measures of 4/4 fit exactly twenty seconds. Dmaj9 moves through F#m7/C#, Bm9, Gmaj9, Em9 and A13 before landing on D6/9 at 16.667 seconds. Common tones and small inner-voice movements connect the chords; the final added sixth keeps the resolution hopeful and open.

The supplied Thai narration speaks at approximately 0–3.4, 3.9–7.9, 8.7–11.2 and 11.6–14.2 seconds. Its text describes taking time to pour water and enjoy the coffee aroma. The upper motif therefore stays small during the opening sentence, answers in the gaps around 3.5, 8.1 and 11.3 seconds, and expands after the last phrase. The ending resolves the motif to D after a final F#–E descent. Its last attack is at 17.8 seconds, leaving more than two seconds for the note and room tail.

The synthetic plucked key uses stretched, independently decaying sine partials and a softened attack. It is an invented instrument, not a recording of an acoustic piano. A restrained sine-rich pad, round low plucks and quiet band-limited sand-like pulses provide depth and movement. No prerecorded music, downloaded samples, named-artist imitation, online generation or purchases were used.

## Arrangement and mix

The motif sits slightly right, broken inner voices span the center, and the bass stays centered. Short cross-channel room reflections create intimacy without an extended wash. The lowpass treatment keeps sustained harmony away from the speech presence region. The pulse stops before the cadence, so the ending has space to breathe.

`music.wav` is the standalone composition. For `mix.wav`, only the music changes gain: about 0.23 during speech and 0.38 in its gaps, with smoothed movement. Speech stays at unity gain and its original sample positions. Measured across active speech, the bed is 11.69 dB below the voice in RMS. Both files end at exactly 20.000 seconds with zero-valued boundary samples. The final 1.85-second taper shapes the decay after the completed cadence.

## Verification and evidence

- Both exports are 960,000 frames, 48 kHz, stereo, 16-bit PCM WAV; all samples are finite and neither export clips.
- FFmpeg EBU R128: standalone music −17.9 LUFS, −4.1 dB true peak; narration mix −19.5 LUFS, −4.5 dB true peak.
- The standalone mono fold-down loses 0.13 dB RMS; stereo correlation is 0.940. The mix mono fold-down loses 0.02 dB.
- Music first and last samples are zero. The final 100 ms RMS is 0.000155 (about −76.2 dBFS).
- The source narration SHA-256 is preserved in `audio-checks.json`; the source recording was read but never modified.
- **Actual listening did not happen.** Verification used PCM inspection, speech-envelope inspection, NumPy measurements and FFmpeg loudness analysis. Emotional balance, timbre and perceived masking remain unverified by listening. The exported WAVs are ready for playback.

## Reproduce

From this directory, after placement in the package:

```powershell
python compose.py --narration ../../assets/narration.wav
```

Alternatively pass explicit `--narration` and `--out` paths. Omitting a nonexistent narration path renders the standalone composition and skips the mix. Dependencies are the installed NumPy and Python standard library; installed FFmpeg supplies the optional loudness report. Synthesis uses a fixed random seed.

One implementation and one repair pass were used. The first render stalled while importing the installed `scipy.signal`; an independent import probe confirmed the same stall. The repair replaced SciPy with NumPy frequency-domain filtering, moving averages and oversampled FFT peak inspection. The two task-owned stalled processes were stopped. Rendering then completed in about six seconds. No other condition outputs or evaluation notes were read.
