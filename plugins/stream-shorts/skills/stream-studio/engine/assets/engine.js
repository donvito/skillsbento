/* ==========================================================================
   motion-reel engine — deterministic canvas motion graphics.
   Everything is a pure function of time T (seconds): renderFrame(T) draws the
   exact frame, so rendering is parallel, seekable and reproducible.
   API reference: references/engine-api.md
   ========================================================================== */

/* ---------- config ---------- */
const CFG = Object.assign({
  w: 1920, h: 1080, fps: 60, duration: 30, bpm: 120,
  displayTracking: -0.03,        // em, applied to F.d in riseText/sliceText/fit
  shake: 9,                      // px of camera shake per unit of cue.shake
  vignette: 0.35,                // 0..1 edge darkening
  fadeIn: 0, fadeOut: 0.35,      // seconds, to/from black
  fontLoads: [],                 // e.g. ['600 100px "Inter Tight"'] — awaited before READY
  theme: {}, fonts: {}, hud: null, music: { mode: 'synth', style: 'energetic', mood: 'dark' },
}, window.REEL_CONFIG || {});
const W = CFG.w, H = CFG.h, FPS = CFG.fps, DUR = CFG.duration, BPM = CFG.bpm, BEAT = 60 / BPM;
const U = Math.min(W, H) / 1080;          // unit scale: design sizes at a 1080px short side, multiply by U
const PORTRAIT = H > W;
const M = Math.round((PORTRAIT ? 0.085 : 0.068) * W);   // safe side margin
const TH = Object.assign({
  bg: '#0a0a0a', fg: '#fafafa', muted: '#8f8f8f', dim: 'rgba(250,250,250,.58)',
  paper: '#f5f4f1', ink: '#0a0a0a', inkDim: 'rgba(10,10,10,.6)', elev: '#1c1b19',
  accent: '#fafafa', accentInk: '#0a0a0a', flash: '#ffffff',
}, CFG.theme);
const F = Object.assign({ d: 'Inter Tight', b: 'Inter Tight', m: 'JetBrains Mono' }, CFG.fonts);
const q = f => /^["']/.test(f) || !/\s/.test(f) ? f : `"${f}"`;
const FD = q(F.d), FB = q(F.b), FM = q(F.m);
const DT = CFG.displayTracking;

/* ---------- canvas ---------- */
const cv = document.getElementById('c') || document.body.appendChild(document.createElement('canvas'));
cv.width = W; cv.height = H;
const X = cv.getContext('2d');
function mk(w = W, h = H) { const c = document.createElement('canvas'); c.width = w; c.height = h; return c }
const BUF = [mk(), mk(), mk(), mk()];

/* ---------- math ---------- */
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, t) => a + (b - a) * t;
const P = (t, a, b) => clamp((t - a) / (b - a));          // progress of t through [a,b]
const E = {
  linear: t => t,
  outExpo: t => t >= 1 ? 1 : 1 - Math.pow(2, -10 * t),
  inExpo: t => t <= 0 ? 0 : Math.pow(2, 10 * t - 10),
  ioExpo: t => t <= 0 ? 0 : t >= 1 ? 1 : t < .5 ? Math.pow(2, 20 * t - 10) / 2 : (2 - Math.pow(2, -20 * t + 10)) / 2,
  outCubic: t => 1 - Math.pow(1 - t, 3),
  inCubic: t => t * t * t,
  ioCubic: t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2,
  outQuint: t => 1 - Math.pow(1 - t, 5),
  outBack: t => { if (t <= 0) return 0; const c1 = 1.9, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2) },
  outElastic: t => t <= 0 ? 0 : t >= 1 ? 1 : Math.pow(2, -10 * t) * Math.sin((t * 10 - .75) * (2 * Math.PI / 3)) + 1,
};
function rng(seed) { return function () { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296 } }
function hash(n) { const s = Math.sin(n * 127.1) * 43758.5453; return s - Math.floor(s) }
function noise1(x) { const i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f); return lerp(hash(i), hash(i + 1), u) * 2 - 1 }
const beats = n => n * BEAT, bars = n => n * 4 * BEAT;
const beatPulse = (T, k = 6) => Math.exp(-((T / BEAT) % 1) * k);   // 1 on each beat, decays

