/* shorts kit — split-screen 9:16 layout on top of motion-reel's engine.js
   top half (0..SEAM): animated gag stage · bottom half: facecam · captions on the seam */
/* BRAND comes from brand.json (injected by short.py scaffold as window.BRAND) */
const BR = Object.assign({ handle: '@yourhandle', tagline: '', ring: '', live: false, cta: 'FOLLOW FOR MORE', ctaEdu: 'SAVE THIS + FOLLOW',
  watermark: true, faceFocus: [.5, .42] }, window.BRAND || {});
const C = Object.assign({ bg: '#07060b', panel: '#120d19', panel2: '#1b1424', pink: '#ff2e88', cyan: '#2ee6ff', yel: '#ffe14d',
  lime: '#b8ff3d', red: '#ff3b3b', green: '#35e07a', white: '#fff8f0', dim: '#9a8fa6', ink: '#07060b' }, BR.colors || {});
let SEAM = 960;   // may be animated per frame (e.g. camera big for a hook, then a small strip)
const FA = '"Display"', FS = '"Body"', FJ = '"Mono"';     // font files: fonts/display.ttf, body.ttf, mono.ttf
/** '#rrggbb' → 'rgba(r,g,b,a)' */
function hexA(hex, a) { const n = parseInt(hex.slice(1), 16); return `rgba(${n >> 16 & 255},${n >> 8 & 255},${n & 255},${a})` }
const EMOF = '"Apple Color Emoji","Noto Color Emoji","Segoe UI Emoji"';

/* ---------- primitives ---------- */
function emo(c, ch, x, y, size, o = {}) {
  const s = o.s ?? 1; if (s <= .001 || (o.alpha ?? 1) <= .002) return;
  c.save(); c.translate(x, y); c.rotate(o.rot || 0); c.scale(s, s); c.globalAlpha *= o.alpha ?? 1;
  c.font = `${size}px ${EMOF}`; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(ch, 0, size * .04); c.restore();
}
/** bold display text with outline; o.s = pop scale around (x,y) */
function big(c, s, x, y, size, o = {}) {
  const sc = o.s ?? 1, a = o.alpha ?? 1; if (sc <= .001 || a <= .002) return 0;
  const f = `${o.weight || 400} ${size}px ${o.font || FA}`;
  c.save(); c.translate(x, y); c.rotate(o.rot || 0); c.scale(sc, sc); c.globalAlpha *= a;
  c.font = f; c.letterSpacing = (o.ls || 0) + 'px'; c.textAlign = o.align || 'center'; c.textBaseline = 'middle';
  if (o.glow) { c.shadowColor = o.glow; c.shadowBlur = size * .35 }
  if (o.stroke !== false) { c.lineJoin = 'round'; c.strokeStyle = o.stroke || '#000'; c.lineWidth = o.lw ?? size * .16; c.strokeText(s, 0, 0) }
  c.shadowBlur = 0; c.fillStyle = o.color || C.white; c.fillText(s, 0, 0);
  const w = c.measureText(s).width; c.restore(); return w;
}
function label(c, s, x, y, size, color = C.white, o = {}) {
  txt(c, s, x, y, { font: font(o.weight || 700, size, o.font || FS), color, align: o.align || 'left', base: 'middle', ls: o.ls || 0, alpha: o.alpha ?? 1 });
}
function rr(c, x, y, w, h, r, fill, stroke, lw = 3) {
  c.beginPath(); c.roundRect(x, y, w, h, r); if (fill) { c.fillStyle = fill; c.fill() } if (stroke) { c.strokeStyle = stroke; c.lineWidth = lw; c.stroke() }
}
/** neon card: dark panel + coloured edge + glow */
function card(c, x, y, w, h, col = C.cyan, o = {}) {
  c.save(); c.shadowColor = col; c.shadowBlur = o.glow ?? 28; rr(c, x, y, w, h, o.r ?? 26, o.fill || C.panel, col, o.lw ?? 4); c.restore();
}
/** pop progress: 0 → overshoot → 1 */
const pop = (t, t0, d = .22) => E.outBack(P(t, t0, t0 + d));
/** slam: big → 1 with a hard landing */
const slam = (t, t0, d = .16) => t < t0 ? 0 : lerp(2.4, 1, E.outCubic(P(t, t0, t0 + d)));
/** stamp box with rotated text that slams in */
function stamp(c, s, x, y, size, col, t, t0, rot = -.12) {
  const k = slam(t, t0); if (!k) return;
  const a = clamp((t - t0) / .06);
  c.save(); c.translate(x, y); c.rotate(rot); c.scale(k, k); c.globalAlpha *= a;
  c.font = `400 ${size}px ${FA}`; const w = c.measureText(s).width + size * .7, h = size * 1.25;
  c.shadowColor = col; c.shadowBlur = 30; rr(c, -w / 2, -h / 2, w, h, size * .12, 'rgba(7,6,11,.82)', col, size * .09); c.shadowBlur = 0;
  c.fillStyle = col; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(s, 0, size * .04); c.restore();
}
function bar(c, x, y, w, h, p, col, bg = 'rgba(255,255,255,.1)') { rr(c, x, y, w, h, h / 2, bg); if (p > 0) { c.save(); c.shadowColor = col; c.shadowBlur = 18; rr(c, x, y, Math.max(h, w * clamp(p)), h, h / 2, col); c.restore() } }
function burst(c, x, y, r0, r1, n, col, a, rot = 0) {
  if (a <= 0) return; c.save(); c.globalAlpha *= a; c.strokeStyle = col; c.lineWidth = 10; c.lineCap = 'round';
  for (let i = 0; i < n; i++) { const an = rot + i * Math.PI * 2 / n; c.beginPath(); c.moveTo(x + Math.cos(an) * r0, y + Math.sin(an) * r0); c.lineTo(x + Math.cos(an) * r1, y + Math.sin(an) * r1); c.stroke() }
  c.restore();
}
/** confetti/sparks, deterministic */
function sparks(c, x, y, t, t0, n, cols, spread = 420, seed = 7) {
  if (t < t0 || t > t0 + 1.2) return; const r = rng(seed), lt = t - t0;
  for (let i = 0; i < n; i++) { const an = r() * Math.PI * 2, v = spread * (.4 + r() * .6), col = cols[i % cols.length];
    const px = x + Math.cos(an) * v * E.outExpo(clamp(lt / .7)), py = y + Math.sin(an) * v * E.outExpo(clamp(lt / .7)) + 260 * lt * lt;
    c.save(); c.globalAlpha = 1 - clamp(lt / 1.2); c.fillStyle = col; c.translate(px, py); c.rotate(lt * 8 + i); c.fillRect(-7, -12, 14, 24); c.restore() }
}

