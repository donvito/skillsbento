/* ===== overlay layout: full-frame camera + motion graphics on top (no split-screen box) =====
   The camera plate is the clip 'cam' (built by `short.py cut` for layout "overlay": the source cropped to cover 1080x1920).
   Overlays live in the wall area above the head (y 0..~560) and the side strips; captions sit on the chest (~y 1480).
   A soft wash (ST.wash) over the wall keeps ink serif readable; a dark foot keeps the handle readable. */

/** camera plate. o: {punches:[[t,amt]], bw:[[a,b]] (black & white ranges, e.g. a flashback), hook:{until, zoom, focusY},
    dim:[[a,b,amt]] (darken, e.g. under a full-screen demo), wash:true|false|fn(T)→0..1, filter} */
function overlayCam(c, T, o = {}) {
  let z = 1.0 + .06 * P(T, 0, typeof SPEECH !== 'undefined' ? SPEECH : DUR);
  for (const [t0, a] of o.punches || []) if (T >= t0) z += a * Math.exp(-(T - t0) * 2.6) * E.outCubic(P(T, t0, t0 + .12));
  let fy = .5;
  if (o.hook) { const hk = 1 - E.ioCubic(P(T, o.hook.until - .55, o.hook.until + .25)); z *= 1 + (o.hook.zoom ?? .14) * hk; fy = lerp(.5, o.hook.focusY ?? .06, hk) }
  const base = { fit: 'cover', zoom: z, focus: [.5, fy] };
  clip(c, 'cam', T, 0, 0, W, H, { ...base, filter: o.filter || 'contrast(1.05) saturate(.94)' });
  let bw = 0;
  for (const [a, b] of o.bw || []) if (T >= a && T < b + .35) bw = Math.max(bw, T < b ? E.ioCubic(P(T, a, a + .3)) : 1 - E.ioCubic(P(T, b, b + .35)));
  if (bw > 0) clip(c, 'cam', T, 0, 0, W, H, { ...base, filter: 'grayscale(1) contrast(1.12) brightness(1.02)', alpha: bw });
  const wa = typeof o.wash === 'function' ? o.wash(T) : o.wash === false ? 0 : 1;
  if (wa > 0) {
    const g = c.createLinearGradient(0, 0, 0, 700);
    g.addColorStop(0, `rgba(${ST.wash},${.66 * wa})`); g.addColorStop(.55, `rgba(${ST.wash},${.32 * wa})`); g.addColorStop(1, `rgba(${ST.wash},0)`);
    c.fillStyle = g; c.fillRect(0, 0, W, 700);
  }
  const g2 = c.createLinearGradient(0, 1300, 0, H); g2.addColorStop(0, 'rgba(0,0,0,0)'); g2.addColorStop(1, 'rgba(0,0,0,.6)'); c.fillStyle = g2; c.fillRect(0, 1300, W, H - 1300);
  if (bw > 0) { const r = rng(Math.floor(T * 30)); c.save(); c.globalAlpha = .07 * bw; for (let i = 0; i < 900; i++) { c.fillStyle = r() > .5 ? '#fff' : '#000'; c.fillRect(r() * W, r() * H, 2, 2) } c.restore() }
  for (const [a] of o.bw || []) if (T >= a && T < a + .3) { c.fillStyle = `rgba(255,255,255,${.55 * (1 - P(T, a, a + .3))})`; c.fillRect(0, 0, W, H) }
  for (const [a, b, amt] of o.dim || []) if (T >= a && T < b) { c.fillStyle = `rgba(8,8,9,${(amt ?? .72) * E.ioCubic(P(T, a, a + .25))})`; c.fillRect(0, 0, W, H) }
}
/** run overlay beats: [{a, draw(c, t, T, dur)}]. Each beat fades + drifts up over its last .16s. Beat 0 must be complete at T=0. */
function runOverlay(c, T, beats, end) {
  for (let i = 0; i < beats.length; i++) {
    const b = beats[i], e = i + 1 < beats.length ? beats[i + 1].a : (end ?? DUR);
    if (T < b.a || T >= e) continue;
    const lt = T - b.a, dur = e - b.a, out = P(lt, dur - .16, dur);
    c.save(); if (out > 0) { c.globalAlpha = 1 - E.inCubic(out); c.translate(0, -26 * E.inCubic(out)) }
    b.draw(c, lt, T, dur); c.restore();
  }
}
/** captions: paper chip, serif (hot words *italic* in ST.hot), words darken as they are spoken.
    caps = [[t0, t1, 'text with *hot* words']]; words = WORDS ([word, start, end] from src/words.json).
    Display words light up in proportion to the source words spoken inside [t0, t1), so caption text can be edited freely.
    o: {y, px, hideUntil} */
