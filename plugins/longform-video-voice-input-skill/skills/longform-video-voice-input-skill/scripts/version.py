#!/usr/bin/env python3
"""Versioned builds: EVERY update to the rendered video becomes a new version. Never overwrite a delivered MP4.

  version.py init  <workdir> --slug ai-agents-101 --project video_v1 --audio work/voice_final.wav
  version.py new   <workdir> "what changed"          # snapshot current -> video_vN+1 (code copied, media + frames hard-linked)
  version.py build <workdir> [--from S --to S]... [--full] [--audio FILE] [--audio-only]
  version.py list  <workdir>

Layout it maintains:
  <workdir>/video_vN/            project for version N (index.html, *.js, media/ hard links, out/jframes hard links)
  <workdir>/output/<slug>-vN.mp4 the deliverable for version N (build refuses to overwrite it)
  <workdir>/CHANGELOG.md         one entry per version: date, note, what was re-rendered, audio used
  <workdir>/versions.json        state

Partial re-render: pass the changed time ranges (seconds, include ~0.5 s for transitions) with --from/--to; those
frames are unlinked in the NEW version only (previous versions keep theirs) and rendered again. --full re-renders
everything. --audio-only re-muxes the previous version's picture with new audio (still a new version).
"""
import argparse, datetime, json, os, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['init', 'new', 'build', 'list']); ap.add_argument('workdir'); ap.add_argument('note', nargs='?')
ap.add_argument('--slug'); ap.add_argument('--project'); ap.add_argument('--audio')
ap.add_argument('--from', dest='frm', type=float, action='append', default=[]); ap.add_argument('--to', type=float, action='append', default=[])
ap.add_argument('--full', action='store_true'); ap.add_argument('--audio-only', action='store_true'); ap.add_argument('--workers', type=int, default=8)
a = ap.parse_args(); wd = os.path.abspath(a.workdir); sp = os.path.join(wd, 'versions.json')
load = lambda: json.load(open(sp)); save = lambda s: json.dump(s, open(sp, 'w'), indent=1)
now = lambda: datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
def log(line): open(os.path.join(wd, 'CHANGELOG.md'), 'a').write(line + '\n')
def mp4(s, v): return os.path.join(wd, 'output', f"{s['slug']}-v{v}.mp4")
def hardlink_tree(src, dst):
    for root, dirs, files in os.walk(src):
        rel = os.path.relpath(root, src); os.makedirs(os.path.join(dst, rel), exist_ok=True)
        for f in files:
            t = os.path.join(dst, rel, f)
            if not os.path.exists(t): os.link(os.path.join(root, f), t)

if a.cmd == 'init':
    proj = os.path.join(wd, a.project or 'video_v1')
    if not os.path.isdir(proj): sys.exit(f'no project dir {proj}')
    s = {'slug': a.slug or os.path.basename(wd), 'current': 1, 'audio': a.audio, 'versions': [{'v': 1, 'dir': os.path.basename(proj), 'note': a.note or 'first version', 'date': now(), 'built': False}]}
    save(s); log(f"# {s['slug']} changelog\n\n## v1 — {now()}\n- {s['versions'][0]['note']}"); print('initialised v1 ->', proj)

elif a.cmd == 'new':
    if not a.note: sys.exit('give a short note of what changes in this version')
    s = load(); prev = s['versions'][-1]; v = prev['v'] + 1
    src = os.path.join(wd, prev['dir']); dst = os.path.join(wd, f'video_v{v}')
    if os.path.exists(dst): sys.exit(f'{dst} exists')
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns('out', 'media'))
    hardlink_tree(os.path.join(src, 'media'), os.path.join(dst, 'media'))
    if os.path.isdir(os.path.join(src, 'out', 'jframes')): hardlink_tree(os.path.join(src, 'out', 'jframes'), os.path.join(dst, 'out', 'jframes'))
    os.makedirs(os.path.join(dst, 'out'), exist_ok=True)
    s['versions'].append({'v': v, 'dir': os.path.basename(dst), 'note': a.note, 'date': now(), 'built': False}); s['current'] = v; save(s)
    log(f"\n## v{v} — {now()}\n- {a.note}"); print(f'v{v}: edit files in {dst}, then: version.py build {a.workdir} --from S --to S')

elif a.cmd == 'build':
    s = load(); cur = s['versions'][-1]; v = cur['v']; proj = os.path.join(wd, cur['dir']); out = mp4(s, v)
    if os.path.exists(out): sys.exit(f'{out} already exists. Every update is a new version: run `version.py new {a.workdir} "<what changed>"` first.')
    audio = os.path.abspath(a.audio) if a.audio else os.path.join(wd, s['audio']) if s.get('audio') else None
    if a.audio: s['audio'] = os.path.relpath(audio, wd)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if a.audio_only:
        prevmp4 = mp4(s, v - 1)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', prevmp4, '-i', audio, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-shortest', '-movflags', '+faststart', out], check=True)
        what = 'audio only (picture copied from v%d)' % (v - 1)
    else:
        fps = 30
        try:
            import re; m = re.search(r'fps:\s*(\d+)', open(os.path.join(proj, 'index.html')).read()); fps = int(m.group(1)) if m else 30
        except Exception: pass
        jf = os.path.join(proj, 'out', 'jframes')
        if a.full and os.path.isdir(jf): shutil.rmtree(jf)
        ranges = list(zip(a.frm, a.to))
        for s0, s1 in ranges:
            for i in range(int(s0 * fps), int(s1 * fps) + 1):
                p = os.path.join(jf, f'{i:05d}.jpg')
                if os.path.exists(p): os.remove(p)          # unlinks only this version's copy
        subprocess.run([sys.executable, os.path.join(HERE, 'render_frames.py'), proj, '--workers', str(a.workers)], check=True)
        cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(fps), '-i', os.path.join(jf, '%05d.jpg')]
        cmd += (['-i', audio, '-map', '0:v', '-map', '1:a', '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-shortest'] if audio else [])
        cmd += ['-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out]
        subprocess.run(cmd, check=True)
        what = 'full render' if a.full or not ranges else 're-rendered ' + ', '.join(f'{x:.1f}–{y:.1f}s' for x, y in ranges)
    cur['built'] = True; cur['mp4'] = os.path.relpath(out, wd); save(s)
    log(f"- built: {what}; audio: {s.get('audio')}\n- file: {os.path.relpath(out, wd)}")
    print(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration,size', '-of', 'default=nw=1', out], capture_output=True, text=True).stdout.strip()); print('built', out)

else:
    s = load()
    for x in s['versions']: print(f"v{x['v']}  {x['date']}  {'built' if x.get('built') else 'not built':9}  {x['dir']:12}  {x['note']}")