/* ---------- text & shapes ---------- */
const font = (w, s, f) => `${w} ${s}px ${f}`;
function bgFill(c, col) { c.fillStyle = col; c.fillRect(-W * .1, -H * .1, W * 1.2, H * 1.2) }
function txt(c, s, x, y, o = {}) {
  const a = o.alpha ?? 1; if (a <= .002 || !s) return;
  c.save(); c.font = o.font; c.fillStyle = o.color || TH.fg; c.textAlign = o.align || 'left'; c.textBaseline = o.base || 'alphabetic';
  const size = parseFloat(o.font.split(' ')[1]); c.letterSpacing = (o.ls ?? (o.track ? o.track * size : 0)) + 'px'; c.globalAlpha *= a;
  if (o.stroke) { c.strokeStyle = o.stroke; c.lineWidth = o.lw || 2; c.strokeText(s, x, y) } else c.fillText(s, x, y);
  c.restore();
}
function mw(c, s, f, ls = 0) { c.save(); c.font = f; c.letterSpacing = ls + 'px'; const w = c.measureText(s).width; c.restore(); return w }
const trackFor = (fam, size) => fam === FD ? size * DT : 0;
function fit(c, s, wt, fam, maxW, maxS) { return Math.min(maxS, 100 * maxW / mw(c, s, font(wt, 100, fam), trackFor(fam, 100))) }
/** letters rise from a mask, staggered. returns total width */
function riseText(c, s, x, y, size, wt, fam, color, t, t0, stag = .03, dur = .5, o = {}) {
  c.save(); c.font = font(wt, size, fam); c.letterSpacing = (o.ls ?? trackFor(fam, size)) + 'px';
  const gap = size * (o.wordGap ?? .07), total = c.measureText(s).width + (s.split(' ').length - 1) * gap; c.restore();
  if (t < t0) return total;
  c.save(); c.font = font(wt, size, fam); c.letterSpacing = (o.ls ?? trackFor(fam, size)) + 'px'; c.fillStyle = color; c.strokeStyle = color; c.lineWidth = o.lw || 3;
  const ox = o.align === 'center' ? x - total / 2 : o.align === 'right' ? x - total : x;
  c.beginPath(); c.rect(ox - size, y - size * 1.05, total + size * 2, size * 1.35); c.clip();
  for (let i = 0; i < s.length; i++) {
    const pre = s.slice(0, i), cx = ox + c.measureText(pre).width + (pre.split(' ').length - 1) * gap;
    const p = E.outExpo(P(t, t0 + i * stag, t0 + i * stag + dur)); if (p <= 0) continue;
    const dy = (1 - p) * size * 1.15;
    if (o.stroke) c.strokeText(s[i], cx, y + dy); else c.fillText(s[i], cx, y + dy);
  }
  c.restore(); return total;
}
function typeText(c, s, x, y, f, color, t, t0, cps, cursor = true, o = {}) {
  if (t < t0) return; const n = Math.floor(clamp((t - t0) * cps, 0, s.length)), str = s.slice(0, n);
  txt(c, str, x, y, { font: f, color, align: o.align, ls: o.ls });
  if (cursor && (n < s.length || Math.floor(t * 4) % 2 === 0)) { const sz = parseFloat(f.split(' ')[1]); c.fillStyle = color; c.fillRect(x + mw(c, str, f, o.ls || 0) + sz * .15, y - sz * .78, sz * .55, sz * .95) }
}
/** word slices in from alternating sides */
function sliceText(c, s, x, y, size, wt, fam, color, t, t0, n = 6, dist = W * .4, o = {}) {
  c.save(); c.font = font(wt, size, fam); c.letterSpacing = trackFor(fam, size) + 'px'; c.fillStyle = color; c.textAlign = o.align || 'left';
  const top = y - size * .78, hg = size * .8;
  for (let i = 0; i < n; i++) {
    const y0 = top + hg * i / n - (i === 0 ? size * .3 : 0), y1 = top + hg * (i + 1) / n + (i === n - 1 ? size * .3 : 0);
    const p = E.outExpo(P(t, t0 + i * .028, t0 + .55 + i * .028)); if (p <= 0) continue;
    c.save(); c.beginPath(); c.rect(-W, y0, W * 3, y1 - y0 + .6); c.clip(); c.globalAlpha = clamp(p * 2.5);
    c.fillText(s, x + (i % 2 ? 1 : -1) * dist * (1 - p), y); c.restore();
  }
  c.restore();
}
/** word-by-word rise, wraps to maxW. returns height used */
function wordsRise(c, s, x, y, size, wt, fam, color, t, t0, maxW, o = {}) {
  const f = font(wt, size, fam), lh = size * (o.lh || 1.12), words = s.split(' '), lines = [[]];
  let cur = 0; const sp = mw(c, ' ', f);
  for (const w of words) { const ww = mw(c, w, f, trackFor(fam, size)); if (cur + ww > maxW && lines[lines.length - 1].length) { lines.push([]); cur = 0 } lines[lines.length - 1].push([w, cur]); cur += ww + sp }
  let k = 0;
  lines.forEach((ln, li) => ln.forEach(([w, ox]) => { const st = t0 + k++ * (o.stag || .06); const p = E.outExpo(P(t, st, st + .45)); if (p <= 0) return;
    c.save(); c.beginPath(); c.rect(x + ox - size, y + li * lh - size * 1.05, mw(c, w, f) + size * 2, size * 1.35); c.clip();
    txt(c, w, x + ox, y + li * lh + (1 - p) * size * 1.1, { font: f, color, ls: trackFor(fam, size) }); c.restore() }));
  return lines.length * lh;
}
function pill(c, x, y, label, o = {}) {
  const f = o.font || font(600, 17 * U, FM), ls = o.ls ?? 2 * U, px = o.padX || 24 * U, h = o.h || 48 * U;
  const w = mw(c, label, f, ls) + px * 2; const p = o.p ?? 1; if (p <= 0) return w;
  c.save(); c.translate(x + w / 2, y); c.scale(p, p); c.beginPath(); c.roundRect(-w / 2, -h / 2, w, h, h / 2);
  if (o.bg) { c.fillStyle = o.bg; c.fill() } if (o.stroke) { c.strokeStyle = o.stroke; c.lineWidth = o.lw || 1.6 * U; c.stroke() }
  c.font = f; c.letterSpacing = ls + 'px'; c.fillStyle = o.fg || TH.fg; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(label, ls / 2, 1);
  c.restore(); return w;
}
function dotGrid(c, sp, col, alpha, ox = 0, oy = 0, r = 1.4) {
  if (alpha <= 0) return; c.save(); c.fillStyle = col; c.globalAlpha = alpha;
  for (let x = ((ox % sp) + sp) % sp - sp; x < W + sp; x += sp) for (let y = ((oy % sp) + sp) % sp - sp; y < H + sp; y += sp) c.fillRect(x - r, y - r, r * 2, r * 2);
  c.restore();
}
/** col like 'rgba(255,255,255,A)' — A is replaced by alpha */
function glow(c, x, y, r, col, a) { const g = c.createRadialGradient(x, y, 0, x, y, r); g.addColorStop(0, col.replace('A', a)); g.addColorStop(1, col.replace('A', 0)); c.fillStyle = g; c.fillRect(x - r, y - r, r * 2, r * 2) }
function star(c, x, y, ro, ri, n, rot, col) { c.save(); c.translate(x, y); c.rotate(rot); c.beginPath(); for (let i = 0; i < n * 2; i++) { const a = i * Math.PI / n, r = i % 2 ? ri : ro; c.lineTo(Math.cos(a) * r, Math.sin(a) * r) } c.closePath(); c.fillStyle = col; c.fill(); c.restore() }
function ringText(c, s, cx, cy, r, rot, f, col, a = 1) {
  if (a <= 0) return; c.save(); c.font = f; c.fillStyle = col; c.globalAlpha *= a; c.textAlign = 'center'; c.textBaseline = 'middle';
  for (let i = 0; i < s.length; i++) { const an = rot + i * 2 * Math.PI / s.length; c.save(); c.translate(cx + Math.cos(an) * r, cy + Math.sin(an) * r); c.rotate(an + Math.PI / 2); c.fillText(s[i], 0, 0); c.restore() }
  c.restore();
}
function qb(ax, ay, bx, by, cx, cy, u) { const v = 1 - u; return { x: v * v * ax + 2 * v * u * bx + u * u * cx, y: v * v * ay + 2 * v * u * by + u * u * cy } }
function ctrlPt(ax, ay, bx, by, k) { const mx = (ax + bx) / 2, my = (ay + by) / 2, dx = bx - ax, dy = by - ay, l = Math.hypot(dx, dy) || 1; return { x: mx - dy / l * k, y: my + dx / l * k } }
function icon(c, type, x, y, s, col) {
  c.save(); c.translate(x, y); c.strokeStyle = col; c.fillStyle = col; c.lineWidth = Math.max(1.5, s * .1); c.lineJoin = 'round'; c.lineCap = 'round';
  if (type === 'bolt') { c.beginPath(); c.moveTo(.12 * s, -.5 * s); c.lineTo(-.26 * s, .06 * s); c.lineTo(-.02 * s, .06 * s); c.lineTo(-.12 * s, .5 * s); c.lineTo(.26 * s, -.08 * s); c.lineTo(.02 * s, -.08 * s); c.closePath(); c.fill() }
  if (type === 'spark') { c.beginPath(); for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4 - Math.PI / 2, r = i % 2 ? s * .13 : s * .5; c.lineTo(Math.cos(a) * r, Math.sin(a) * r) } c.closePath(); c.fill() }
  if (type === 'eye') { c.beginPath(); c.ellipse(0, 0, s * .5, s * .3, 0, 0, 7); c.stroke(); c.beginPath(); c.arc(0, 0, s * .13, 0, 7); c.fill() }
  if (type === 'arrow') { c.beginPath(); c.moveTo(-.34 * s, .34 * s); c.lineTo(.34 * s, -.34 * s); c.moveTo(-.1 * s, -.34 * s); c.lineTo(.34 * s, -.34 * s); c.lineTo(.34 * s, .1 * s); c.stroke() }
  if (type === 'play') { c.beginPath(); c.moveTo(-.25 * s, -.35 * s); c.lineTo(.35 * s, 0); c.lineTo(-.25 * s, .35 * s); c.closePath(); c.fill() }
  if (type === 'check') { c.beginPath(); c.moveTo(-.35 * s, 0); c.lineTo(-.1 * s, .25 * s); c.lineTo(.38 * s, -.3 * s); c.stroke() }
  if (type === 'plus') { c.beginPath(); c.moveTo(-.35 * s, 0); c.lineTo(.35 * s, 0); c.moveTo(0, -.35 * s); c.lineTo(0, .35 * s); c.stroke() }
  c.restore();
}
/** count-up number formatting */
function countUp(value, p, o = {}) { const v = value * p; const d = o.decimals ?? 0; return (o.prefix || '') + v.toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d }) + (p >= 1 ? (o.suffix || '') : '') }

