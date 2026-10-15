# A small coffee ritual — video

Warm paper margins frame a close view of brewing. The story proceeds from kettle and filter preparation to dry grounds, then the swirling bloom and the filled glass. The four Thai phrases establish a patient rhythm; ชงช้า resolves the final four seconds. The frame stays still to let the footage provide the movement. A copper progress rule and four small stage dots keep the visual rhythm restrained.

Only coffee-source.mp4 is used. The 960×540 original is scaled to 996×560 and center-cropped to 664×560 within a 720×1280 composition. This retains the dripper, water agitation and filled glass without pretending the footage was shot vertically. A slight warm grade connects its mixed lighting to the paper field. Filter preparation is slowed threefold; the final cup detail is slowed fourfold. Cuts remain clean, avoiding transitions that would obscure the brewing.

Thai text is shaped by HarfBuzz and rasterized with FreeType from Windows Tahoma. No font is redistributed. The brand is fictional; no venue or product claims are made.

## Original audio

A self-created sound bed uses low-amplitude sine tones, FFT-filtered seeded noise through the bloom, and short synthesized glass-like pings at phrase changes. No source audio or third-party music is used. Sample peak and RMS are in run.json. Audio was measured, not listened to; subjective listening remains unverified.

## Build

`python source.py --input ../../assets/coffee-source.mp4`

The default input is the relative shared source in the final demos/video/before destination. In this staging directory supply its actual path. Requires installed Pillow, numpy, uharfbuzz, freetype-py, FFmpeg. `python -S` bypasses unrelated local Python startup hooks. No downloads or external projects.

## Verification and one repair pass

Inspected the supplied-source contact sheets before selecting ranges. Inspected five rendered frames and targeted Thai text/image crops. The first verification revealed a bloom image during the brand hold; the single repair pass moved the last selection to the filled cup at 53.6–54.6s and padded fractional retiming tails by holding the last available frame. This avoids source credits and preserves exactly 480 frames. Final technical verification and full-frame/crop inspection are recorded in run.json. No full playback or subjective listening occurred.

## Credits

Footage supplied in demos/assets/coffee-source.mp4. Its embedded original end card credits © 2017 Lev Lazinskiy, with music credited to Just Watching by Podington Bear / soundofpicture.com. This edit uses the supplied silent picture only; none of that music is included. Attribution is retained here separately from the story. No claim of a real Thai venue.

Timing in run.json is a documented lower bound from the first working artifact timestamp; initial brief read/tool discovery preceded it. Render timing is recorded separately.
