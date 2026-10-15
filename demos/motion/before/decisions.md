# Quiet coffee — motion

The three phrases arrive in their required order. A cream paper field, espresso-colored Tahoma and a hairline cup rim give the eye a steady place to rest. The moving point traces one slow circuit; text enters with a small upward settle and leaves with a short dissolve. There is no sound.

The middle phrase wraps after ให้กาแฟ, preserving its copy and reading order. Thai is shaped by HarfBuzz, including above/below marks, then rasterized by FreeType. Font is read from Windows, not redistributed.

## Build

`python source.py` (or `python -S source.py` to bypass unrelated local Python startup hooks). Requires installed Pillow, numpy, uharfbuzz, freetype-py and FFmpeg on PATH. Outputs beside source.

## Verification

Inspected the rendered contact sheet at 1.00, 3.42 and 6.50 seconds, plus the final-size poster and Thai mark crop. Thai copy and marks are intact, text fits comfortably and the final brand is legible. FFprobe: H.264 yuv420p, 720×1280, 24 fps, 192 frames, 8.000 seconds, no audio. No full playback occurred. No repair needed.

Timing in run.json is a lower bound from the first recorded working-directory creation. Initial brief reading and tool discovery preceded that timestamp, so full task start is unknown. Render timing is recorded separately.