/* ---------- media (clips are pre-extracted frame sequences; see scripts/ingest.py) ---------- */
let MEDIA = {};
const IMGC = new Map(); let MISSING = []; let LIVE = false;
function loadURL(url) {
  let e = IMGC.get(url); if (e) return e.p;
  const img = new Image(); e = { img, ok: false }; e.p = new Promise(r => { img.onload = () => { e.ok = true; r(img) }; img.onerror = () => r(null) });
  img.src = url; IMGC.set(url, e);
  if (IMGC.size > 700) { for (const [k, v] of IMGC) { if (!v.keep) { IMGC.delete(k); break } } }
  return e.p;
}
function getURL(url) { const e = IMGC.get(url); if (e && e.ok) return e.img; if (!e) loadURL(url); if (!LIVE) MISSING.push(url); return null }
const frameURL = (m, i) => `${m.dir}/${String(i + 1).padStart(5, '0')}.${m.ext || 'jpg'}`;
function clipIndex(m, lt, o) {
  let s = (o.in || 0) + Math.max(0, lt) * (o.speed ?? 1);
  if (o.loop) s = s % m.duration; s = clamp(s, 0, m.duration - 1 / m.fps);
  return Math.min(m.frames - 1, Math.floor(s * m.fps + 1e-6));
}
function drawFit(c, img, iw, ih, x, y, w, h, o) {
  const s = (o.fit === 'contain' ? Math.min(w / iw, h / ih) : Math.max(w / iw, h / ih)) * (o.zoom || 1);
  const dw = iw * s, dh = ih * s, fx = o.focus ? o.focus[0] : .5, fy = o.focus ? o.focus[1] : .5;
  c.save(); c.beginPath(); if (o.radius) c.roundRect(x, y, w, h, o.radius); else c.rect(x, y, w, h); c.clip();
  if (o.filter) c.filter = o.filter; if (o.alpha != null) c.globalAlpha *= o.alpha;
  c.drawImage(img, x + (w - dw) * fx, y + (h - dh) * fy, dw, dh); c.restore();
}
function placeholder(c, id, x, y, w, h, o = {}) {
  c.save(); c.beginPath(); if (o.radius) c.roundRect(x, y, w, h, o.radius); else c.rect(x, y, w, h); c.clip();
  c.fillStyle = 'rgba(128,128,128,.16)'; c.fillRect(x, y, w, h);
  c.strokeStyle = 'rgba(128,128,128,.35)'; c.lineWidth = 1; for (let k = -h; k < w; k += 28 * U) { c.beginPath(); c.moveTo(x + k, y + h); c.lineTo(x + k + h, y); c.stroke() }
  c.restore(); txt(c, `[ ${id} ]`, x + w / 2, y + h / 2, { font: font(500, 16 * U, FM), color: 'rgba(128,128,128,.9)', align: 'center', base: 'middle', ls: 2 });
}
/** draw a video clip at local time lt. o: {in, speed, loop, fit:'cover'|'contain', focus:[fx,fy], zoom, radius, filter, alpha} */
function clip(c, id, lt, x, y, w, h, o = {}) {
  const m = MEDIA[id]; if (!m || m.type !== 'clip') return placeholder(c, id, x, y, w, h, o);
  const img = getURL(frameURL(m, clipIndex(m, lt, o)));
  for (let k = 1; k <= 8; k++) loadURL(frameURL(m, clipIndex(m, lt + k / FPS, o)));   // prefetch
  if (img) drawFit(c, img, m.w, m.h, x, y, w, h, o);
}
/** draw a still image (photo, logo, screenshot). same options as clip */
function image(c, id, x, y, w, h, o = {}) {
  const m = MEDIA[id]; if (!m || m.type !== 'image') return placeholder(c, id, x, y, w, h, o);
  const img = getURL(m.src); if (img) drawFit(c, img, m.w, m.h, x, y, w, h, o);
}
/** clip or image, whichever id is */
function media(c, id, lt, x, y, w, h, o = {}) { const m = MEDIA[id]; return m && m.type === 'image' ? image(c, id, x, y, w, h, o) : clip(c, id, lt, x, y, w, h, o) }
const hasMedia = id => !!MEDIA[id];

