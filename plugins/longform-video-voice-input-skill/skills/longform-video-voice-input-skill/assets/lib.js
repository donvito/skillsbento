/* ==========================================================================
   Visual library for long-form voice-driven explainers. Default theme: monochrome
   (black / white / gray, like the user's Grok Bot screens), grotesque display font,
   plain backgrounds. Swap the C palette for another theme. Pure functions of time T.
   Key pieces: wt()/phraseTimes() sync to window.VO, richLine/syncPara word-synced
   text, card/chip/bubble/phone/zoomPanel UI, spark() = the agent dot, ico() icons.
   ========================================================================== */
const C = {
  ivory: '#F3F3F3', paper: '#FFFFFF', oat: '#EAEAEA', oat2: '#D4D4D4',
  ink: '#0B0B0B', ink2: '#555555', ink3: '#8E8E8E', line: 'rgba(0,0,0,.09)',
  clay: '#6E6E6E', clayD: '#3A3A3A', clayL: '#DDDDDD', clayXL: '#EEEEEE', sun: '#A8A8A8',
  slate: '#0A0A0A', slate2: '#161616', slate3: '#242424', slate4: '#3A3A3A',
  cream: '#F5F5F5', creamDim: 'rgba(245,245,245,.6)', creamFaint: 'rgba(245,245,245,.12)',
  olive: '#8F8F8F', oliveL: '#E6E6E6', sky: '#9A9A9A', skyL: '#E8E8E8', red: '#4A4A4A', redL: '#E9E9E9', amber: '#8A8A8A', amberL: '#EEEEEE',
};
const SERIF = '"Bricolage Grotesque"', SANS = '"Inter"', MONO = '"JetBrains Mono"';
const fS = (px, w = 500, it = false) => `${it ? 800 : 600} ${Math.round(px * .86 * 10) / 10}px ${SERIF}`;
const fN = (px, w = 500) => `${w} ${px}px ${SANS}`;
const fM = (px, w = 500) => `${w} ${px}px ${MONO}`;
const TAU = Math.PI * 2;

/* ---------- VO word lookup ---------- */
const VOW = (window.VO || []).map(([w, s, e]) => ({ w, s, e, n: w.toLowerCase().replace(/[^a-z0-9]/g, '') }));
/** time of the first VO word matching `word` starting at/after `near - .6` */
function wt(word, near) { const n = word.toLowerCase().replace(/[^a-z0-9]/g, ''); for (const v of VOW) if (v.s >= near - .6 && v.n === n) return v.s; return near }
/** for a phrase, return per-word reveal times by matching the VO sequentially from tFrom */
const _phraseCache = new Map();
function phraseTimes(text, tFrom) {
  const key = text + '@' + tFrom; if (_phraseCache.has(key)) return _phraseCache.get(key);
  const words = text.split(/\s+/).filter(Boolean); let k = VOW.findIndex(v => v.s >= tFrom - .35); if (k < 0) k = VOW.length;
  const out = []; let last = tFrom;
  for (const w of words) {
    const n = w.toLowerCase().replace(/[^a-z0-9]/g, ''); let found = -1;
    for (let j = k; j < Math.min(VOW.length, k + 6); j++) if (VOW[j].n === n || (n.length > 3 && VOW[j].n.startsWith(n.slice(0, 4)))) { found = j; break }
    if (found >= 0) { last = VOW[found].s; k = found + 1 } else last += .18;
    out.push(last);
  }
  _phraseCache.set(key, out); return out;
}

/* ---------- grain + backgrounds ---------- */
const GRAIN = (() => { const g = mk(256, 256), x = g.getContext('2d'), d = x.createImageData(256, 256), r = rng(11);
  for (let i = 0; i < d.data.length; i += 4) { const v = r() * 255; d.data[i] = d.data[i + 1] = d.data[i + 2] = v; d.data[i + 3] = 255 } x.putImageData(d, 0, 0); return g })();
let _gp = null;
function grain(c, a) { if (!_gp) _gp = c.createPattern(GRAIN, 'repeat'); c.save(); c.globalAlpha = a; c.globalCompositeOperation = 'overlay'; c.fillStyle = _gp; c.fillRect(0, 0, W, H); c.restore() }
function bgLight(c, T, o = {}) {
  bgFill(c, o.col || C.ivory);
  glow(c, W * (.84 + .05 * noise1(T * .07)), H * (.1 + .05 * noise1(T * .05 + 3)), W * .5, 'rgba(255,255,255,A)', .7);
  glow(c, W * (.08 + .04 * noise1(T * .06 + 7)), H * .98, W * .42, 'rgba(0,0,0,A)', .03);
}
function bgDark(c, T, o = {}) {
  bgFill(c, o.col || C.slate);
  glow(c, W * (.78 + .06 * noise1(T * .06)), H * (.22 + .08 * noise1(T * .05 + 9)), W * .62, 'rgba(255,255,255,A)', (o.glow ?? .16) * .35);
  glow(c, W * .1, H * 1.0, W * .45, 'rgba(255,255,255,A)', .02);
}
/** graph-paper grid, drifting slowly */
function gridLines(c, col, sp, T) { c.save(); c.strokeStyle = col; c.lineWidth = 1; const ox = (T * 6 * U) % sp, oy = (T * 3 * U) % sp; c.beginPath();
  for (let x = -ox; x < W + sp; x += sp) { c.moveTo(Math.round(x) + .5, 0); c.lineTo(Math.round(x) + .5, H) } for (let y = -oy; y < H + sp; y += sp) { c.moveTo(0, Math.round(y) + .5); c.lineTo(W, Math.round(y) + .5) } c.stroke(); c.restore() }
