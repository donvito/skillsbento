#!/usr/bin/env python3
"""Download free stock media by id (no API key needed: the CDNs are open, the websites/APIs are not).

  stock.py pexels-photo <id> <out.jpg> [--w 2200]
  stock.py pexels-video <id> <out.mp4>            # probes the hd/uhd fps filename patterns
  stock.py unsplash <photo-1490806843957-31f4c9a91c65> <out.jpg>   # images.unsplash.com id, NOT the page slug

Find ids with WebSearch (allowed_domains ["pexels.com"] or ["unsplash.com"]): pexels.com/photo/<slug>-<ID>/,
pexels.com/video/<slug>-<ID>/. Unsplash page slugs can't be downloaded without auth; avoid Unsplash+ (paid)
results. Always LOOK at a contact sheet of what you downloaded: titles lie (a "BGC skyline" was another city).
Log every id in output/stock-credits.txt.
"""
import subprocess, sys
kind, ident, out = sys.argv[1:4]; w = sys.argv[sys.argv.index('--w') + 1] if '--w' in sys.argv else '2200'
def get(url, dest):
    r = subprocess.run(['curl', '-s', '-L', '-m', '120', '-o', dest, '-w', '%{http_code} %{content_type}', url], capture_output=True, text=True).stdout
    return r.startswith('200') and ('image' in r or 'video' in r)
if kind == 'pexels-photo':
    ok = get(f'https://images.pexels.com/photos/{ident}/pexels-photo-{ident}.jpeg?auto=compress&cs=tinysrgb&w={w}', out)
elif kind == 'unsplash':
    ok = get(f'https://images.unsplash.com/{ident}?w={w}&q=85&fm=jpg', out)
elif kind == 'pexels-video':
    ok = False
    for res in ['hd_1920_1080', 'uhd_2560_1440', 'uhd_3840_2160']:
        for fps in ['30', '25', '24', '60', '50', '29.97', '23.98']:
            url = f'https://videos.pexels.com/video-files/{ident}/{ident}-{res}_{fps}fps.mp4'
            c = subprocess.run(['curl', '-s', '-m', '15', '-r', '0-100', '-o', '/dev/null', '-w', '%{http_code}', url], capture_output=True, text=True).stdout
            if c in ('200', '206'): ok = get(url, out); break
        if ok: break
else: sys.exit(__doc__)
print(('ok ' if ok else 'FAILED ') + out); sys.exit(0 if ok else 1)