/* ---------- cues → camera shake / flash ---------- */
let CUES = [];
function impulse(T, key, k) { let s = 0; for (const q of CUES) if (q[key] && T >= q.t) s += q[key] * Math.exp(-(T - q.t) * k); return s }

/* ---------- transitions ---------- */
const TRANS = {
  whip(c, T, tr, fa, fb) {
    const acc = BUF[1].getContext('2d'), tmp = BUF[2].getContext('2d'), N = 10, sh = 1 / 60, ax = tr.axis || 'x', dir = tr.dir || 1;
    for (let k = 0; k < N; k++) {
      const e = E.ioExpo(P(T + (k / (N - 1) - .5) * sh, tr.start, tr.end)), off = e * (ax === 'x' ? W : H) * dir;
      tmp.save(); ax === 'x' ? tmp.translate(-off, 0) : tmp.translate(0, -off); fa(tmp, T); tmp.restore();
      tmp.save(); ax === 'x' ? tmp.translate((W * dir) - off, 0) : tmp.translate(0, (H * dir) - off); fb(tmp, T); tmp.restore();
      acc.globalAlpha = 1 / (k + 1); acc.drawImage(BUF[2], 0, 0);
    }
    acc.globalAlpha = 1; c.save(); c.setTransform(1, 0, 0, 1, 0, 0); c.drawImage(BUF[1], 0, 0); c.restore();
  },
  iris(c, T, tr, fa, fb) {
    fa(c, T); const p = (tr.ease ? E[tr.ease] : E.ioExpo)(P(T, tr.start, tr.end)), R = Math.hypot(W, H) * p;
    if (R <= 0) return; const cx = (tr.x ?? .5) * W, cy = (tr.y ?? .5) * H;
    const b = BUF[3].getContext('2d'); b.setTransform(1, 0, 0, 1, 0, 0); fb(b, T);
    c.save(); c.beginPath(); c.arc(cx, cy, R, 0, 7); c.clip(); c.setTransform(1, 0, 0, 1, 0, 0); c.drawImage(BUF[3], 0, 0); c.restore();
    if (tr.stroke) { c.save(); c.strokeStyle = tr.stroke; c.lineWidth = 3 * U; c.beginPath(); c.arc(cx, cy, R, 0, 7); c.stroke(); c.restore() }
  },
  fade(c, T, tr, fa, fb) {
    fa(c, T); const p = E.ioCubic(P(T, tr.start, tr.end)); if (p <= 0) return;
    const b = BUF[3].getContext('2d'); b.setTransform(1, 0, 0, 1, 0, 0); fb(b, T);
    c.save(); c.setTransform(1, 0, 0, 1, 0, 0); c.globalAlpha = p; c.drawImage(BUF[3], 0, 0); c.restore();
  },
  /** hard-edged diagonal wipe; tr.angle in degrees, tr.color draws a leading bar */
  wipe(c, T, tr, fa, fb) {
    fa(c, T); const p = (tr.ease ? E[tr.ease] : E.ioExpo)(P(T, tr.start, tr.end)); if (p <= 0) return;
    const b = BUF[3].getContext('2d'); b.setTransform(1, 0, 0, 1, 0, 0); fb(b, T);
    const a = (tr.angle ?? -15) * Math.PI / 180, L = Math.hypot(W, H), sweep = L * 1.2, x0 = -L * .1 + sweep * p;
    c.save(); c.setTransform(1, 0, 0, 1, 0, 0); c.translate(W / 2, H / 2); c.rotate(a); c.translate(-W / 2, -H / 2);
    c.beginPath(); c.rect(-L, -L, x0 + L, 3 * L); c.clip();
    c.translate(W / 2, H / 2); c.rotate(-a); c.translate(-W / 2, -H / 2); c.drawImage(BUF[3], 0, 0); c.restore();
    if (tr.color && p < 1) { c.save(); c.setTransform(1, 0, 0, 1, 0, 0); c.translate(W / 2, H / 2); c.rotate(a); c.translate(-W / 2, -H / 2); c.fillStyle = tr.color; c.fillRect(x0 - 40 * U, -L, 40 * U, 3 * L); c.restore() }
  },
  /** scale A up through the frame, B settles in from slightly large */
  zoom(c, T, tr, fa, fb) {
    const p = P(T, tr.start, tr.end), mid = .5, cx = (tr.x ?? .5) * W, cy = (tr.y ?? .5) * H;
    if (p < mid) { const k = 1 + 6 * E.inExpo(p / mid); c.save(); c.translate(cx, cy); c.scale(k, k); c.translate(-cx, -cy); fa(c, T); c.restore(); c.fillStyle = TH.flash; c.globalAlpha = E.inCubic(p / mid) * .9; c.fillRect(-W, -H, 3 * W, 3 * H); c.globalAlpha = 1 }
    else { const k = 1 + .25 * (1 - E.outExpo((p - mid) / (1 - mid))); c.save(); c.translate(cx, cy); c.scale(k, k); c.translate(-cx, -cy); fb(c, T); c.restore() }
  },
};
/** overlay helpers usable inside a scene (e.g. last beat of a scene) */
function stripesWipe(c, t, t0, dur, color, n = 7, slant = .17 * W) {
  const bwn = (W + slant) / n;
  for (let i = 0; i < n; i++) { const st = t0 + i * dur * .05, p = E.ioCubic(P(t, st, st + dur * .6)); if (p <= 0) continue;
    const xi = -slant + i * bwn, off = (1 - p) * (W + slant + bwn + 40), bw = bwn + 3; c.fillStyle = color; c.beginPath();
    c.moveTo(xi + slant + off, -10); c.lineTo(xi + slant + bw + off, -10); c.lineTo(xi + bw + off, H + 10); c.lineTo(xi + off, H + 10); c.closePath(); c.fill() }
}
function barsWipe(c, t, t0, dur, color, n = 9) {
  const bh = H / n; for (let i = 0; i < n; i++) { const p = E.ioExpo(P(t, t0 + i * dur * .08, t0 + dur * .3 + i * dur * .08)); if (p <= 0) continue; c.fillStyle = color;
    if (i % 2) c.fillRect(W * (1 - p) - 2, i * bh - 1, W * p + W * .1, bh + 2); else c.fillRect(-W * .1, i * bh - 1, W * p + W * .1, bh + 2) }
}