/** fine dotted paper grid */
function dots() { }
function _oldDots(c, col, a, sp = 36, ox = 0, oy = 0) { dotGrid(c, sp * U, col, a, ox, oy, 1.3 * U) }

/* ---------- text ---------- */
function measure(c, s, f) { c.save(); c.font = f; const w = c.measureText(s).width; c.restore(); return w }
/** split a string into lines that fit maxW */
function wrap(c, s, f, maxW) {
  const words = s.split(' '), lines = []; let cur = '';
  for (const w of words) { const t = cur ? cur + ' ' + w : w; if (measure(c, t, f) > maxW && cur) { lines.push(cur); cur = w } else cur = t }
  if (cur) lines.push(cur); return lines;
}
/** masked rise of a single string */
function riseStr(c, s, x, y, f, col, T, t0, o = {}) {
  const p = (o.ease || E.outExpo)(P(T, t0, t0 + (o.dur || .6))); if (p <= 0) return;
  const size = parseFloat(f.match(/(\d+(\.\d+)?)px/)[1]);
  c.save(); c.font = f; c.textAlign = o.align || 'left'; c.textBaseline = 'alphabetic'; c.fillStyle = col;
  if (o.alpha != null) c.globalAlpha *= o.alpha;
  const w = c.measureText(s).width, x0 = o.align === 'center' ? x - w / 2 : o.align === 'right' ? x - w : x;
  c.beginPath(); c.rect(x0 - size, y - size * 1.1, w + size * 2, size * 1.45); c.clip();
  c.globalAlpha *= clamp(p * 1.6); c.fillText(s, x, y + (1 - p) * size * 1.05); c.restore();
}
/**
 * Rich line: runs = [[text, font, color], ...] laid out on one baseline; each word rises at its own time.
 * times: array of per-word times (across all runs) or a start time + stagger.
 */
function richLine(c, runs, x, y, T, o = {}) {
  const items = []; let cx = 0; const sp = o.space ?? null;
  runs.forEach(([s, f, col, extra]) => { s.split(' ').forEach((w, i, arr) => { if (!w) return; const ww = measure(c, w, f), spw = sp ?? measure(c, ' ', f); items.push({ w, f, col, x: cx, ww, extra }); cx += ww + spw }) });
  const total = cx - (items.length ? (sp ?? measure(c, ' ', items[items.length - 1].f)) : 0);
  const x0 = o.align === 'center' ? x - total / 2 : o.align === 'right' ? x - total : x;
  items.forEach((it, i) => {
    const t0 = Array.isArray(o.times) ? (o.times[i] ?? o.times[o.times.length - 1]) : (o.t0 ?? 0) + i * (o.stag ?? .07);
    riseStr(c, it.w, x0 + it.x, y, it.f, it.col, T, t0, { dur: o.dur, alpha: o.alpha });
    if (it.extra === 'underline') { const p = E.outExpo(P(T, t0 + .15, t0 + .7)); if (p > 0) { c.save(); c.fillStyle = it.col; const sz = parseFloat(it.f.match(/(\d+(\.\d+)?)px/)[1]); c.fillStyle = C.sun; c.globalAlpha *= clamp(o.alpha ?? 1); c.fillRect(x0 + it.x, y + sz * .1, (it.ww + (i < items.length - 1 && items[i + 1].extra === 'underline' ? measure(c, ' ', it.f) : 0)) * p, Math.max(4, sz * .085)); c.restore() } }
    if (it.extra === 'mark') { const p = E.outExpo(P(T, t0 + .1, t0 + .6)); if (p > 0) { const sz = parseFloat(it.f.match(/(\d+(\.\d+)?)px/)[1]); c.save(); c.globalCompositeOperation = 'multiply'; c.fillStyle = C.clayL; c.fillRect(x0 + it.x - sz * .08, y - sz * .72, (it.ww + sz * .16) * p, sz * .9); c.restore(); riseStr(c, it.w, x0 + it.x, y, it.f, it.col, T, t0, { dur: o.dur }) } }
  });
  return total;
}
/** paragraph whose words reveal in sync with the VO (phraseTimes) or a stagger */
function syncPara(c, s, x, y, maxW, f, lh, col, T, tFrom, o = {}) {
  const lines = wrap(c, s, f, maxW), times = o.times || (o.sync === false ? null : phraseTimes(s, tFrom)); let k = 0;
  lines.forEach((ln, li) => { const n = ln.split(' ').length; const ts = times ? times.slice(k, k + n) : null;
    const lx = o.align === 'center' ? x : x;
    richLine(c, [[ln, f, col]], lx, y + li * lh, T, { times: ts, t0: tFrom + k * (o.stag ?? .05), stag: o.stag ?? .05, align: o.align, dur: o.dur }); k += n });
  return lines.length * lh;
}
const sentence = s => s.charAt(0) + s.slice(1).toLowerCase().replace(/\bai\b/g, 'AI');
function label(c, s, x, y, col, a = 1, o = {}) { txt(c, sentence(s), x, y, { font: fN((o.size || 17 * U) * 1.35, 600), color: col, align: o.align, alpha: a, base: o.base }) }
/** kicker: clay dot + mono caps label */
function kicker() { }
function _oldKicker(c, s, x, y, T, t0, col = C.clay, o = {}) {
  const p = E.outExpo(P(T, t0, t0 + .5)); if (p <= 0) return;
  c.save(); c.globalAlpha *= p; const dx = o.align === 'center' ? -(measure(c, s, fM(17 * U)) + s.length * 3 * U + 22 * U) / 2 : 0;
  c.fillStyle = col; c.beginPath(); c.arc(x + dx + 6 * U, y - 6 * U, 5 * U * E.outBack(P(T, t0, t0 + .4)), 0, TAU); c.fill();
  label(c, s, x + dx + 22 * U + (1 - p) * 20 * U, y, col); c.restore();
}

