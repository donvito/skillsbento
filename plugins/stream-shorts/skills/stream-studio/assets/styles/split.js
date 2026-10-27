/* ===== split layout, editorial look (overrides the stock kit's neon stage / facecam / captions / end card) =====
   Top half: paper stage (ST.stage) with a fine dot grid, a slow orbit line and a paper wipe between beats.
   Bottom half: facecam. Captions: paper chips with ink serif, *hot* words in ST.hot. Soft shadows, no neon.
   CL = the classic palette names used by earlier editorial pages (paper, ivory, oat, ink, slate, cloud, orange, crail…). */
const CL = Object.assign({ paper: ST.paper, ivory: ST.stage, oat: ST.paper2, ink: ST.ink, slate: ST.grey2, cloud: ST.grey, cloudL: ST.cardDim,
  orange: ST.accent, crail: ST.hot, kraft: ST.accent, olive: ST.green, sky: ST.grey, fig: ST.accent, red: ST.red }, ST.pal || {});
function softShadow(c, a = .14, b = 34, y = 12) { c.shadowColor = `rgba(20,20,19,${a})`; c.shadowBlur = b; c.shadowOffsetY = y }

function big(c, s, x, y, size, o = {}) {
  const sc = o.s ?? 1, a = o.alpha ?? 1; if (sc <= .001 || a <= .002) return 0;
  c.save(); c.translate(x, y); c.rotate(o.rot || 0); c.scale(sc, sc); c.globalAlpha *= a;
  c.font = `${o.weight || 600} ${size}px ${o.font || FA}`; c.letterSpacing = (o.ls ?? -size * .02) + 'px';
  c.textAlign = o.align || 'center'; c.textBaseline = 'middle';
  if (o.stroke) { c.lineJoin = 'round'; c.strokeStyle = o.stroke; c.lineWidth = o.lw ?? size * .12; c.strokeText(s, 0, 0) }
  c.fillStyle = o.color || CL.ink; c.fillText(s, 0, 0);
  const w = c.measureText(s).width; c.restore(); return w;
}
function card(c, x, y, w, h, col = CL.orange, o = {}) {
  c.save(); softShadow(c, .12, 30, 10); rr(c, x, y, w, h, o.r ?? 26, o.fill || CL.paper); c.restore();
  rr(c, x, y, w, h, o.r ?? 26, null, col, o.lw ?? 3);
}
function stamp(c, s, x, y, size, col, t, t0, rot = -.06) {
  const k = slam(t, t0); if (!k) return;
  c.save(); c.translate(x, y); c.rotate(rot); c.scale(k, k); c.globalAlpha *= clamp((t - t0) / .06);
  c.font = `600 ${size}px ${FA}`; const w = c.measureText(s).width + size * .8, h = size * 1.35;
  softShadow(c, .2, 24, 8); rr(c, -w / 2, -h / 2, w, h, h / 2, col); c.shadowColor = 'transparent';
  c.fillStyle = CL.paper; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(s, 0, size * .04); c.restore();
}
function bar(c, x, y, w, h, p, col, bg = 'rgba(20,20,19,.07)') { rr(c, x, y, w, h, h / 2, bg); if (p > 0) rr(c, x, y, Math.max(h, w * clamp(p)), h, h / 2, col) }