/* ---------- timeline ---------- */
let SCENES = [], TRANSITIONS = [];
function drawScene(c, T) {
  for (const tr of TRANSITIONS) if (T >= tr.start && T < tr.end) {
    const A = SCENES[tr.from], B = SCENES[tr.to];
    TRANS[tr.type](c, T, tr, (cc, TT) => A.draw(cc, TT - A.start, TT), (cc, TT) => B.draw(cc, TT - B.start, TT)); return;
  }
  let s = SCENES[0]; for (const sc of SCENES) if (T >= sc.start) s = sc;
  s.draw(c, T - s.start, T);
}
const VIG = (() => { const v = mk(), c = v.getContext('2d'), g = c.createRadialGradient(W / 2, H / 2, Math.min(W, H) * .35, W / 2, H / 2, Math.hypot(W, H) * .55); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, `rgba(0,0,0,${CFG.vignette})`); c.fillStyle = g; c.fillRect(0, 0, W, H); return v })();
function hud(c, T) {
  const h = CFG.hud; if (!h) return; const a = .75 * P(T, h.fadeIn ?? .9, (h.fadeIn ?? .9) + .4); if (a <= 0) return;
  c.save(); c.globalCompositeOperation = 'difference'; c.fillStyle = '#fff'; c.strokeStyle = '#fff'; c.globalAlpha = a;
  const m = 40 * U, L = 26 * U; c.lineWidth = 2 * U;
  [[m, m, 1, 1], [W - m, m, -1, 1], [m, H - m, 1, -1], [W - m, H - m, -1, -1]].forEach(([x, y, sx, sy]) => { c.beginPath(); c.moveTo(x, y + sy * L); c.lineTo(x, y); c.lineTo(x + sx * L, y); c.stroke() });
  c.font = font(500, 15 * U, FM); c.letterSpacing = 2 * U + 'px'; c.textBaseline = 'middle';
  c.textAlign = 'left'; c.fillText(h.title || '', m + L + 14 * U, m + 2);
  const fr = Math.floor(T * FPS) % FPS, s = Math.floor(T); c.textAlign = 'right'; c.fillText(`00:${String(s).padStart(2, '0')}:${String(fr).padStart(2, '0')}`, W - m - L - 14 * U, m + 2);
  let sec = ''; for (const [t0, l] of (h.sections || [])) if (T >= t0) sec = l; c.fillText(sec, W - m - L - 14 * U, H - m - 2);
  c.textAlign = 'left'; c.fillText(h.left || `${BPM} BPM`, m + L + 14 * U, H - m - 2);
  if (!PORTRAIT) c.fillRect(m + 160 * U, H - m - 3, (W - 2 * m - 460 * U) * T / DUR, 2 * U);
  c.restore();
}
function drawFrame(T) {
  const sc = BUF[0].getContext('2d'); sc.setTransform(1, 0, 0, 1, 0, 0);
  const sh = CFG.shake * U * impulse(T, 'shake', 11), dx = sh * noise1(T * 37), dy = sh * noise1(T * 37 + 50), zs = 1 + sh / (400 * U);
  sc.save(); sc.translate(W / 2 + dx, H / 2 + dy); sc.scale(zs, zs); sc.translate(-W / 2, -H / 2); drawScene(sc, T); sc.restore();
  X.setTransform(1, 0, 0, 1, 0, 0); X.globalCompositeOperation = 'source-over'; X.globalAlpha = 1; X.drawImage(BUF[0], 0, 0);
  if (CFG.vignette > 0) X.drawImage(VIG, 0, 0);
  const fl = Math.min(1, impulse(T, 'flash', 11)); if (fl > .004) { X.globalAlpha = fl; X.fillStyle = TH.flash; X.fillRect(0, 0, W, H); X.globalAlpha = 1 }
  hud(X, T);
  const fo = Math.max(CFG.fadeIn ? 1 - P(T, 0, CFG.fadeIn) : 0, CFG.fadeOut ? P(T, DUR - CFG.fadeOut, DUR) : 0);
  if (fo > 0) { X.globalAlpha = fo; X.fillStyle = '#000'; X.fillRect(0, 0, W, H); X.globalAlpha = 1 }
}
/** render T, waiting for any clip frames / images it needs. returns when pixels are final */
async function renderFrame(T) {
  for (let pass = 0; pass < 6; pass++) { MISSING = []; drawFrame(T); if (!MISSING.length) return true; await Promise.all(MISSING.map(u => loadURL(u))) }
  return false;
}