/* ---------- stage (top half) ---------- */
function stageBg(c, T, tint = C.pink) {
  c.fillStyle = C.bg; c.fillRect(-20, -20, W + 40, SEAM + 20);
  glow(c, W / 2, SEAM * .42, 700, /^#[0-9a-f]{6}$/i.test(tint) ? hexA(tint, 'A') : 'rgba(255,46,136,A)', .16);
  // perspective neon floor
  const hz = SEAM * .66; c.save(); c.beginPath(); c.rect(0, hz, W, SEAM - hz); c.clip();
  c.strokeStyle = tint; c.lineWidth = 2;
  for (let i = -12; i <= 12; i++) { c.globalAlpha = .22; c.beginPath(); c.moveTo(W / 2 + i * 26, hz); c.lineTo(W / 2 + i * 190, SEAM); c.stroke() }
  const sp = (T * .9) % 1;
  for (let k = 0; k < 9; k++) { const z = (k + sp) / 9, y = hz + (SEAM - hz) * z * z; c.globalAlpha = .1 + .3 * z; c.beginPath(); c.moveTo(0, y); c.lineTo(W, y); c.stroke() }
  c.restore();
  const g = c.createLinearGradient(0, hz - 60, 0, hz + 40); g.addColorStop(0, 'rgba(7,6,11,0)'); g.addColorStop(1, 'rgba(7,6,11,.0)'); c.fillStyle = g;
  // scanlines
  c.save(); c.globalAlpha = .06; c.fillStyle = '#000'; for (let y = 0; y < SEAM; y += 6) c.fillRect(0, y, W, 2); c.restore();
}
/** run the stage beats; each beat lands with a slam + flash; first beat is untouched so frame 0 is clean */
function runBeats(c, T, beats) {
  c.save(); c.beginPath(); c.rect(0, 0, W, SEAM); c.clip();
  for (let i = 0; i < beats.length; i++) {
    const b = beats[i], end = i + 1 < beats.length ? beats[i + 1].a : Infinity;
    if (T < b.a || T >= end) continue;
    const lt = T - b.a;
    stageBg(c, T, b.tint || C.pink);
    c.save();
    if (i > 0) { const k = 1 + .09 * (1 - E.outExpo(P(lt, 0, .3))); c.translate(W / 2, SEAM / 2); c.scale(k, k); c.translate(-W / 2, -SEAM / 2) }
    b.draw(c, lt, T, end - b.a); c.restore();
    if (i > 0 && lt < .14) { c.fillStyle = `rgba(255,255,255,${.35 * (1 - lt / .14)})`; c.fillRect(0, 0, W, SEAM) }
    if (i > 0 && lt < .2) { const p = E.outCubic(lt / .2); c.fillStyle = b.tint || C.pink; c.save(); c.globalAlpha = .9; c.translate(lerp(-W * .3, W * 1.3, p), 0); c.rotate(.22); c.fillRect(-40, -200, 80, SEAM + 400); c.restore() }
  }
  c.restore();
}

/* ---------- facecam (bottom half) ---------- */
/** punches: [[t, amount]] quick zoom-ins on emphasis words */
function faceCam(c, T, punches = [], o = {}) {
  let z = 1.02 + .05 * P(T, 0, DUR);
  for (const [t0, a] of punches) if (T >= t0) z += a * Math.exp(-(T - t0) * 5) * E.outExpo(P(T, t0, t0 + .08));
  clip(c, 'face', Math.min(T, o.end ?? 1e9), 0, SEAM, W, H - SEAM, { zoom: z, focus: o.focus || BR.faceFocus });
  const g = c.createLinearGradient(0, H - 260, 0, H); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,.55)'); c.fillStyle = g; c.fillRect(0, H - 260, W, 260);
  if (BR.watermark && BR.handle) label(c, BR.handle, W / 2, H - 70, 34, 'rgba(255,248,240,.8)', { align: 'center', weight: 700 });
  // neon seam
  c.save(); const sg = c.createLinearGradient(0, 0, W, 0); sg.addColorStop(0, C.pink); sg.addColorStop(1, C.cyan);
  c.shadowColor = C.pink; c.shadowBlur = 24; c.fillStyle = sg; c.fillRect(0, SEAM - 4, W, 8); c.restore();
}

