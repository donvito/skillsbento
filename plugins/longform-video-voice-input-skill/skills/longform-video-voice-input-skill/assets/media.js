/* media helpers: photos, b-roll, captions, background hooks, big spoken openers (load after lib.js + parts.js) */
/* ---------- helpers ---------- */
/** full-bleed photo / clip with a slow push-in */
function photoFill(c, id, T, t0, o = {}) {
  const a = o.alpha ?? 1; if (a <= 0) return;
  const z = lerp(o.z0 ?? 1.12, o.z1 ?? 1.0, E.outCubic(P(T, t0, t0 + (o.dur || 7))));
  media(c, id, Math.max(0, T - t0), -2, -2, W + 4, H + 4, { zoom: z, focus: o.focus, alpha: a, speed: o.speed, loop: true });
  if (o.scrim) { c.save(); c.globalAlpha *= a; const g = c.createLinearGradient(0, 0, 0, H); g.addColorStop(0, `rgba(0,0,0,${o.scrim * .55})`); g.addColorStop(.55, `rgba(0,0,0,${o.scrim * .35})`); g.addColorStop(1, `rgba(0,0,0,${o.scrim})`); c.fillStyle = g; c.fillRect(0, 0, W, H); c.restore() }
}
/** rounded photo card with soft shadow and Ken Burns */
function photoCard(c, id, x, y, w, h, T, t0, o = {}) {
  const a = o.alpha ?? 1; if (a <= 0) return;
  c.save(); c.globalAlpha *= a;
  if (o.shadow !== false) { c.save(); c.shadowColor = 'rgba(0,0,0,.28)'; c.shadowBlur = 50 * U; c.shadowOffsetY = 20 * U; rr(c, x, y, w, h, o.r ?? 26 * U); c.fillStyle = '#ddd'; c.fill(); c.restore() }
  media(c, id, Math.max(0, T - t0), x, y, w, h, { radius: o.r ?? 26 * U, zoom: lerp(o.z0 ?? 1.12, 1, E.outCubic(P(T, t0, t0 + 6))), focus: o.focus, loop: true });
  c.restore();
}
/** circular photo avatar */
function photoCircle(c, id, x, y, r, T, o = {}) {
  const a = o.alpha ?? 1; if (a <= 0) return; c.save(); c.globalAlpha *= a; c.beginPath(); c.arc(x, y, r, 0, TAU); c.clip();
  media(c, id, 0, x - r, y - r, 2 * r, 2 * r, { focus: o.focus }); c.restore();
}
/** big white caption with shadow, for b-roll */
function brollText(c, runs, x, y, T, times, o = {}) {
  c.save(); c.shadowColor = 'rgba(0,0,0,.55)'; c.shadowBlur = 30 * U; c.shadowOffsetY = 4 * U;
  richLine(c, runs, x, y, T, { times, align: o.align }); c.restore();
}
/** background hook: lets a scene paint footage between its background fill and its content */
let BG_EXTRA = null;
{ const _l = bgLight, _d = bgDark;
  bgLight = function (c, T, o) { _l(c, T, o); if (BG_EXTRA) BG_EXTRA(c, T) };
  bgDark = function (c, T, o) { _d(c, T, o); if (BG_EXTRA) BG_EXTRA(c, T) }; }
const withBg = (base, fn) => (c, t, T) => { BG_EXTRA = fn; try { base(c, t, T) } finally { BG_EXTRA = null } };
const after = (base, fn) => (c, t, T) => { base(c, t, T); fn(c, t, T) };


/** big centered spoken line for scene openings, fades out at `until` (use: S.x = after(S.x, bigSay('In this video…', [t1,t2,t3], tEnd, dark))) */
const bigSay = (text, times, until, dark, o = {}) => (c, t, T) => {
  const a = 1 - E.ioCubic(P(T, until - .35, until)); if (a <= 0 || T < times[0] - .2) return;
  c.save(); c.globalAlpha *= a; c.translate(0, -30 * U * P(T, until - .35, until));
  richLine(c, [[text, SF(o.size || 120), dark ? C.cream : C.ink]], W / 2, H / 2 + 40 * U, T, { align: 'center', times }); c.restore() };
