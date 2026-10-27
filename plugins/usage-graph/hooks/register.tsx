import { atom, read, update } from 'claude-code'
import type { Register, SessionContextUsage, SessionCost, SessionRateLimit } from 'claude-code'

import type { Sample } from '../types'

const history = atom({ plugin: 'usage-graph', key: 'history' } as const, [])

const MAX_SAMPLES = 120
const BLOCKS = '▁▂▃▄▅▆▇█'

type Series = {
  label: string
  color: string
  pick: (s: Sample) => number | undefined
}

const SERIES: Series[] = [
  { label: '5h', color: '#d97757', pick: s => s.fiveHour },
  { label: '7d', color: '#6a9bcc', pick: s => s.sevenDay },
  { label: 'ctx', color: '#8f9a6b', pick: s => s.context },
]

function toSample(
  t: number,
  context: SessionContextUsage,
  rateLimits: SessionRateLimit[],
  cost: SessionCost | undefined,
): Sample {
  const five = rateLimits.find(r => r.kind === 'five_hour')
  const seven = rateLimits.find(r => r.kind === 'seven_day')

  return {
    t,
    fiveHour: five?.percentUsed,
    fiveHourResetsAt: five?.resetsAt,
    sevenDay: seven?.percentUsed,
    sevenDayResetsAt: seven?.resetsAt,
    context: context.percent,
    tokens: context.tokens,
    window: context.window,
    usd: cost?.usd,
  }
}

type Reset = { at: string; left: string }

// When a window resets, in local time: the clock alone today, the weekday
// within the week, the date beyond it; and how long until then.
function reset(iso: string | undefined, now: number): Reset | undefined {
  if (!iso) return undefined
  const when = Date.parse(iso)
  const ms = when - now
  if (!Number.isFinite(ms) || ms <= 0) return undefined

  const date = new Date(when)
  const time = date.toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' })
  const isToday = date.toDateString() === new Date(now).toDateString()
  const day = isToday
    ? ''
    : ms < 6 * 86_400_000
      ? `${date.toLocaleDateString(undefined, { weekday: 'short' })} `
      : `${date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}, `

  const mins = Math.round(ms / 60000)
  const hours = Math.floor(mins / 60)
  const left =
    mins < 60 ? `${mins}m` : hours < 24 ? `${hours}h ${mins % 60}m` : `${Math.floor(hours / 24)}d ${hours % 24}h`

  return { at: `${day}${time}`, left }
}

function resetSuffix(iso: string | undefined, now: number): string {
  const r = reset(iso, now)

  return r ? ` (resets ${r.at}, in ${r.left})` : ''
}

function resetFooter(iso: string | undefined, now: number): string {
  const r = reset(iso, now)

  return r ? `Resets ${r.at} · in ${r.left}` : ''
}

function hasLimits(s: Sample): boolean {
  return s.fiveHour !== undefined || s.sevenDay !== undefined
}

function compact(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1).replace(/\.0$/, '')}M`
  if (n >= 1000) return `${Math.round(n / 1000)}k`

  return String(n)
}

function contextNote(s: Sample): string {
  if (s.usd !== undefined && !hasLimits(s)) return `$${s.usd.toFixed(2)} this session`
  if (s.tokens === undefined || s.window === undefined) return ''

  return `${compact(s.tokens)} / ${compact(s.window)} tokens`
}

function summary(last: Sample, now: number): string {
  const parts: string[] = []
  if (last.fiveHour !== undefined) {
    parts.push(`5h ${last.fiveHour}%${resetSuffix(last.fiveHourResetsAt, now)}`)
  }
  if (last.sevenDay !== undefined) {
    parts.push(`7d ${last.sevenDay}%${resetSuffix(last.sevenDayResetsAt, now)}`)
  }
  if (last.context !== undefined) parts.push(`context ${last.context}%`)
  // On a plan the dollar figure is only an API-price estimate, so it shows
  // only where there are no plan limits (an API key, where it is real spend).
  if (last.usd !== undefined && !hasLimits(last)) parts.push(`$${last.usd.toFixed(2)}`)

  return parts.length ? parts.join(' · ') : 'Usage: waiting for the first reading'
}

function sparkline(values: (number | undefined)[], width: number): string {
  return values
    .slice(-width)
    .map(v => {
      if (v === undefined) return ' '
      const i = Math.round((Math.min(100, Math.max(0, v)) / 100) * (BLOCKS.length - 1))

      return BLOCKS[i] ?? ' '
    })
    .join('')
}

type Card = {
  title: string
  color: string
  value: number
  values: number[]
  footer: string
}

function esc(text: string): string {
  return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

function cardSvg(card: Card, x: number, w: number): string {
  const pad = 14
  const font = 'font-family="-apple-system,BlinkMacSystemFont,system-ui,sans-serif"'
  const hot = card.value >= 90 ? '#e5534b' : card.value >= 75 ? '#d4a72c' : card.color
  const left = x + pad
  const inner = w - pad * 2

  // The sparkline sits right of the big number, scaled to its own range so
  // small moves still read; a flat run is drawn mid-height.
  let spark = ''
  const vals = card.values.slice(-40)
  if (vals.length >= 2) {
    const sx = left + 78
    const sw = x + w - pad - sx
    const sy = 22
    const sh = 26
    let lo = Math.min(...vals)
    let hi = Math.max(...vals)
    if (hi - lo < 2) {
      const mid = (hi + lo) / 2
      lo = mid - 1
      hi = mid + 1
    }
    const pts = vals.map((v, i) => [
      sx + (i / (vals.length - 1)) * sw,
      sy + sh - ((v - lo) / (hi - lo)) * sh,
    ])
    const line = pts.map(([px, py]) => `${px!.toFixed(1)},${py!.toFixed(1)}`).join(' ')
    const area = `${sx},${sy + sh} ${line} ${sx + sw},${sy + sh}`
    const end = pts[pts.length - 1]!
    spark =
      `<polygon points="${area}" fill="${hot}" fill-opacity="0.12"/>` +
      `<polyline points="${line}" fill="none" stroke="${hot}" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"/>` +
      `<circle cx="${end[0]!.toFixed(1)}" cy="${end[1]!.toFixed(1)}" r="2.6" fill="${hot}"/>`
  }

  const fill = Math.max(0, Math.min(100, card.value)) / 100

  return (
    `<text x="${left}" y="16" font-size="10.5" font-weight="600" letter-spacing="0.8" fill="#8b8b8b" ${font}>${esc(card.title)}</text>` +
    `<text x="${left}" y="47" font-size="26" font-weight="600" fill="${hot}" ${font}>${Math.round(card.value)}<tspan font-size="15" fill-opacity="0.75">%</tspan></text>` +
    spark +
    `<rect x="${left}" y="58" width="${inner}" height="5" rx="2.5" fill="#8b8b8b" fill-opacity="0.22"/>` +
    (fill > 0
      ? `<rect x="${left}" y="58" width="${Math.max(5, inner * fill).toFixed(1)}" height="5" rx="2.5" fill="${hot}"/>`
      : '') +
    `<text x="${left}" y="80" font-size="10.5" fill="#8b8b8b" ${font}>${esc(card.footer)}</text>`
  )
}

