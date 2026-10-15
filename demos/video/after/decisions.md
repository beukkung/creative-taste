# A small coffee ritual — after

Direction: brewing changes the image more than graphics do. A single large image aperture leads, while Thai phrases sit quietly above it. The fine copper progress line connects the slow preparations with the final drink.

Footage was inspected at two-second source intervals plus targeted crop samples. The supplied clip is landscape 960×540 and includes original edits, a brief color effect and end credits. Crop x=270, width=600, full height=540 preserves the kettle, filter rim and glass, then scales to 720×648 within the vertical composition. This gives the action room without sacrificing its outer edges to a full-height vertical crop.

Final source-to-edit map:

| Edit | Source seconds | Observed action |
|---|---|---|
| 0–4 | 5–9 | Kettle, the preparation pause |
| 4–8 | 18–22 | Grounds in the paper filter |
| 8–13 | 35–40 | Brewing/pouring activity in filter |
| 13–16 | 46–49 | Bloom and bubbles |
| 16–20 | 53–57 | Finished dark coffee in glass |

Copy: ก่อนวันจะเริ่ม across preparation; ค่อย ๆ เท during the pour; ค่อย ๆ ตื่น during bloom; ชงช้า across the four-second ending. Text is shaped by HarfBuzz and rendered with FreeType/Tahoma. The brand is fictional; no venue is named or implied.

Sound: generated from seeded noise, a very low 73.42Hz tone and two decaying glass-like resonances, using NumPy. The broad low-pass air texture rises with the brew then falls away. No third-party music or original source audio is present. Unencoded peak is about −15.2dBFS and RMS about −42.7dBFS. These are measurements, not listening evidence. AAC stereo 48kHz is included.

Credits: supplied `../../assets/coffee-source.mp4`; its own end slate identifies © 2017 LEV LAZINSKIY. No external license assertion is made here. The supplied original audio was removed before this task; no original music was reused. Attribution stays in this file.

Verification: final poster, final frame, source crop sheet and twelve exported timepoints including every cut were viewed; Thai marks and the complete filter/glass were inspected. FFprobe confirms H.264 yuv420p, 720×1280, 24fps, 480 frames and exactly 20.000s; a complete FFmpeg decode passed without errors. Full uninterrupted playback and listening were not performed.

Repair accounting: initial verification exposed source end credits near the ending. The first repair shortened the source range, and reinspection exposed an internal source glass cut before the bloom beat. The second correction shortened the pour range and gave the preparation one additional second. Thus two repair cycles were used, one beyond the requested pass budget; no further iteration was performed. A stalled SciPy import had already been replaced with NumPy FFT filtering before the initial video render.

Reproduce with `python source.py`. The source uses `../../assets/coffee-source.mp4` in final demos/video/after placement; its fallback supports this assigned production workspace. Dependencies and shared-session timing limits appear in run.json. System fonts are not redistributed.