function overlayCaptions(c, T, caps, words, o = {}) {
  const Y = o.y ?? 1478;
  for (let i = 0; i < caps.length; i++) {
    const [a, b, s] = caps[i]; if (T < a || T >= b || T < (o.hideUntil ?? -1)) continue;
    const toks = s.split(' ').filter(Boolean).map(w => ({ hot: w.includes('*'), s: w.replace(/\*/g, '') }));
    const src = (words || []).filter(w => w[1] >= a - .05 && w[1] < b), said = src.filter(w => T >= w[1] - .04).length;
    const lit = src.length ? Math.ceil(said / src.length * toks.length) : toks.length;
    let px = o.px || 66; const gap = () => px * .27, tot = () => toks.reduce((n, w) => n + sw(c, w.s, px, w.hot), 0) + gap() * (toks.length - 1);
    while (tot() > 880 && px > 46) px -= 2;
    const total = tot(), lt = T - a, k = a === 0 ? 1 : lerp(.92, 1, E.outBack(P(lt, 0, .2))), al = a === 0 ? 1 : clamp(lt / .1);
    const cw = total + px, ch = px * 1.5;
    c.save(); c.globalAlpha = al; c.translate(W / 2, Y); c.scale(k, k);
    c.save(); shade(c, .35, 30, 10); rr(c, -cw / 2, -ch / 2, cw, ch, 22, ST.chip); c.restore();
    let x = -total / 2;
    toks.forEach((w, j) => {
      const ww = sw(c, w.s, px, w.hot);
      c.font = fnt(600, px, w.hot ? ITAL : SERIF); c.letterSpacing = (-px * .025) + 'px'; c.textAlign = 'left'; c.textBaseline = 'middle';
      c.fillStyle = j < lit ? (w.hot ? ST.hot : ST.chipInk) : ST.chipDim; c.fillText(w.s, x, px * .03);
      x += ww + gap();
    });
    c.restore();
  }
}
function overlayProgress(c, T, end) { c.fillStyle = 'rgba(0,0,0,.12)'; c.fillRect(0, 0, W, 6); c.fillStyle = ST.progress; c.fillRect(0, 0, W * clamp(T / end), 6) }
function overlayHandle(c) { if (BR.handle) body(c, BR.handle, W / 2, 1600, 30, 'rgba(255,255,255,.85)', { align: 'center', w: 600 }) }
/** end card: style background, face in a ring, ring text, LIVE pill, serif CTA + italic handle. o: {faceT, start, logos:[id,id]} */
function overlayEnd(c, t, T, o = {}) {
  bgFill(c, ST.endBg);
  c.save(); c.fillStyle = ST.endDot; const off = (T * 6) % 36; for (let y = 18 - off; y < H; y += 36) for (let x = 18; x < W; x += 36) { c.beginPath(); c.arc(x, y, 1.6, 0, 7); c.fill() } c.restore();
  const cx = W / 2, cy = 640, r = 250 * E.outBack(P(t, 0, .35));
  if (r > 1) {
    c.save(); shade(c, .4, 60, 16); c.beginPath(); c.arc(cx, cy, r + 10, 0, 7); c.fillStyle = ST.endRing; c.fill(); c.restore();
    c.save(); c.beginPath(); c.arc(cx, cy, r, 0, 7); c.clip(); clip(c, 'face', o.faceT ?? 0, cx - r * 1.125, cy - r, r * 2.25, r * 2, { focus: BR.faceFocus }); c.restore();
    if (BR.ring) ringText(c, ' ' + BR.ring.replace(/\s*•?\s*$/, '') + ' •', cx, cy, r + 60, t * .8 - 1.5, font(600, 28, FJ), ST.endDim, P(t, .15, .4));
  }
  const lv = BR.live ? pop(t, .12) : 0;
  if (lv > 0) { c.save(); c.translate(cx, cy + r + 10); c.scale(lv, lv); rr(c, -92, -34, 184, 68, 34, ST.endFg); c.fillStyle = ST.red; c.beginPath(); c.arc(-50, 0, 11, 0, 7); c.fill(); mono(c, 'LIVE', 14, 2, 30, ST.endBg, { align: 'center', ls: 2 }); c.restore() }
  const s0 = o.start ?? (T - t), a1 = rise(T, s0 + .18), a2 = rise(T, s0 + .3);
  const cta = o.line1 || BR.cta || 'Follow for more';
  serif(c, cta, cx, 1105, Math.min(100, fit(c, cta, 600, SERIF, W - 140, 100)), { color: ST.endFg, halo: false, alpha: a1.a, dy: a1.dy });
  if (BR.handle) serif(c, BR.handle, cx, 1235, Math.min(92, fit(c, BR.handle, 600, ITAL, W - 140, 92)), { it: true, color: ST.endFg, halo: false, alpha: a2.a, dy: a2.dy });
  const tag = o.line3 ?? BR.tagline; if (tag) body(c, tag, cx, 1350, 34, ST.endDim, { align: 'center', alpha: P(t, .4, .6) });
  const [l1, l2] = o.logos || [];
  if (l1) { const p = rise(T, s0 + .35); logo(c, l1, 175, 395, 120, { s: p.a ? p.s : 0, rot: -.08 }) }
  if (l2) { const p = rise(T, s0 + .42); logo(c, l2, 905, 395, 100, { s: p.a ? p.s : 0, rot: .08 }) }
}
