import { atom, read, update } from 'claude-code'
import type { Register, SessionContextUsage, SessionCost, SessionRateLimit } from 'claude-code'

import type { Sample } from '../types'

const history = atom({ plugin: 'usage-graph', key: 'history' } as const, [])
const isHidden = atom({ plugin: 'usage-graph', key: 'isHidden' } as const, false)

const COMMAND = 'usage-graph'

const MAX_SAMPLES = 400
const LIMITS_KEY = 'limits'
const HOUR = 3_600_000
const KEEP_LIMITS_MS = 8 * 24 * HOUR

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

// Plan limits are the account's, not the session's: their readings are kept
// in $.store so a new session shows them before its first reply.
function limitPart(s: Sample): Sample | undefined {
  if (s.fiveHour === undefined && s.sevenDay === undefined) return undefined

  return {
    t: s.t,
    fiveHour: s.fiveHour,
    fiveHourResetsAt: s.fiveHourResetsAt,
    sevenDay: s.sevenDay,
    sevenDayResetsAt: s.sevenDayResetsAt,
  }
}

function storedLimits(value: unknown): Sample[] {
  return Array.isArray(value)
    ? value.filter((s): s is Sample => typeof s === 'object' && s !== null && typeof s.t === 'number')
    : []
}

function isLive(iso: string | undefined, now: number): boolean {
  return iso !== undefined && Date.parse(iso) > now
}

// The latest value of each figure, from the latest sample that has it; a
// limit whose window has already reset is dropped until a fresh reading.
function current(samples: Sample[], now: number): Sample {
  const out: Sample = { t: now }
  for (const s of samples) {
    if (s.fiveHour !== undefined) {
      out.fiveHour = s.fiveHour
      out.fiveHourResetsAt = s.fiveHourResetsAt
    }
    if (s.sevenDay !== undefined) {
      out.sevenDay = s.sevenDay
      out.sevenDayResetsAt = s.sevenDayResetsAt
    }
    if (s.context !== undefined) {
      out.context = s.context
      out.tokens = s.tokens
      out.window = s.window
    }
    if (s.usd !== undefined) out.usd = s.usd
  }
  if (out.fiveHourResetsAt !== undefined && !isLive(out.fiveHourResetsAt, now)) {
    out.fiveHour = undefined
    out.fiveHourResetsAt = undefined
  }
  if (out.sevenDayResetsAt !== undefined && !isLive(out.sevenDayResetsAt, now)) {
    out.sevenDay = undefined
    out.sevenDayResetsAt = undefined
  }

  return out
}

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

