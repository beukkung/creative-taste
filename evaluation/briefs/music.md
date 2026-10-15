# Voiceover music bed

Compose an original, polished 20.000-second instrumental for a Thai coffee voiceover. Mood: unhurried, intimate and hopeful; support speech, but remain engaging alone. No imitation of a named artist. No prerecorded music. The shared narration text is in demos/assets/narration.txt; use narration.wav if available. Both conditions get the same recording. Do not change that recording.

Deliver music.wav (48 kHz stereo PCM), an optional same-duration narration mix if the shared narration WAV is available, and runnable Python source. Use installed numpy/scipy and standard-library wave, with FFmpeg if useful. You may synthesize your own instruments. No extra dependencies, online generation or purchases. Export a musical ending rather than an accidental abrupt cut. Explain your composition and mix choices and state whether actual listening happened. Keep all file paths relative to the script or accept an output argument.

Production budget: one initial implementation and one verification/repair pass; target 15 minutes, stop by 20 minutes. Record actual elapsed time and repair passes. You may inspect your own output. Do not inspect other conditions' outputs. You may use existing tools and skills. Save source and decisions in the assigned directory.