/* ---------- shapes ---------- */
function rr(c, x, y, w, h, r) { c.beginPath(); c.roundRect(x, y, w, h, r) }
function card(c, x, y, w, h, o = {}) {
  const r = o.r ?? 22 * U; c.save();
  if (o.alpha != null) c.globalAlpha *= o.alpha;
  if (o.shadow !== 0) { c.shadowColor = o.shadowCol || 'rgba(0,0,0,.16)'; c.shadowBlur = (o.shadow ?? 1) * 40 * U; c.shadowOffsetY = (o.shadow ?? 1) * 14 * U }
  rr(c, x, y, w, h, r); c.fillStyle = o.fill || C.paper; c.fill(); c.shadowColor = 'transparent';
  if (o.stroke) { c.strokeStyle = o.stroke; c.lineWidth = o.lw || 1.5 * U; c.stroke() }
  c.restore();
}
/** pop-in transform helper: scales around (cx,cy) */
function pop(c, cx, cy, p, fn, o = {}) {
  if (p <= 0) return; const s = o.from != null ? lerp(o.from, 1, p) : p;
  c.save(); c.translate(cx, cy + (o.dy || 0) * (1 - p)); c.scale(s, s); c.translate(-cx, -cy); c.globalAlpha *= clamp(p * 1.5); fn(); c.restore();
}
/** chip with optional icon */
function chip(c, x, y, s, o = {}) {
  const f = o.font || fN(24 * U, 500), h = o.h || 52 * U, pad = o.pad || 22 * U, iw = o.icon ? h * .62 : 0;
  const w = measure(c, s, f) + pad * 2 + (iw ? iw + 10 * U : 0); const p = o.p ?? 1; if (p <= 0) return w;
  const x0 = o.align === 'center' ? x - w / 2 : o.align === 'right' ? x - w : x;
  pop(c, x0 + w / 2, y, p, () => {
    rr(c, x0, y - h / 2, w, h, h / 2); c.fillStyle = o.bg || C.paper; c.fill(); if (o.stroke) { c.strokeStyle = o.stroke; c.lineWidth = 1.5 * U; c.stroke() }
    if (o.icon) ico(c, o.icon, x0 + pad + iw / 2, y, iw, o.ic || o.fg || C.ink);
    txt(c, s, x0 + pad + (iw ? iw + 10 * U : 0), y + 1, { font: f, color: o.fg || C.ink, base: 'middle' });
  }, { from: .6 });
  return w;
}
/** animated check in a circle */
function checkMark(c, x, y, r, p, col = C.olive, o = {}) {
  if (p <= 0) return; const a = E.outBack(P(p, 0, .45));
  c.save(); c.translate(x, y); c.scale(a, a); c.beginPath(); c.arc(0, 0, r, 0, TAU); c.fillStyle = col; c.fill();
  const q = E.outCubic(P(p, .3, 1)); c.strokeStyle = o.ink || '#fff'; c.lineWidth = r * .2; c.lineCap = 'round'; c.lineJoin = 'round';
  c.beginPath(); const pts = [[-.42, .02], [-.12, .32], [.45, -.3]]; c.moveTo(pts[0][0] * r, pts[0][1] * r);
  if (q < .4) { const k = q / .4; c.lineTo(lerp(pts[0][0], pts[1][0], k) * r, lerp(pts[0][1], pts[1][1], k) * r) }
  else { c.lineTo(pts[1][0] * r, pts[1][1] * r); const k = (q - .4) / .6; c.lineTo(lerp(pts[1][0], pts[2][0], k) * r, lerp(pts[1][1], pts[2][1], k) * r) }
  c.stroke(); c.restore();
}
function crossMark(c, x, y, r, p, col = C.red) {
  if (p <= 0) return; const a = E.outBack(P(p, 0, .45));
  c.save(); c.translate(x, y); c.scale(a, a); c.beginPath(); c.arc(0, 0, r, 0, TAU); c.fillStyle = col; c.fill();
  c.strokeStyle = '#fff'; c.lineWidth = r * .2; c.lineCap = 'round'; const q = E.outCubic(P(p, .3, 1)), k = .36 * r;
  c.beginPath(); c.moveTo(-k, -k); c.lineTo(lerp(-k, k, clamp(q * 2)), lerp(-k, k, clamp(q * 2))); if (q > .5) { c.moveTo(k, -k); c.lineTo(lerp(k, -k, (q - .5) * 2), lerp(-k, k, (q - .5) * 2)) } c.stroke(); c.restore();
}
/** strike-through line drawn over a region */
function strike(c, x, y, w, p, col = C.red, lw = 4) { if (p <= 0) return; c.save(); c.strokeStyle = col; c.lineWidth = lw * U; c.lineCap = 'round'; c.beginPath(); c.moveTo(x, y); c.lineTo(x + w * E.outCubic(p), y - 2 * U); c.stroke(); c.restore() }

