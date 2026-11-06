#!/bin/bash
# Light voice clean-up that keeps the timeline (so transcript times stay valid).
#   enhance_voice.sh <in.wav> <out.wav> [--denoise]
# Default: rumble high-pass, mild FFT denoise, presence EQ, de-ess, gentle compression, -16 LUFS.
# --denoise adds hum notches + stronger broadband reduction (users may find it too processed; offer A/B clips).
# Best quality is usually the user's own pass through Adobe Podcast "Enhance": edit first, export the edited
# track, let them enhance it, then just normalise it with finalize_audio.py.
set -e
in="$1"; out="$2"; extra=""
[ "$3" = "--denoise" ] && extra="bandreject=f=50:w=4,bandreject=f=60:w=4,bandreject=f=120:w=6,afftdn=nr=18:nf=-48:tn=1,"
ffmpeg -y -loglevel error -i "$in" -af "highpass=f=75,${extra}afftdn=nr=10:nf=-50:tn=1,equalizer=f=200:t=q:w=1:g=-1.5,equalizer=f=3500:t=q:w=1.2:g=2.5,equalizer=f=11000:t=h:w=1:g=1.5,deesser=i=0.35,acompressor=threshold=-24dB:ratio=3:attack=8:release=120:makeup=4,loudnorm=I=-16:TP=-1.5:LRA=7" -ar 48000 -ac 2 "$out"
echo "$out"