/* ---------- boot ---------- */
const Reel = {
  async start(def) {
    SCENES = def.scenes; TRANSITIONS = def.transitions || []; CUES = def.cues || [];
    for (let i = 0; i < SCENES.length; i++) if (SCENES[i].end == null) SCENES[i].end = i + 1 < SCENES.length ? SCENES[i + 1].start : DUR;
    try { const r = await fetch('media/manifest.json', { cache: 'no-store' }); if (r.ok) MEDIA = await r.json() } catch (e) { }
    await Promise.all(CFG.fontLoads.map(f => document.fonts.load(f)));
    await document.fonts.ready;
    await Promise.all(Object.values(MEDIA).filter(m => m.type === 'image').map(m => loadURL(m.src).then(() => { const e = IMGC.get(m.src); if (e) e.keep = true })));
    window.REEL = { config: CFG, cues: CUES, media: MEDIA, scenes: SCENES.map(s => ({ name: s.name, start: s.start, end: s.end })), transitions: TRANSITIONS };
    window.renderFrame = renderFrame;
    const h = location.hash;
    if (h.startsWith('#play')) {
      LIVE = true; cv.style.width = '100vw'; cv.style.height = 'auto'; document.body.style.background = '#000';
      const t0 = performance.now(); const loop = () => { drawFrame(((performance.now() - t0) / 1000) % DUR); requestAnimationFrame(loop) }; loop();
    } else if (h.startsWith('#t=')) { cv.style.width = '100vw'; cv.style.height = 'auto'; await renderFrame(parseFloat(h.slice(3))) }
    else await renderFrame(0);
    window.READY = true;
  },
};