/* ---------- captions on the seam ---------- */
/** caps: [[t0, t1, 'TEXT with *HOT* words']] */
function captions(c, T, caps, o = {}) {
  const y0 = o.y ?? SEAM + 150, size = o.size ?? 104;
  for (let i = 0; i < caps.length; i++) {
    const [a, b, s] = caps[i]; if (T < a || T >= b) continue;
    const lt = T - a, k = i === 0 && a === 0 ? 1 : lerp(.55, 1, E.outBack(P(lt, 0, .16)));
    const words = s.split(' ').map(w => ({ hot: /\*/.test(w), w: w.replace(/\*/g, '') }));
    c.save(); c.font = `400 ${size}px ${FA}`;
    const sp = size * .26, maxW = W - 150;
    const lines = [[]]; let cw = 0;
    for (const wd of words) { wd.width = c.measureText(wd.w).width; if (cw + wd.width > maxW && lines[lines.length - 1].length) { lines.push([]); cw = 0 } lines[lines.length - 1].push(wd); cw += wd.width + sp }
    const lh = size * 1.05, top = y0 - (lines.length - 1) * lh / 2;
    c.translate(W / 2, y0); c.rotate((i % 2 ? 1 : -1) * .025); c.scale(k, k); c.translate(-W / 2, -y0);
    lines.forEach((ln, li) => {
      const tw = ln.reduce((s, w) => s + w.width, 0) + sp * (ln.length - 1); let x = W / 2 - tw / 2;
      for (const wd of ln) {
        const hotCol = o.hot || C.yel;
        big(c, wd.w, x + wd.width / 2, top + li * lh, size, { color: wd.hot ? hotCol : C.white, lw: size * .2, glow: wd.hot ? 'rgba(0,0,0,.0)' : null });
        x += wd.width + sp;
      }
    });
    c.restore();
  }
}
function progress(c, T, end) { const p = clamp(T / end); c.fillStyle = 'rgba(255,255,255,.12)'; c.fillRect(0, 0, W, 10); c.save(); c.shadowColor = C.pink; c.shadowBlur = 16; c.fillStyle = C.pink; c.fillRect(0, 0, W * p, 10); c.restore() }