/* ---------- the agent mark (spark) ---------- */
function spark(c, x, y, r, T, o = {}) {
  const p = o.p ?? 1; if (p <= 0 || r <= 0) return; const col = o.col || C.ink, busy = o.busy || 0;
  const breathe = 1 + .04 * Math.sin(T * 2.4);
  c.save(); c.translate(x, y); c.scale(p * breathe, p * breathe);
  c.beginPath(); c.arc(0, 0, r * .5, 0, TAU); c.fillStyle = col; c.fill();
  c.strokeStyle = col; c.lineWidth = Math.max(1.5, r * .09); c.lineCap = 'round';
  c.globalAlpha *= .35 + .65 * busy; c.beginPath();
  if (busy > .05) { const a = T * 4; c.arc(0, 0, r * .82, a, a + Math.PI * 1.3) } else c.arc(0, 0, r * .82, 0, TAU);
  c.stroke(); c.restore();
}
function _oldSpark(c, x, y, r, T, o = {}) {
  const p = o.p ?? 1; if (p <= 0) return; const n = o.rays || 10, col = o.col || C.clay, rot = (o.rot ?? 0) + (o.spin ?? .15) * T;
  c.save(); c.translate(x, y); c.scale(p, p); c.rotate(rot); c.strokeStyle = col; c.lineCap = 'round';
  const busy = o.busy || 0;
  for (let i = 0; i < n; i++) {
    const a = i * TAU / n, h = .72 + .28 * hash(i * 3.7 + (o.seed || 0)), pulse = 1 + busy * .22 * Math.sin(T * 9 - i * .8);
    c.lineWidth = r * .2; c.beginPath(); c.moveTo(Math.cos(a) * r * .16, Math.sin(a) * r * .16); c.lineTo(Math.cos(a) * r * h * pulse, Math.sin(a) * r * h * pulse); c.stroke();
  }
  c.restore();
}
/** orbiting dots around the agent mark while it is "working" */
function workingRing(c, x, y, r, T, a = 1, col = C.clay) {
  if (a <= 0) return; c.save(); c.globalAlpha *= a; for (let i = 0; i < 3; i++) { const an = T * 2.4 + i * TAU / 3; c.fillStyle = col; c.beginPath(); c.arc(x + Math.cos(an) * r, y + Math.sin(an) * r, 5 * U, 0, TAU); c.fill() }
  c.strokeStyle = col; c.globalAlpha *= .25; c.lineWidth = 1.5 * U; c.beginPath(); c.arc(x, y, r, 0, TAU); c.stroke(); c.restore();
}
/** typing dots */
function typingDots(c, x, y, T, col = C.ink3, a = 1) { if (a <= 0) return; c.save(); c.globalAlpha *= a; for (let i = 0; i < 3; i++) { const b = Math.max(0, Math.sin(T * 7 - i * .7)); c.fillStyle = col; c.beginPath(); c.arc(x + i * 16 * U, y - b * 5 * U, 5 * U, 0, TAU); c.fill() } c.restore() }