function cardsSvg(cards: Card[]): string {
  const W = 760
  const H = 88
  const w = W / cards.length
  const dividers = cards
    .slice(1)
    .map((_, i) => `<line x1="${w * (i + 1)}" x2="${w * (i + 1)}" y1="6" y2="${H - 6}" stroke="#8b8b8b" stroke-opacity="0.2"/>`)
    .join('')

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}">${dividers}${cards.map((c, i) => cardSvg(c, i * w, w)).join('')}</svg>`
}

function toCards(samples: Sample[], now: number): Card[] {
  const last = samples[samples.length - 1]!
  const series = (pick: (s: Sample) => number | undefined) =>
    samples.map(pick).filter((v): v is number => v !== undefined)
  const cards: Card[] = []

  if (last.fiveHour !== undefined) {
    cards.push({ title: '5-HOUR LIMIT', color: '#d97757', value: last.fiveHour, values: series(s => s.fiveHour), footer: resetFooter(last.fiveHourResetsAt, now) })
  }
  if (last.sevenDay !== undefined) {
    cards.push({ title: 'WEEKLY LIMIT', color: '#6a9bcc', value: last.sevenDay, values: series(s => s.sevenDay), footer: resetFooter(last.sevenDayResetsAt, now) })
  }
  if (last.context !== undefined) {
    cards.push({ title: 'CONTEXT', color: '#8f9a6b', value: last.context, values: series(s => s.context), footer: contextNote(last) })
  }

  return cards
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const ran = await next(e)
    // A reload runs this again; the history in $.state survives it.
    if ((await read($, history)).length === 0) {
      const usage = await $.session.usage()
      const sample = toSample(await $.clock.now(), usage.context, usage.rateLimits, usage.cost)
      await update($, history, () => [sample])
    }

    return ran
  })

  on('session.measure', async ($, e, next) => {
    const sample = toSample(await $.clock.now(), e.context, e.rateLimits, e.cost)
    await update($, history, list => [...list, sample].slice(-MAX_SAMPLES))

    return next(e)
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const samples = await read($, history)
    if (e.props.hasSurvey || samples.length === 0) return next(e)

    const last = samples[samples.length - 1]!
    const shown = SERIES.filter(s => samples.some(sample => s.pick(sample) !== undefined))
    const text = summary(last, await $.clock.now())

    if (e.surface === 'terminal') {
      const { Box, Text } = $.ui.resolve(e)
      const width = Math.max(8, e.props.bodyColumns - 10)

      return (
        <Box flexDirection="column">
          <Text dimColor>{text}</Text>
          {shown.map(s => {
            const v = s.pick(last)

            return (
              <Text>
                <Text dimColor>{s.label.padEnd(4)}</Text>
                <Text color={s.color}>{sparkline(samples.map(s.pick), width)}</Text>
                <Text dimColor>{v === undefined ? '' : ` ${v}%`}</Text>
              </Text>
            )
          })}
        </Box>
      )
    }

    const { Svg } = $.ui.resolve(e)
    const cards = toCards(samples, await $.clock.now())
    if (cards.length === 0) return next(e)

    return <Svg source={cardsSvg(cards)} alt={`Usage: ${text}`} />
  })
}
