# Media licenses and provenance

## Coffee footage and frames: CC BY-SA 4.0

- Title: **Pour Over** (2017).
- Author: **Lev Lazinskiy**.
- Source: https://commons.wikimedia.org/wiki/File:Pour_Over.ogv
- License: https://creativecommons.org/licenses/by-sa/4.0/
- Source file retrieved 2026-10-15 from Wikimedia Commons. License metadata verified through the Commons API.
- `demos/assets/coffee-source.mp4`: silent, resized/re-encoded adaptation. Original music **removed**; not redistributed in this repository.
- `demos/assets/coffee-01.jpg` through `coffee-04.jpg`: frames extracted at 6, 18, 34 and 49 seconds.
- Both `demos/video/*/video.mp4`, their posters, and frontend screenshots incorporating these images are adaptations distributed under **CC BY-SA 4.0**, not MIT. Video edits include cropping, sequencing, typography and newly synthesized sound.
- No association with or endorsement of the fictional CHONG CHA cafe is implied.

## Original material

Skill instructions, source code, fictional cafe copy, original synthesized instrumental music and motion typography are created for this repository and distributed under MIT unless identified above. System fonts are used locally for rendering and are **not** included.

## Shared narration

`demos/assets/narration.txt` is original fictional demo copy. The distributed `narration.wav` is generated **locally with eSpeak NG's Thai formant synthesizer**, using no prerecorded voice, outside speech service or third-party song. Original text and generated speech fixture are offered under MIT. It is a deliberately synthetic comparison voice, not a recording of the owner or owner-approved narration quality.

The generator is [scripts/make_narration.py](scripts/make_narration.py). Engine: eSpeak NG via espeakng-loader 0.2.4. Engine/data are GPL-3.0 and **not bundled**. Engine source/license: https://github.com/espeak-ng/espeak-ng and https://github.com/espeak-ng/espeak-ng/blob/master/COPYING . GPL-3 section 2 distinguishes program output from the program itself; the output here is newly synthesized original text, not copied engine code or a prerecorded voice. Runtime/library and generated-file hashes are in [narration provenance](evaluation/narration-provenance.json).

An earlier development-only speech fixture from a public speech service was replaced during release review because redistribution permission was not established. **That audio and the mixes containing it are not published.** Both public mixes were rebuilt with the same local replacement, keeping each original instrumental byte-identical and matching the four phrase windows. This intervention is recorded in the input-lock history and reproducibility report; it is not concealed as an unchanged frozen input.

## References, not bundled assets

REA (https://github.com/morluto/rea), MIT: informed evidence-first investigation and the optional REA routing guide. No REA source or binaries are bundled. Existing installed design/media skills were inspected to avoid duplicating or conflicting with their responsibilities; no third-party skill library is copied into this package.
