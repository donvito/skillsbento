/* reusable composed parts */

/** agent composer card with synced typed prompt. returns card height */
function composer(c, x, y, w, text, T, tFrom, o = {}) {
  const f = o.font || fN(40 * U, 450), lh = parseFloat(f.match(/(\d+(\.\d+)?)px/)[1]) * 1.38, pad = 40 * U;
  const lines = wrap(c, text, f, w - pad * 2 - 70 * U), h = o.h || (lines.length * lh + pad * 2 + 70 * U);
  const p = E.outExpo(P(T, o.t0 ?? tFrom - .8, (o.t0 ?? tFrom - .8) + .7)); if (p <= 0) return h;
  c.save(); c.globalAlpha *= p; c.translate(0, (1 - p) * 40 * U);
  card(c, x, y, w, h, { fill: o.fill || C.paper, r: 30 * U, stroke: o.stroke });
  // header
  spark(c, x + pad + 16 * U, y + pad + 14 * U, 17 * U, T, { col: C.clay, busy: o.busy || 0 });
  const times = phraseTimes(text, tFrom); let k = 0;
  lines.forEach((ln, i) => { const n = ln.split(' ').length; richLine(c, [[ln, f, o.fg || C.ink]], x + pad, y + pad + 70 * U + lh * (i + .75), T, { times: times.slice(k, k + n), dur: .35 }); k += n });
  // send button
  const sp = E.outBack(P(T, o.sendAt ?? 1e9, (o.sendAt ?? 1e9) + .4));
  c.save(); const bx = x + w - pad - 28 * U, by = y + h - pad - 8 * U; c.beginPath(); c.arc(bx, by, 28 * U, 0, TAU); c.fillStyle = T > (o.sendAt ?? 1e9) ? C.clay : (o.dark ? C.slate4 : C.oat); c.fill();
  ico(c, 'send', bx + 2 * U, by, 26 * U, T > (o.sendAt ?? 1e9) ? '#fff' : (o.dark ? C.creamDim : C.ink3)); c.restore();
  if (sp > 0 && sp < 1) { c.save(); c.strokeStyle = C.clay; c.globalAlpha = 1 - sp; c.lineWidth = 3 * U; c.beginPath(); c.arc(bx, by, 28 * U + 30 * U * sp, 0, TAU); c.stroke(); c.restore() }
  c.restore(); return h;
}

/** step row: icon tile + text + status (spinner -> check) */
function stepRow(c, x, y, w, icon, title, T, t0, tDone, o = {}) {
  const p = E.outExpo(P(T, t0, t0 + .55)); if (p <= 0) return;
  const h = o.h || 86 * U, dark = o.dark;
  c.save(); c.globalAlpha *= p; c.translate((1 - p) * -40 * U, 0);
  card(c, x, y, w, h, { fill: dark ? C.slate2 : C.paper, r: 20 * U, shadow: dark ? 0 : .6, stroke: dark ? C.creamFaint : null });
  icoTile(c, icon, x + 26 * U + 26 * U, y + h / 2, 52 * U, { bg: dark ? 'rgba(140,140,140,.16)' : C.clayXL, col: C.clay });
  txt(c, title, x + 104 * U, y + h / 2 + 2 * U, { font: o.font || fN(30 * U, 500), color: dark ? C.cream : C.ink, base: 'middle' });
  const done = P(T, tDone, tDone + .6);
  if (T < tDone) workingRing(c, x + w - 44 * U, y + h / 2, 16 * U, T, P(T, t0 + .3, t0 + .6), C.clay);
  checkMark(c, x + w - 44 * U, y + h / 2, 20 * U, done, C.olive);
  c.restore();
}

/** phone with a name pill under it */
function appPhone(c, id, cx, cy, h, T, t0, name, o = {}) {
  const p = (o.ease || E.outExpo)(P(T, t0, t0 + .8)); if (p <= 0) return;
  c.save(); c.globalAlpha *= clamp(p * 1.4);
  const yy = cy + (1 - p) * 220 * U;
  phone(c, id, cx, yy, h, T, { rot: (o.rot || 0) * p + (1 - p) * (o.rot0 || 0), lt: o.lt ?? Math.max(0, T - t0), zoom: o.zoom, focus: o.focus, loop: o.loop, speed: o.speed, in: o.in });
  if (name) { const np = E.outBack(P(T, t0 + .25, t0 + .7)); chip(c, cx, yy + h / 2 + 62 * U, name, { align: 'center', font: fN(28 * U, 600), bg: o.dark === false ? C.ink : C.cream, fg: o.dark === false ? C.cream : C.ink, h: 56 * U, p: np }) }
  c.restore();
}