/* ---------- icons (line style) ---------- */
function ico(c, name, x, y, s, col, o = {}) {
  c.save(); c.translate(x, y); c.strokeStyle = col; c.fillStyle = col; c.lineWidth = o.lw || Math.max(1.6, s * .085); c.lineCap = 'round'; c.lineJoin = 'round';
  const k = s / 2; const L = (pts) => { c.beginPath(); pts.forEach(([a, b], i) => i ? c.lineTo(a * k, b * k) : c.moveTo(a * k, b * k)); c.stroke() };
  const circ = (cx, cy, r, fill) => { c.beginPath(); c.arc(cx * k, cy * k, r * k, 0, TAU); fill ? c.fill() : c.stroke() };
  const box = (x0, y0, w, h, r, fill) => { c.beginPath(); c.roundRect(x0 * k, y0 * k, w * k, h * k, r * k); fill ? c.fill() : c.stroke() };
  switch (name) {
    case 'search': circ(-.15, -.15, .55); L([[.25, .25], [.8, .8]]); break;
    case 'mail': box(-.85, -.6, 1.7, 1.2, .15); L([[-.8, -.5], [0, .1], [.8, -.5]]); break;
    case 'plane': c.beginPath(); c.moveTo(-.9 * k, .05 * k); c.lineTo(.85 * k, -.15 * k); c.quadraticCurveTo(1 * k, 0, .85 * k, .15 * k); c.lineTo(-.9 * k, .05 * k); c.stroke(); L([[0, -.08], [-.35, -.75], [-.15, -.75], [.35, -.1]]); L([[.0, .12], [-.35, .75], [-.15, .75], [.35, .12]]); L([[-.7, .02], [-.85, -.35]]); break;
    case 'cart': L([[-.9, -.7], [-.6, -.7], [-.35, .35], [.65, .35], [.85, -.4], [-.5, -.4]]); circ(-.25, .7, .12, 1); circ(.5, .7, .12, 1); break;
    case 'phone': c.beginPath(); c.moveTo(-.55 * k, -.85 * k); c.lineTo(-.25 * k, -.85 * k); c.lineTo(-.1 * k, -.45 * k); c.lineTo(-.3 * k, -.25 * k); c.quadraticCurveTo(-.05 * k, .25 * k, .3 * k, .35 * k); c.lineTo(.5 * k, .15 * k); c.lineTo(.85 * k, .3 * k); c.lineTo(.85 * k, .6 * k); c.quadraticCurveTo(.8 * k, .9 * k, .5 * k, .85 * k); c.quadraticCurveTo(-.7 * k, .6 * k, -.85 * k, -.5 * k); c.quadraticCurveTo(-.85 * k, -.85 * k, -.55 * k, -.85 * k); c.stroke(); break;
    case 'calendar': box(-.8, -.65, 1.6, 1.45, .15); L([[-.8, -.2], [.8, -.2]]); L([[-.4, -.85], [-.4, -.5]]); L([[.4, -.85], [.4, -.5]]); circ(-.35, .25, .09, 1); circ(0, .25, .09, 1); circ(.35, .25, .09, 1); break;
    case 'card': box(-.9, -.6, 1.8, 1.2, .15); L([[-.9, -.25], [.9, -.25]]); L([[-.6, .3], [-.2, .3]]); break;
    case 'lock': box(-.6, -.15, 1.2, .95, .15); c.beginPath(); c.arc(0, -.15 * k, .4 * k, Math.PI, 0); c.stroke(); circ(0, .3, .1, 1); break;
    case 'globe': circ(0, 0, .82); c.beginPath(); c.ellipse(0, 0, .35 * k, .82 * k, 0, 0, TAU); c.stroke(); L([[-.8, 0], [.8, 0]]); L([[-.65, -.45], [.65, -.45]]); L([[-.65, .45], [.65, .45]]); break;
    case 'pin': c.beginPath(); c.moveTo(0, .9 * k); c.bezierCurveTo(-.25 * k, .45 * k, -.7 * k, .1 * k, -.7 * k, -.25 * k); c.arc(0, -.25 * k, .7 * k, Math.PI, 0); c.bezierCurveTo(.7 * k, .1 * k, .25 * k, .45 * k, 0, .9 * k); c.stroke(); circ(0, -.25, .25); break;
    case 'check': L([[-.6, 0], [-.15, .45], [.65, -.45]]); break;
    case 'x': L([[-.55, -.55], [.55, .55]]); L([[.55, -.55], [-.55, .55]]); break;
    case 'clock': circ(0, 0, .82); L([[0, -.5], [0, 0], [.35, .25]]); break;
    case 'bed': L([[-.9, -.5], [-.9, .6]]); L([[-.9, .25], [.9, .25], [.9, .6]]); box(-.6, -.15, .5, .35, .12); c.beginPath(); c.moveTo(-.02 * k, .25 * k); c.lineTo(-.02 * k, -.2 * k); c.lineTo(.6 * k, -.2 * k); c.quadraticCurveTo(.9 * k, -.2 * k, .9 * k, .1 * k); c.stroke(); break;
    case 'list': [-.5, 0, .5].forEach(yy => { circ(-.65, yy, .08, 1); L([[-.35, yy], [.75, yy]]) }); break;
    case 'warn': c.beginPath(); c.moveTo(0, -.85 * k); c.lineTo(.9 * k, .75 * k); c.lineTo(-.9 * k, .75 * k); c.closePath(); c.stroke(); L([[0, -.25], [0, .2]]); circ(0, .47, .07, 1); break;
    case 'user': circ(0, -.38, .38); c.beginPath(); c.arc(0, .9 * k, .75 * k, Math.PI * 1.08, Math.PI * 1.92); c.stroke(); break;
    case 'coffee': c.beginPath(); c.moveTo(-.7 * k, -.2 * k); c.lineTo(.45 * k, -.2 * k); c.lineTo(.35 * k, .6 * k); c.quadraticCurveTo(.3 * k, .8 * k, .1 * k, .8 * k); c.lineTo(-.45 * k, .8 * k); c.quadraticCurveTo(-.65 * k, .8 * k, -.65 * k, .6 * k); c.closePath(); c.stroke(); c.beginPath(); c.arc(.55 * k, .2 * k, .22 * k, -Math.PI / 2, Math.PI / 2); c.stroke(); L([[-.35, -.45], [-.25, -.7]]); L([[0, -.45], [.1, -.75]]); break;
    case 'chat': c.beginPath(); c.roundRect(-.85 * k, -.7 * k, 1.7 * k, 1.15 * k, .3 * k); c.stroke(); L([[-.35, .45], [-.55, .8], [0, .45]]); break;
    case 'tool': c.beginPath(); c.arc(.3 * k, -.3 * k, .38 * k, Math.PI * .9, Math.PI * 2.6); c.stroke(); L([[.05, -.05], [-.75, .75]]); break;
    case 'bolt': c.beginPath(); c.moveTo(.15 * k, -.9 * k); c.lineTo(-.5 * k, .1 * k); c.lineTo(-.02 * k, .1 * k); c.lineTo(-.15 * k, .9 * k); c.lineTo(.5 * k, -.1 * k); c.lineTo(.02 * k, -.1 * k); c.closePath(); c.stroke(); break;
    case 'doc': c.beginPath(); c.moveTo(-.6 * k, -.85 * k); c.lineTo(.25 * k, -.85 * k); c.lineTo(.6 * k, -.5 * k); c.lineTo(.6 * k, .85 * k); c.lineTo(-.6 * k, .85 * k); c.closePath(); c.stroke(); L([[-.3, -.15], [.3, -.15]]); L([[-.3, .2], [.3, .2]]); L([[-.3, .52], [.1, .52]]); break;
    case 'star': c.beginPath(); for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, r = (i % 2 ? .38 : .85) * k; c.lineTo(Math.cos(a) * r, Math.sin(a) * r) } c.closePath(); o.fill ? c.fill() : c.stroke(); break;
    case 'flag': L([[-.6, .9], [-.6, -.85]]); c.beginPath(); c.moveTo(-.6 * k, -.8 * k); c.quadraticCurveTo(0, -1 * k, .2 * k, -.75 * k); c.quadraticCurveTo(.45 * k, -.5 * k, .8 * k, -.7 * k); c.lineTo(.8 * k, .05 * k); c.quadraticCurveTo(.45 * k, .25 * k, .2 * k, 0); c.quadraticCurveTo(0, -.25 * k, -.6 * k, -.05 * k); c.stroke(); break;
    case 'gear': circ(0, 0, .3); for (let i = 0; i < 8; i++) { const a = i * TAU / 8; L([[Math.cos(a) * .55, Math.sin(a) * .55], [Math.cos(a) * .85, Math.sin(a) * .85]]) } circ(0, 0, .58); break;
    case 'home': L([[-.85, -.05], [0, -.8], [.85, -.05]]); L([[-.6, -.25], [-.6, .8], [.6, .8], [.6, -.25]]); L([[-.18, .8], [-.18, .3], [.18, .3], [.18, .8]]); break;
    case 'shield': c.beginPath(); c.moveTo(0, -.9 * k); c.lineTo(.75 * k, -.6 * k); c.quadraticCurveTo(.75 * k, .5 * k, 0, .9 * k); c.quadraticCurveTo(-.75 * k, .5 * k, -.75 * k, -.6 * k); c.closePath(); c.stroke(); L([[-.3, 0], [-.05, .25], [.35, -.2]]); break;
    case 'code': L([[-.4, -.5], [-.9, 0], [-.4, .5]]); L([[.4, -.5], [.9, 0], [.4, .5]]); L([[.15, -.7], [-.15, .7]]); break;
    case 'browser': box(-.9, -.7, 1.8, 1.4, .15); L([[-.9, -.35], [.9, -.35]]); circ(-.68, -.53, .06, 1); circ(-.5, -.53, .06, 1); circ(-.32, -.53, .06, 1); break;
    case 'apps': [[-.45, -.45], [.45, -.45], [-.45, .45], [.45, .45]].forEach(([a, b]) => box(a - .32, b - .32, .64, .64, .14)); break;
    case 'box': L([[-.8, -.35], [0, -.75], [.8, -.35], [.8, .45], [0, .85], [-.8, .45], [-.8, -.35]]); L([[-.8, -.35], [0, .05], [.8, -.35]]); L([[0, .05], [0, .85]]); break;
    case 'send': c.beginPath(); c.moveTo(-.85 * k, -.75 * k); c.lineTo(.9 * k, 0); c.lineTo(-.85 * k, .75 * k); c.lineTo(-.55 * k, 0); c.closePath(); c.stroke(); L([[-.55, 0], [.2, 0]]); break;
    case 'bulb': c.beginPath(); c.arc(0, -.2 * k, .58 * k, Math.PI * .8, Math.PI * 2.2); c.lineTo(.25 * k, .55 * k); c.lineTo(-.25 * k, .55 * k); c.closePath(); c.stroke(); L([[-.22, .8], [.22, .8]]); break;
    case 'q': circ(0, 0, .85); c.font = `700 ${k * 1.1}px ${SANS}`; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('?', 0, k * .05); break;
    case 'money': circ(0, 0, .85); c.font = `700 ${k * 1.1}px ${SANS}`; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('$', 0, k * .05); break;
    case 'wave': for (let i = -3; i <= 3; i++) { const hh = (.25 + .6 * Math.abs(Math.sin(i * 1.7 + (o.T || 0) * 8))) * (1 - Math.abs(i) * .1); L([[i * .26, -hh], [i * .26, hh]]) } break;
    case 'mic': box(-.3, -.85, .6, 1.05, .3); c.beginPath(); c.arc(0, -.1 * k, .55 * k, 0, Math.PI); c.stroke(); L([[0, .45], [0, .85]]); break;
    case 'store': L([[-.85, -.2], [-.7, -.8], [.7, -.8], [.85, -.2]]); c.beginPath(); c.moveTo(-.85 * k, -.2 * k); c.lineTo(.85 * k, -.2 * k); c.stroke(); L([[-.7, -.2], [-.7, .85], [.7, .85], [.7, -.2]]); L([[-.2, .85], [-.2, .35], [.2, .35], [.2, .85]]); break;
    case 'hotel': box(-.65, -.85, 1.3, 1.7, .08); for (let r2 = 0; r2 < 3; r2++) for (let q2 = 0; q2 < 2; q2++) box(-.38 + q2 * .5, -.6 + r2 * .42, .26, .22, .03, 1); L([[-.15, .85], [-.15, .55], [.15, .55], [.15, .85]]); break;
  }
  c.restore();
}
/** icon inside a soft rounded square tile */
function icoTile(c, name, x, y, s, o = {}) {
  c.save(); rr(c, x - s / 2, y - s / 2, s, s, s * .28); c.fillStyle = o.bg || C.clayXL; c.fill(); if (o.stroke) { c.strokeStyle = o.stroke; c.lineWidth = 1.5 * U; c.stroke() } c.restore();
  ico(c, name, x, y, s * .5, o.col || C.clayD, { T: o.T });
}