type Card = {
  title: string
  color: string
  value: number
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
  const barY = 58
  const barH = 8
  const value = Math.max(0, Math.min(100, card.value))
  const filled = value > 0 ? Math.max(barH, (inner * value) / 100) : 0

  return (
    `<text x="${left}" y="16" font-size="10.5" font-weight="600" letter-spacing="0.8" fill="#8b8b8b" ${font}>${esc(card.title)}</text>` +
    `<text x="${left}" y="47" font-size="26" font-weight="600" fill="${hot}" ${font}>${Math.round(card.value)}<tspan font-size="15" fill-opacity="0.75">%</tspan></text>` +
    `<rect x="${left}" y="${barY}" width="${inner}" height="${barH}" rx="${barH / 2}" fill="#8b8b8b" fill-opacity="0.22"/>` +
    (filled > 0 ? `<rect x="${left}" y="${barY}" width="${filled.toFixed(1)}" height="${barH}" rx="${barH / 2}" fill="${hot}"/>` : '') +
    `<text x="${left}" y="84" font-size="10.5" fill="#8b8b8b" ${font}>${esc(card.footer)}</text>`
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
  const last = current(samples, now)
  const cards: Card[] = []

  if (last.fiveHour !== undefined) {
    cards.push({ title: '5-HOUR LIMIT', color: '#d97757', value: last.fiveHour, footer: resetFooter(last.fiveHourResetsAt, now) })
  }
  if (last.sevenDay !== undefined) {
    cards.push({ title: 'WEEKLY LIMIT', color: '#6a9bcc', value: last.sevenDay, footer: resetFooter(last.sevenDayResetsAt, now) })
  }
  if (last.context !== undefined) {
    cards.push({ title: 'CONTEXT', color: '#8f9a6b', value: last.context, footer: contextNote(last) })
  }

  return cards
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const ran = await next(e)
    // A reload runs this again; the history in $.state survives it.
    if ((await read($, history)).length === 0) {
      const now = await $.clock.now()
      const usage = await $.session.usage()
      const sample = toSample(now, usage.context, usage.rateLimits, usage.cost)
      const kept = storedLimits(await $.store.get(LIMITS_KEY)).filter(s => s.t > now - KEEP_LIMITS_MS)
      await update($, history, () => [...kept, sample].slice(-MAX_SAMPLES))
    }
    await $.command.register({
      name: COMMAND,
      description: 'Show or hide the usage band above the prompt',
      argumentHint: '[show|hide]',
    })

    return ran
  })

  on('command.run', { command: COMMAND }, async ($, e) => {
    const arg = e.args.trim().toLowerCase()
    const hide = arg === 'hide' ? true : arg === 'show' ? false : !(await read($, isHidden))
    await update($, isHidden, () => hide)

    return { text: hide ? 'Usage band hidden. Run /usage-graph to show it again.' : 'Usage band shown.' }
  })

  on('session.measure', async ($, e, next) => {
    const sample = toSample(await $.clock.now(), e.context, e.rateLimits, e.cost)
    await update($, history, list => [...list, sample].slice(-MAX_SAMPLES))

    const limits = limitPart(sample)
    if (limits) {
      // Read again before writing: other sessions add to the same store.
      const kept = storedLimits(await $.store.get(LIMITS_KEY)).filter(s => s.t > sample.t - KEEP_LIMITS_MS)
      await $.store.set(LIMITS_KEY, [...kept, limits].slice(-MAX_SAMPLES))
    }

    return next(e)
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const samples = await read($, history)
    if (e.props.hasSurvey || samples.length === 0 || (await read($, isHidden))) return next(e)

    const hide = () => {
      void update($, isHidden, () => true)
      $.ui.toast('Usage band hidden. Run /usage-graph to show it again.')
    }

    const now = await $.clock.now()
    const last = current(samples, now)
    const shown = SERIES.filter(s => s.pick(last) !== undefined)
    const text = summary(last, now)

    if (e.surface === 'terminal') {
      const { Box, Button, Text } = $.ui.resolve(e)
      const width = Math.max(8, e.props.bodyColumns - 11)

      return (
        <Box flexDirection="column">
          <Box flexDirection="row" justifyContent="space-between">
            <Text dimColor>{text}</Text>
            <Button key="hide" role="dismiss" label="Hide" onPress={hide} />
          </Box>
          {shown.map(s => {
            const v = Math.max(0, Math.min(100, s.pick(last) ?? 0))
            const filled = Math.round((v / 100) * width)

            return (
              <Text>
                <Text dimColor>{s.label.padEnd(4)}</Text>
                <Text color={s.color}>{'█'.repeat(filled)}</Text>
                <Text dimColor>{'░'.repeat(width - filled)}</Text>
                <Text dimColor>{` ${Math.round(v)}%`}</Text>
              </Text>
            )
          })}
        </Box>
      )
    }

    const { Box, Button, Svg } = $.ui.resolve(e)
    const cards = toCards(samples, now)
    if (cards.length === 0) return next(e)

    return (
      <Box flexDirection="row" alignItems="flex-start">
        <Box flexGrow={1}>
          <Svg source={cardsSvg(cards)} alt={`Usage: ${text}`} />
        </Box>
        <Button key="hide" role="dismiss" label="Hide" onPress={hide} />
      </Box>
    )
  })
}