/** big chapter card */
function chapterCard(c, T, t0, num, title1, title2, tWords, o = {}) {
  bgDark(c, T, { glow: .2 });
  const cx = M, top = H * .38;
  const lp = E.outExpo(P(T, t0, t0 + .8));
  const f = fS(118 * U, 450), fi = fS(118 * U, 400, true);
  richLine(c, title1, cx, top + 70 * U, T, { times: tWords[0] });
  if (title2) richLine(c, title2, cx, top + 70 * U + 128 * U, T, { times: tWords[1] });
  // big outline numeral
  const np = E.outExpo(P(T, t0, t0 + 1.2));
  c.save(); c.globalAlpha = .07 * np; c.font = fS(620 * U, 500); c.textAlign = 'right'; c.fillStyle = C.cream; c.fillText(num, W - M + (1 - np) * 80 * U, H * .86); c.restore();
}
const SF = (px, it = false, w) => it ? fS(px * U, w || 400, true) : fS(px * U, w || 450);

/** simple Mt Fuji illustration */
function fuji(c, x, y, w, T, p = 1) {
  if (p <= 0) return; const h = w * .5; c.save(); c.globalAlpha *= p;
  c.beginPath(); c.arc(x + w * .72, y + h * .25, w * .11 * E.outBack(P(p, .2, 1)), 0, TAU); c.fillStyle = C.clay; c.fill();
  c.beginPath(); c.moveTo(x, y + h); c.lineTo(x + w * .38, y + h * .28); c.quadraticCurveTo(x + w * .5, y + h * .2, x + w * .62, y + h * .28); c.lineTo(x + w, y + h); c.closePath(); c.fillStyle = '#BDBDBD'; c.fill();
  c.beginPath(); c.moveTo(x + w * .38, y + h * .28); c.quadraticCurveTo(x + w * .5, y + h * .2, x + w * .62, y + h * .28); c.lineTo(x + w * .69, y + h * .42); c.lineTo(x + w * .6, y + h * .38); c.lineTo(x + w * .53, y + h * .45); c.lineTo(x + w * .46, y + h * .38); c.lineTo(x + w * .38, y + h * .44); c.lineTo(x + w * .31, y + h * .41); c.closePath(); c.fillStyle = '#fff'; c.fill();
  c.restore();
}
/** generic browser window */
function browserWin(c, x, y, w, h, title, T, o = {}) {
  card(c, x, y, w, h, { fill: o.fill || '#fff', r: 14 * U, shadow: o.shadow ?? .8 });
  c.save(); rr(c, x, y, w, 40 * U, [14 * U, 14 * U, 0, 0]); c.fillStyle = o.bar || C.oat; c.fill();
  [0, 1, 2].forEach(i => { c.beginPath(); c.arc(x + 22 * U + i * 18 * U, y + 20 * U, 5.5 * U, 0, TAU); c.fillStyle = ['#C4C4C4', '#C4C4C4', '#C4C4C4'][i]; c.fill() });
  rr(c, x + 90 * U, y + 9 * U, w - 120 * U, 22 * U, 11 * U); c.fillStyle = 'rgba(255,255,255,.75)'; c.fill();
  txt(c, title, x + 104 * U, y + 21 * U, { font: fM(13 * U), color: C.ink2, base: 'middle' });
  // placeholder content lines
  const r = rng(o.seed || 1);
  if (o.content !== false) { rr(c, x + 22 * U, y + 58 * U, w * .38, h - 80 * U, 8 * U); c.fillStyle = o.img || C.oat2; c.fill();
    for (let i = 0; i < 6; i++) { const ly = y + 66 * U + i * 26 * U; if (ly > y + h - 24 * U) break; rr(c, x + w * .38 + 40 * U, ly, (w * .5 - 40 * U) * (.5 + .5 * r()), 10 * U, 5 * U); c.fillStyle = i ? C.oat : C.oat2; c.fill() } }
  c.restore();
}
/** rounded toggle */
function toggle(c, x, y, on, p = 1) {
  const w = 64 * U, h = 36 * U; rr(c, x, y - h / 2, w, h, h / 2); c.fillStyle = on ? lerp(0, 1, p) > .5 ? C.olive : C.slate4 : C.slate4; c.fill();
  const k = on ? E.outBack(p) : 0; c.beginPath(); c.arc(x + h / 2 + (w - h) * k, y, h / 2 - 4 * U, 0, TAU); c.fillStyle = '#fff'; c.fill();
}