function stageBg(c, T, tint = CL.orange) {
  c.fillStyle = CL.ivory; c.fillRect(-20, -20, W + 40, SEAM + 20);
  const g = c.createRadialGradient(W * .78, SEAM * .1, 0, W * .78, SEAM * .1, 900);
  g.addColorStop(0, hexA(tint, .16)); g.addColorStop(1, hexA(tint, 0)); c.fillStyle = g; c.fillRect(0, 0, W, SEAM);
  c.save(); c.fillStyle = 'rgba(20,20,19,.07)'; const off = (T * 6) % 36;
  for (let y = 18 - off; y < SEAM; y += 36) for (let x = 18; x < W; x += 36) { c.beginPath(); c.arc(x, y, 1.6, 0, 7); c.fill() }
  c.restore();
  c.save(); c.strokeStyle = hexA(tint, .22); c.lineWidth = 2; c.beginPath(); c.arc(W * .86, SEAM * .14, 260 + Math.sin(T * .8) * 10, 0, 7); c.stroke(); c.restore();
}
function runBeats(c, T, beats) {
  c.save(); c.beginPath(); c.rect(0, 0, W, SEAM); c.clip();
  for (let i = 0; i < beats.length; i++) {
    const b = beats[i], end = i + 1 < beats.length ? beats[i + 1].a : Infinity;
    if (T < b.a || T >= end) continue;
    const lt = T - b.a;
    stageBg(c, T, b.tint || CL.orange);
    c.save();
    if (i > 0) { const k = 1 + .05 * (1 - E.outExpo(P(lt, 0, .35))), dy = 40 * (1 - E.outExpo(P(lt, 0, .35))); c.translate(W / 2, SEAM / 2 + dy); c.scale(k, k); c.translate(-W / 2, -SEAM / 2) }
    b.draw(c, lt, T, end - b.a); c.restore();
    if (i > 0 && lt < .28) { const p = E.ioCubic(lt / .28), x = lerp(0, W + 60, p);
      c.fillStyle = CL.ivory; c.fillRect(x, 0, W, SEAM); c.fillStyle = b.tint || CL.orange; c.fillRect(x - 14, 0, 14, SEAM) }
  }
  c.restore();
}
function faceCam(c, T, punches = [], o = {}) {
  let z = 1.02 + .05 * P(T, 0, DUR);
  for (const [t0, a] of punches) if (T >= t0) z += a * Math.exp(-(T - t0) * 5) * E.outExpo(P(T, t0, t0 + .08));
  clip(c, 'face', Math.min(T, o.end ?? 1e9), 0, SEAM, W, H - SEAM, { zoom: z, focus: o.focus || BR.faceFocus });
  const g = c.createLinearGradient(0, H - 260, 0, H); g.addColorStop(0, 'rgba(20,20,19,0)'); g.addColorStop(1, 'rgba(20,20,19,.5)'); c.fillStyle = g; c.fillRect(0, H - 260, W, 260);
  if (BR.watermark && BR.handle) label(c, BR.handle, W / 2, H - 70, 34, 'rgba(250,249,245,.85)', { align: 'center', weight: 600 });
  c.fillStyle = CL.ivory; c.fillRect(0, SEAM - 5, W, 10); c.fillStyle = CL.orange; c.fillRect(0, SEAM - 2, W * .18, 4);
}
/* captions: paper chips with ink serif, hot words in ST.hot */
function captions(c, T, caps, o = {}) {
  const y0 = o.y ?? SEAM + 150, size = o.size ?? 84;
  for (let i = 0; i < caps.length; i++) {
    const [a, b, s] = caps[i]; if (T < a || T >= b) continue;
    const lt = T - a, k = i === 0 && a === 0 ? 1 : lerp(.8, 1, E.outBack(P(lt, 0, .18))), al = i === 0 && a === 0 ? 1 : clamp(lt / .08);
    const words = s.split(' ').map(w => ({ hot: /\*/.test(w), w: w.replace(/\*/g, '') }));
    c.save(); c.font = `600 ${size}px ${FA}`; c.letterSpacing = (-size * .015) + 'px';
    const sp = size * .26; words.forEach(wd => wd.width = c.measureText(wd.w).width);
    const tw = words.reduce((s, w) => s + w.width, 0) + sp * (words.length - 1), bw = tw + size * .9, bh = size * 1.45;
    c.globalAlpha = al; c.translate(W / 2, y0); c.scale(k, k);
    softShadow(c, .3, 30, 10); rr(c, -bw / 2, -bh / 2, bw, bh, 22, CL.paper); c.shadowColor = 'transparent';
    let x = -tw / 2; c.textBaseline = 'middle'; c.textAlign = 'left';
    for (const wd of words) { c.fillStyle = wd.hot ? (o.hot || CL.crail) : CL.ink; c.fillText(wd.w, x, size * .02); x += wd.width + sp }
    c.restore();
  }
}
function progress(c, T, end) { c.fillStyle = 'rgba(20,20,19,.08)'; c.fillRect(0, 0, W, 10); c.fillStyle = CL.orange; c.fillRect(0, 0, W * clamp(T / end), 10) }
function endCard(c, t, T, o = {}) {
  bgFill(c, CL.ivory);
  c.save(); c.fillStyle = 'rgba(20,20,19,.06)'; for (let y = 18; y < H; y += 36) for (let x = 18; x < W; x += 36) { c.beginPath(); c.arc(x, y, 1.6, 0, 7); c.fill() } c.restore();
  const cx = W / 2, cy = 640, r = 250 * E.outBack(P(t, 0, .35));
  if (r > 1) {
    c.save(); softShadow(c, .2, 50, 16); c.beginPath(); c.arc(cx, cy, r + 12, 0, 7); c.fillStyle = CL.orange; c.fill(); c.restore();
    c.save(); c.beginPath(); c.arc(cx, cy, r, 0, 7); c.clip(); clip(c, 'face', o.faceT ?? 0, cx - r * 1.125, cy - r, r * 2.25, r * 2, { focus: BR.faceFocus }); c.restore();
    if (BR.ring) ringText(c, ' ' + BR.ring.replace(/\s*•?\s*$/, '') + ' •', cx, cy, r + 60, t * .8 - 1.5, font(600, 30, FJ), CL.slate, P(t, .15, .4));
  }
  const live = BR.live ? pop(t, .12) : 0; if (live > 0) { c.save(); c.translate(cx, cy + r + 10); c.scale(live, live); rr(c, -92, -34, 184, 68, 34, CL.crail); c.fillStyle = CL.paper; c.beginPath(); c.arc(-50, 0, 11, 0, 7); c.fill(); label(c, 'LIVE', 12, 2, 36, CL.paper, { align: 'center', weight: 700 }); c.restore() }
  const cta = o.line1 || (o.edu ? BR.ctaEdu : BR.cta), handle = BR.handle || '';
  big(c, cta, cx, 1110, Math.min(104, fit(c, cta, 600, FA, W - 140, 104)), { s: pop(t, .18), color: CL.ink });
  if (handle) big(c, handle, cx, 1245, Math.min(110, fit(c, handle, 600, FA, W - 120, 110)), { s: pop(t, .28), color: CL.crail });
  const tag = o.line3 ?? BR.tagline; if (tag) label(c, tag, cx, 1360, 38, CL.cloud, { align: 'center', weight: 500, alpha: P(t, .4, .6) });
  if (o.emoji) emo(c, o.emoji, cx + 330, 450, 150, { s: pop(t, .35), rot: Math.sin(T * 5) * .12 });
}
