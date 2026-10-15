> Release integration note: the shared narration was replaced with locally synthesized eSpeak NG after worker production. Instrumental music.wav is byte-identical; public mix.wav and audio checks were regenerated. Metrics/prose below describe the original worker stage unless stated otherwise; see evaluation/reproducibility.json and final technical checks.

# Slow morning — original coffee voiceover bed

## Composition

The composition lasts exactly 20.000 seconds: six bars of 4/4 at 72 BPM. Its home key is D major. The bass moves D–B–G–A–D–D while the upper voices retain common tones; extended chords add intimacy and the dominant-to-tonic movement makes the close feel hopeful. The final chord begins at 16.667 seconds, leaving more than three seconds to settle.

All instruments are synthesized mathematically in `compose.py`; no recordings, musical samples, online services, named-artist references, or paid APIs were used. A soft struck-tine keyboard supplies the harmony. A quieter nylon-like pluck plays a sparse motif, with a low sine bass, a very soft hand pulse, filtered brush noise, and a slow pad. These descriptions refer to synthesized timbres rather than recordings of physical instruments.

## Mix

The melodic material leaves rests and the accompaniment avoids bright hats or dense midrange activity. The bass is centered, chord voices are distributed gently across stereo, and quiet crossed room taps supply depth. A high-pass filter removes subsonic energy and a low-pass filter softens the top. The standalone bed targets -23.5 dBFS RMS with preserved dynamics. This is an RMS target, not a LUFS claim.

The closing tonic is part of the composition; a smooth 1.55-second release then brings its remaining tail to zero at the file boundary. The opening uses a short ramp to prevent a boundary click.

If the common narration is supplied, the script preserves the source file, reads it into memory, centers it, and adjusts only its overall playback gain. The bed sits 3.5–7.5 dB below its standalone level, with a smoothed look-ahead envelope providing greater reduction during speech. This prevents abrupt pumping and gives Thai consonants space. The mixed output remains exactly 20 seconds. Narration longer than 20 seconds is rejected rather than truncated.

## Reproduction

Use Python 3 with installed NumPy (FFmpeg is needed only if narration requires resampling):

```powershell
python compose.py --output . --narration ../../assets/narration.wav
```

Paths default to the source file's directory. In the delivered `demos/music/before/` location, the default narration path resolves to the shared `demos/assets/narration.wav`. Random synthesis details and PCM dither use seed 16872.

## Verification and limitations

Both files were verified as 48 kHz stereo 16-bit integer PCM, 960,000 frames, exactly 20.000 seconds. The floating-point synthesis has no nonfinite or clipped samples. FFmpeg measured the exported music at -21.3 LUFS integrated and -6.6 dBTP; the narration mix measured -17.8 LUFS and -3.2 dBTP. Stereo correlations before PCM quantization are 0.985 (music) and 0.998 (mix), consistent with restrained stereo width and centered speech. The final 10 ms of the synthesized bed is below -134 dBFS before dither. The common recording's last sample above -50 dBFS occurs at 14.225 seconds, and its final 100 ms is silent, so the mix does not cut off the supplied speech waveform. Semantic completeness and natural speech delivery were not verified by listening.

One repair pass was used. The initial render stalled while importing `scipy.signal`; an isolated import probe confirmed the same behavior. Only this task's two stalled Python processes were stopped. Filtering was replaced with zero-padded NumPy FFT filtering, speech-envelope smoothing with a cumulative moving average, and optional narration resampling with FFmpeg. The successful render then completed in about 3.5 seconds. No musical redesign was made in the repair pass.

Actual auditory listening has not happened: this environment provides no confirmed audio playback-to-model listening route. Objective waveform and file checks do not establish subjective sound quality, naturalness of synthetic speech, or the musical balance as heard by a person. No comparison with other conditions was performed.

Skills actually read: none. The task-specific brief and installed NumPy/FFmpeg tools were used directly. Production began at 2026-10-15 05:31:11 UTC; final artifact/metadata verification ended at the UTC time recorded in `run.json`. One initial implementation and one verification/repair pass were used.