/* ---------- pointer cursor ---------- */
function cursor(c, x, y, T, click = -9, o = {}) {
  const s = (o.s || 34) * U, cp = P(T, click, click + .35), sq = click > -1 && T >= click && T < click + .35 ? 1 - .15 * Math.sin(cp * Math.PI) : 1;
  if (click > -1 && T >= click && T < click + .6) { const rp = P(T, click, click + .6); c.save(); c.strokeStyle = o.ring || C.clay; c.globalAlpha = 1 - rp; c.lineWidth = 3 * U; c.beginPath(); c.arc(x, y, 10 * U + 34 * U * E.outCubic(rp), 0, TAU); c.stroke(); c.restore() }
  c.save(); c.translate(x, y); c.scale(sq, sq); c.beginPath(); c.moveTo(0, 0); c.lineTo(0, s); c.lineTo(s * .27, s * .76); c.lineTo(s * .45, s * 1.12); c.lineTo(s * .6, s * 1.05); c.lineTo(s * .43, s * .7); c.lineTo(s * .75, s * .7); c.closePath();
  c.shadowColor = 'rgba(0,0,0,.25)'; c.shadowBlur = 8 * U; c.shadowOffsetY = 3 * U; c.fillStyle = o.fill || C.ink; c.fill(); c.shadowColor = 'transparent'; c.strokeStyle = '#fff'; c.lineWidth = 2 * U; c.stroke(); c.restore();
}

