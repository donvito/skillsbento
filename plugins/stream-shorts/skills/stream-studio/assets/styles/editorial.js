/* ===== editorial primitives (shared by the grok + claude styles) =====
   Serif display + italic emphasis, Inter body, mono kickers, paper / dark cards, hand-drawn strokes.
   Colours come from ST (the style's "tokens"); fonts from fonts/display.ttf, display-italic.ttf, body.ttf, mono.ttf.
   Every helper that draws media checks hasMedia(id) first, so a missing logo is skipped, not drawn as a placeholder. */
const SERIF = '"Display"', ITAL = '"DisplayIt"';
const fnt = (w, px, fam) => `${w} ${px}px ${fam}`;

function shade(c, a = .16, b = 34, y = 12) { c.shadowColor = `rgba(0,0,0,${a})`; c.shadowBlur = b; c.shadowOffsetY = y }
/** serif headline. o: {it, align, color, s, alpha, dy, rot, halo:false, haloCol, ls} → width */
function serif(c, s, x, y, px, o = {}) {
  const sc = o.s ?? 1, a = o.alpha ?? 1; if (sc <= .001 || a <= .002) return 0;
  c.save(); c.translate(x, y + (o.dy || 0)); c.rotate(o.rot || 0); c.scale(sc, sc); c.globalAlpha *= a;
  c.font = fnt(600, px, o.it ? ITAL : SERIF); c.letterSpacing = (o.ls ?? -px * .025) + 'px'; c.textAlign = o.align || 'center'; c.textBaseline = 'middle';
  if (o.halo !== false) { c.shadowColor = o.haloCol || ST.halo; c.shadowBlur = px * .45 }
  c.fillStyle = o.color || ST.ink; c.fillText(s, 0, 0);
  const w = c.measureText(s).width; c.restore(); return w;
}
/** measure: serif (it = italic) or, with fam, any family (letter-spacing 0) */
function sw(c, s, px, it = false, w = 600, fam) { c.save(); c.font = fnt(w, px, fam || (it ? ITAL : SERIF)); c.letterSpacing = (fam ? 0 : -px * .025) + 'px'; const m = c.measureText(s).width; c.restore(); return m }
function body(c, s, x, y, px, col = ST.ink, o = {}) {
  c.save(); c.globalAlpha *= o.alpha ?? 1; c.font = fnt(o.w || 500, px, FS); c.letterSpacing = (o.ls || 0) + 'px'; c.fillStyle = col; c.textAlign = o.align || 'left'; c.textBaseline = 'middle'; c.fillText(s, x, y); c.restore();
}
function mono(c, s, x, y, px, col = ST.grey, o = {}) { label(c, s, x, y, px, col, { font: FJ, weight: 700, ls: o.ls ?? 3, align: o.align || 'left', alpha: o.alpha ?? 1 }) }
/** entrance: rise + settle. returns {a, dy, s}; zero before t0 */
function rise(T, t0, d = .42) { if (T < t0) return { a: 0, dy: 0, s: 0 }; const p = E.outBack(P(T, t0, t0 + d)); return { a: clamp((T - t0) / .16), dy: (1 - p) * 34, s: lerp(.9, 1, p) } }
/** draw fn() at (x,y) with the rise entrance from global time t0 */
function inn(c, T, t0, x, y, fn, d = .42) {
  const p = rise(T, t0, d); if (p.a <= 0) return;
  c.save(); c.globalAlpha *= p.a; c.translate(x, y + p.dy); c.scale(p.s, p.s); fn(); c.restore();
}
/** mono kicker pill centred on x. o: {light, dot (pulsing red dot), px} */
function kicker(c, T, t0, s, x, y, o = {}) {
  const p = rise(T, t0); if (p.a <= 0) return;
  c.save(); c.globalAlpha *= p.a; c.translate(x, y + p.dy);
  const px = o.px || 26, dot = o.dot ? 34 : 0;
  c.font = fnt(700, px, FJ); c.letterSpacing = '3px'; const w = c.measureText(s).width + 56 + dot, h = px * 2.5;
  c.save(); shade(c, .22, 22, 6); rr(c, -w / 2, -h / 2, w, h, h / 2, o.light ? ST.paper : ST.ink); c.restore();
  if (o.dot) { c.fillStyle = ST.red; c.globalAlpha *= .55 + .45 * Math.sin(T * 7); c.beginPath(); c.arc(-w / 2 + 34, 0, 9, 0, 7); c.fill(); c.globalAlpha = p.a }
  c.fillStyle = o.light ? ST.ink : ST.paper; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(s, dot / 2, 1);
  c.restore();
}
/** white/ivory paper card with a soft shadow */
function paper(c, x, y, w, h, o = {}) { c.save(); shade(c, o.sh ?? .2, 40, 14); rr(c, x, y, w, h, o.r ?? 28, o.fill || ST.paper); c.restore(); if (o.line !== false) rr(c, x, y, w, h, o.r ?? 28, null, ST.line, 2) }
/** dark UI card (Grok-black / Claude ink) with a hairline */
function dark(c, x, y, w, h, o = {}) { c.save(); shade(c, .35, 46, 16); rr(c, x, y, w, h, o.r ?? 30, o.fill || ST.card); c.restore(); rr(c, x, y, w, h, o.r ?? 30, null, ST.hair, 2) }
/** app icon / avatar. o: {s, rot, alpha, round, bg, ringCol} — skipped if the image id is missing */
function logo(c, id, x, y, size, o = {}) {
  const s = o.s ?? 1; if (s <= .001 || !hasMedia(id)) return;
  c.save(); c.translate(x, y); c.rotate(o.rot || 0); c.scale(s, s); c.globalAlpha *= o.alpha ?? 1;
  const r = size * (o.round ? .5 : .24);
  c.save(); shade(c, .25, 26, 8); rr(c, -size / 2, -size / 2, size, size, r, o.bg || '#000'); c.restore();
  c.save(); c.beginPath(); c.roundRect(-size / 2, -size / 2, size, size, r); c.clip(); image(c, id, -size / 2, -size / 2, size, size, { fit: 'cover' }); c.restore();
  if (o.ringCol) rr(c, -size / 2, -size / 2, size, size, r, null, o.ringCol, Math.max(2, size * .015));
  c.restore();
}
/* ---- hand-drawn strokes (p = 0..1 draw-on) ---- */
function scribble(c, x0, x1, y, p, col = ST.accent, lw = 10, seed = 3) {
  if (p <= 0) return; c.save(); c.strokeStyle = col; c.lineWidth = lw; c.lineCap = 'round'; c.beginPath();
  const n = 28; for (let i = 0; i <= n * p; i++) { const u = i / n, x = lerp(x0, x1, u), yy = y + Math.sin(u * 8 + seed) * lw * .35 + (u - .5) * -lw * .6; i ? c.lineTo(x, yy) : c.moveTo(x, yy) }
  c.stroke(); c.restore();
}
/** bowed line from (x0,y0) to (x1,y1): strikes, arrows, X marks */
function stroke2(c, x0, y0, x1, y1, p, col = ST.accent, lw = 12, bow = 14) {
  if (p <= 0) return; c.save(); c.strokeStyle = col; c.lineWidth = lw; c.lineCap = 'round'; c.beginPath();
  const n = 20; for (let i = 0; i <= n * p; i++) { const u = i / n, x = lerp(x0, x1, u), y = lerp(y0, y1, u) + Math.sin(u * Math.PI) * bow; i ? c.lineTo(x, y) : c.moveTo(x, y) }
  c.stroke(); c.restore();
}
/** loose hand-drawn ellipse with overshoot (circle a word) */
function ring(c, cx, cy, rx, ry, p, col = ST.accent, lw = 7, seed = 1) {
  if (p <= 0) return; c.save(); c.strokeStyle = col; c.lineWidth = lw; c.lineCap = 'round'; c.beginPath();
  const a0 = -2.2, n = 60, tot = Math.PI * 2.15;
  for (let i = 0; i <= n * p; i++) { const u = i / n, a = a0 + u * tot, k = 1 + .04 * Math.sin(u * 5 + seed) + .05 * u; const x = cx + Math.cos(a) * rx * k, y = cy + Math.sin(a) * ry * k; i ? c.lineTo(x, y) : c.moveTo(x, y) }
  c.stroke(); c.restore();
}
/** round checkbox; p = 0..1 fill-in */
function tick(c, x, y, r, p, fill = ST.ink, mark = ST.paper) {
  rr(c, x - r, y - r, r * 2, r * 2, r, null, p > 0 ? fill : ST.line.replace(/[\d.]+\)$/, '.3)'), 3);
  if (p <= 0) return; const k = E.outBack(p);
  c.save(); c.translate(x, y); c.scale(k, k); c.fillStyle = fill; c.beginPath(); c.arc(0, 0, r, 0, 7); c.fill();
  c.strokeStyle = mark; c.lineWidth = r * .24; c.lineCap = 'round'; c.lineJoin = 'round'; c.beginPath(); c.moveTo(-r * .42, 0); c.lineTo(-r * .1, r * .32); c.lineTo(r * .45, -r * .32); c.stroke(); c.restore();
}
/** chat bubble anchored at its bottom tail corner (x = left edge, or right edge when right=true). o: {dark, px} */
function bubble(c, T, t0, x, y, s, right, o = {}) {
  const px = o.px || 36, w = sw(c, s, px, false, 500, FS) + 64, h = px * 2.05;
  inn(c, T, t0, x, y, () => {
    const ox = right ? -w : 0;
    c.save(); shade(c, .2, 26, 8); rr(c, ox, -h, w, h, [30, 30, right ? 6 : 30, right ? 30 : 6], o.dark ? ST.card : ST.paper); c.restore();
    body(c, s, ox + 32, -h / 2 + 1, px, o.dark ? ST.cardInk : ST.ink);
  }, .36);
}
/** small "ILLUSTRATIVE" tag for mock UIs */
function illus(c, x, y, align = 'right', col) { mono(c, 'ILLUSTRATIVE', x, y, 18, col || ST.grey, { align, ls: 2 }) }
/** flip card: blank front, flips to emoji + label at global time tf */
function flip(c, T, t0, tf, x, y, w, h, em, s) {
  const p = rise(T, t0, .35); if (p.a <= 0) return;
  const fp = P(T, tf, tf + .32), sx = Math.max(.02, Math.abs(Math.cos(fp * Math.PI))), back = fp > .5;
  c.save(); c.globalAlpha *= p.a; c.translate(x, y + p.dy); c.scale(sx * p.s, p.s);
  if (!back) { paper(c, -w / 2, -h / 2, w, h, { fill: ST.paper2, r: 26 }); serif(c, '?', 0, 4, 84, { color: ST.line.replace(/[\d.]+\)$/, '.25)'), halo: false }) }
  else { paper(c, -w / 2, -h / 2, w, h, { r: 26 }); if (em) emo(c, em, 0, -34, 60); serif(c, s, 0, em ? 44 : 0, s.length > 9 ? 40 : 46, { halo: false }) }
  c.restore();
}
/** real footage in a floating phone frame. o: {focus, zoom, in, tilt} — skipped if the clip id is missing */
function phone(c, T, t0, id, lt, x, y, w, h, o = {}) {
  if (!hasMedia(id)) return;
  const p = E.outBack(P(T, t0, t0 + .5)), fl = Math.sin(T * 2) * 6;
  c.save(); c.translate(x, y + fl + (1 - p) * 260); c.rotate((1 - p) * -.08 + (o.tilt ?? -.015)); c.globalAlpha *= clamp((T - t0) / .15);
  c.save(); shade(c, .5, 70, 24); rr(c, -w / 2, -h / 2, w, h, w * .13, '#1b1b1d'); c.restore();
  rr(c, -w / 2, -h / 2, w, h, w * .13, null, 'rgba(255,255,255,.12)', 3);
  clip(c, id, lt, -w / 2 + 18, -h / 2 + 18, w - 36, h - 36, { fit: 'cover', focus: o.focus || [.5, .45], zoom: o.zoom || 1.15, in: o.in || 0, radius: w * .1 });
  c.restore();
}
/** pull-quote card: italic serif quote + small attribution */
function quote(c, T, t0, x, y, q, by, o = {}) {
  inn(c, T, t0, x, y, () => {
    const w = o.w || 900, px = o.px || 44;
    paper(c, -w / 2, -95, w, 190, { r: 30 });
    serif(c, q, 0, -22, px, { it: true, halo: false });
    if (by) body(c, by, 0, 42, 26, ST.grey2, { align: 'center' });
  }, .4);
}
/** scrolling mono band (e.g. a list of roles), slightly rotated */
function marquee(c, T, t0, s, y, o = {}) {
  const a = clamp((T - t0) / .3); if (a <= 0) return;
  c.save(); c.globalAlpha *= a; c.translate(0, y); c.rotate(o.rot ?? -.02);
  c.save(); shade(c, .3, 24, 8); c.fillStyle = o.bg || ST.ink; c.fillRect(-40, -38, W + 80, 76); c.restore();
  c.font = fnt(700, 28, FJ); c.letterSpacing = '4px'; c.fillStyle = o.fg || ST.paper; c.textBaseline = 'middle'; c.textAlign = 'left';
  const mw = c.measureText(s).width, off = ((T - t0) * (o.speed || 220)) % mw;
  for (let x = -off; x < W; x += mw) c.fillText(s, x, 2);
  c.restore();
}