/* ---------- end card (full screen) ---------- */
function endCard(c, t, T, o = {}) {
  bgFill(c, C.bg); stageBg(c, T, C.pink);
  c.save(); c.translate(0, SEAM * .9); stageBg(c, T + .5, C.cyan); c.restore();
  const cx = W / 2, cy = 640, r = 250 * E.outBack(P(t, 0, .35));
  if (r > 1) {
    c.save(); c.shadowColor = C.pink; c.shadowBlur = 50; c.beginPath(); c.arc(cx, cy, r + 12, 0, 7); c.fillStyle = C.pink; c.fill(); c.restore();
    c.save(); c.beginPath(); c.arc(cx, cy, r, 0, 7); c.clip(); clip(c, 'face', o.faceT ?? 0, cx - r * 1.125, cy - r, r * 2.25, r * 2, { focus: BR.faceFocus }); c.restore();
    if (BR.ring) ringText(c, ' ' + BR.ring.replace(/\s*•?\s*$/, '') + ' •', cx, cy, r + 60, t * .8 - 1.5, font(700, 30, FJ), C.cyan, P(t, .15, .4));
  }
  const live = BR.live ? pop(t, .12) : 0; if (live > 0) { c.save(); c.translate(cx, cy + r + 10); c.scale(live, live); rr(c, -92, -34, 184, 68, 34, C.red); c.fillStyle = '#fff'; c.beginPath(); c.arc(-50, 0, 11, 0, 7); c.fill(); label(c, 'LIVE', 12, 2, 38, '#fff', { align: 'center', weight: 700 }); c.restore() }
  const cta = o.line1 || (o.edu ? BR.ctaEdu : BR.cta), handle = (BR.handle || '').toUpperCase();
  big(c, cta, cx, 1110, Math.min(118, fit(c, cta, 400, FA, W - 140, 118)), { s: pop(t, .18), color: C.white });
  if (handle) big(c, handle, cx, 1250, Math.min(132, fit(c, handle, 400, FA, W - 120, 132)), { s: pop(t, .28), color: C.yel, glow: hexA(C.yel, .5) });
  const tag = o.line3 ?? BR.tagline; if (tag) label(c, tag, cx, 1370, 40, C.dim, { align: 'center', weight: 600, alpha: P(t, .4, .6) });
  if (o.emoji) emo(c, o.emoji, cx + 330, 450, 150, { s: pop(t, .35), rot: Math.sin(T * 5) * .12 });
}

/* ---------- educational helpers ---------- */
/** numbered step badge + heading at the top of the stage */
function stepBadge(c, n, text, t, col = C.cyan) {
  const p = pop(t, 0, .25); if (p <= 0) return;
  c.save(); c.translate(140, 115); c.scale(p, p); c.shadowColor = col; c.shadowBlur = 24; rr(c, -60, -44, 120, 88, 44, col); c.shadowBlur = 0;
  big(c, String(n), 0, 3, 62, { color: C.ink, stroke: false }); c.restore();
  const tp = E.outExpo(P(t, .06, .35)); c.save(); c.beginPath(); c.rect(220, 60, W - 260, 110); c.clip();
  big(c, text, 230 + (1 - tp) * -120, 115, 76, { align: 'left', color: C.white, alpha: tp, lw: 10 }); c.restore();
}
/** browser window chrome with a typed URL */
function browserBar(c, x, y, w, url, t, t0, cps = 26) {
  rr(c, x, y, w, 96, 22, '#1c1824', 'rgba(255,255,255,.18)', 2);
  [C.red, C.yel, C.green].forEach((col, i) => { c.fillStyle = col; c.beginPath(); c.arc(x + 36 + i * 32, y + 48, 10, 0, 7); c.fill() });
  rr(c, x + 140, y + 18, w - 170, 60, 30, '#0b0910');
  label(c, '🔒', x + 172, y + 49, 26, C.dim);
  typeText(c, url, x + 205, y + 61, font(700, 34, FJ), C.white, t, t0, cps);
}