/* ---------- phone mockup ---------- */
/** draws an iPhone-like frame centred at cx,cy with screen height h. id: image or clip id */
function phone(c, id, cx, cy, h, T, o = {}) {
  const sw = h * (900 / 1950), bez = h * .022, r = h * .085, x = cx - sw / 2, y = cy - h / 2;
  c.save(); if (o.alpha != null) c.globalAlpha *= o.alpha;
  c.translate(cx, cy); c.rotate(o.rot || 0); c.scale(o.scale ?? 1, o.scale ?? 1); c.translate(-cx, -cy);
  c.shadowColor = o.shadowCol || 'rgba(0,0,0,.35)'; c.shadowBlur = 60 * U; c.shadowOffsetY = 26 * U;
  rr(c, x - bez, y - bez, sw + bez * 2, h + bez * 2, r + bez); c.fillStyle = o.frame || '#121212'; c.fill(); c.shadowColor = 'transparent';
  c.strokeStyle = 'rgba(255,255,255,.12)'; c.lineWidth = 1.5 * U; c.stroke();
  const src = MEDIA[id];
  if (src) media(c, id, o.lt ?? 0, x, y, sw, h, { radius: r, zoom: o.zoom || 1, focus: o.focus, speed: o.speed, loop: o.loop, in: o.in });
  else { rr(c, x, y, sw, h, r); c.fillStyle = '#fff'; c.fill() }
  if (o.island !== false) { rr(c, cx - sw * .14, y + h * .018, sw * .28, h * .028, h * .014); c.fillStyle = '#000'; c.fill() }
  c.restore();
  return { x, y, w: sw, h };
}
/** draw a normalized sub-rectangle [sx,sy,sw,sh] (0..1) of an image/clip into a rounded card (magnifier panel) */
function zoomPanel(c, id, rect, x, y, w, T, o = {}) {
  const m = MEDIA[id]; if (!m) return 0; const [sx, sy, sw, sh] = rect; const h = w * (sh * m.h) / (sw * m.w);
  const img = m.type === 'image' ? getURL(m.src) : getURL(frameURL(m, clipIndex(m, o.lt || 0, o)));
  c.save(); if (o.alpha != null) c.globalAlpha *= o.alpha;
  c.shadowColor = 'rgba(0,0,0,.28)'; c.shadowBlur = 50 * U; c.shadowOffsetY = 20 * U; rr(c, x, y, w, h, o.r ?? 20 * U); c.fillStyle = '#fff'; c.fill(); c.shadowColor = 'transparent';
  c.clip(); if (img) c.drawImage(img, sx * m.w, sy * m.h, sw * m.w, sh * m.h, x, y, w, h); c.restore();
  if (o.stroke) { c.save(); c.strokeStyle = o.stroke; c.lineWidth = 3 * U; rr(c, x, y, w, h, o.r ?? 20 * U); c.stroke(); c.restore() }
  return h;
}

/* ---------- chat bubbles ---------- */
let BUBW = 0;
function bubble(c, x, y, s, maxW, o = {}) {
  const f = o.font || fN(28 * U, 450), lh = (o.lh || 1.35) * parseFloat(f.match(/(\d+(\.\d+)?)px/)[1]), pad = o.pad || 24 * U;
  const lines = wrap(c, s, f, maxW - pad * 2), tw = Math.max(...lines.map(l => measure(c, l, f))), w = tw + pad * 2, h = lines.length * lh + pad * 1.5;
  const user = o.who === 'user', x0 = user ? x - w : x, p = o.p ?? 1; BUBW = w; if (p <= 0) return h;
  pop(c, user ? x : x0, y + h, E.outBack(P(p, 0, 1)), () => {
    c.save(); if (o.shadow !== false) { c.shadowColor = 'rgba(0,0,0,.12)'; c.shadowBlur = 24 * U; c.shadowOffsetY = 8 * U }
    rr(c, x0, y, w, h, Math.min(26 * U, h / 2)); c.fillStyle = o.bg || (user ? C.ink : C.paper); c.fill(); c.restore();
    const tc = o.fg || (user ? '#fff' : C.ink), chars = o.type != null ? Math.floor(o.type) : 1e9; let used = 0;
    lines.forEach((l, i) => { const vis = l.slice(0, Math.max(0, chars - used)); used += l.length + 1; txt(c, vis, x0 + pad, y + pad * .75 + lh * (i + .5) + 1, { font: f, color: tc, base: 'middle' }) });
  }, { from: .7, dy: 20 * U });
  return h;
}

/* ---------- chapter chrome ---------- */
const CHAPTERS = [];  // [startT, endT, '01', 'Title']
let SCENE_DARK = [];   // filled by timeline: [{start,end,dark}]
function isDark(T) { let d = true; for (const s of SCENE_DARK) if (T >= s.start) d = s.dark; return d }
/** thin progress bar along the bottom (no text headings: the user asked for none). Set PROGRESS_FROM to the end of the hook. */
let PROGRESS_FROM = 8;
window.CHROME = (c, T) => {
  if (T < PROGRESS_FROM || T > DUR - 6) return;
  const a = P(T, PROGRESS_FROM, PROGRESS_FROM + 1) * (1 - P(T, DUR - 7, DUR - 6)), dark = isDark(T);
  c.globalAlpha = a * .5; c.fillStyle = dark ? C.creamFaint : C.line; c.fillRect(0, H - 5 * U, W, 5 * U);
  c.globalAlpha = a; c.fillStyle = dark ? C.cream : C.ink; c.fillRect(0, H - 5 * U, W * T / DUR, 5 * U);
};
