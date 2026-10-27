import { expect, mock, test } from 'claude-code/testing'

const BAND = {
  plugin: 'usage-graph',
  component: 'AbovePrompt',
  props: {
    hasSurvey: false,
    isWorking: false,
    maxRows: 10,
    bodyColumns: 60,
    scroll: { offset: 0, bodyRows: 9 },
    view: {},
  },
} as const

const RUN = {
  command: 'usage-graph',
  origin: { kind: 'composer' },
  presentation: { isFullscreen: false, columns: 80 },
} as const

test('the band graphs plan usage and context, on terminal and desktop', async ($, on) => {
  mock.clock(on)
  mock.store(on)
  on('session.measure', (_, e) => ({ changed: e.changed }))

  for (const [five, ctx] of [
    [10, 20],
    [25, 35],
    [42, 50],
  ] as const) {
    await $.session.measure({
      context: { window: 200000, tokens: ctx * 2000, percent: ctx },
      rateLimits: [
        { kind: 'five_hour', percentUsed: five, resetsAt: new Date(3 * 3_600_000).toISOString() },
        { kind: 'seven_day', percentUsed: 18 },
      ],
      cost: { usd: 1.5 },
      changed: ['context', 'rateLimits', 'cost'],
    })
  }

  const desktop = await $.ui.mount({ ...BAND, surface: 'desktop' })
  const svg = await desktop.find({ type: 'Svg' })
  expect(String(svg?.props.alt)).toMatch(/5h 42%.*7d 18%/)
  expect(String(svg?.props.source)).toMatch(/WEEKLY LIMIT/)
  expect(String(svg?.props.source)).toMatch(/100k \/ 200k tokens/)
  expect(String(svg?.props.source)).toMatch(/Resets \d{1,2}:\d{2}.* · in [23]h/)
  expect(String(svg?.props.source)).not.toMatch(/\$1\.50/)
  await desktop.unmount()

  const terminal = await $.ui.mount({ ...BAND, surface: 'terminal' })
  expect((await terminal.find({ type: 'Text', text: /context 50%/ }))?.text).not.toMatch(/\$/)
  expect(await terminal.find({ type: 'Text', text: /█/ })).toBeTruthy()
  await terminal.unmount()
})

test('the band stays empty before any reading', async ($, on) => {
  on('ui.render', ($, e) => {
    const { Text } = $.ui.resolve(e)

    return <Text>engine</Text>
  })

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  expect((await ui.find({ type: 'Text', text: /engine/ }))?.text).toBe('engine')
  await ui.unmount()
})

test('a new session shows the stored limits until its own reading', async ($, on) => {
  const HOUR = 3_600_000
  const at = (h: number) => new Date(h * HOUR).toISOString()
  mock.clock(on, { now: 10 * HOUR })
  mock.store(on, {
    limits: [
      { t: 1 * HOUR, fiveHour: 50, fiveHourResetsAt: at(3) },
      { t: 6 * HOUR, fiveHour: 5, fiveHourResetsAt: at(11) },
      { t: 8 * HOUR, fiveHour: 12, fiveHourResetsAt: at(11) },
      { t: 9 * HOUR, fiveHour: 20, fiveHourResetsAt: at(11), sevenDay: 30, sevenDayResetsAt: at(100) },
    ],
  })
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('command.register', () => ({ value: { command: 'usage-graph' } }))
  on('session.usage', () => ({ value: { startedAt: 10 * HOUR, context: { window: 200000 }, rateLimits: [] } }))
  on('session.measure', (_, e) => ({ changed: e.changed }))

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  const source = String((await ui.find({ type: 'Svg' }))?.props.source)
  // The latest stored reading in a live window, not the old 50% whose window reset.
  expect(source).toMatch(/>20<tspan/)
  expect(source).not.toMatch(/>50<tspan/)
  await ui.unmount()

  // A fresh reading in the session replaces the stored one.
  await $.session.measure({
    context: { window: 200000, tokens: 20000, percent: 10 },
    rateLimits: [
      { kind: 'five_hour', percentUsed: 26, resetsAt: at(11) },
      { kind: 'seven_day', percentUsed: 31, resetsAt: at(100) },
    ],
    changed: ['context', 'rateLimits'],
  })

  const terminal = await $.ui.mount({ ...BAND, surface: 'terminal' })
  expect((await terminal.find({ type: 'Text', text: /5h 26%/ }))?.text).toMatch(/7d 31%/)
  await terminal.unmount()
})

test('the band hides from its button and /usage-graph brings it back', async ($, on) => {
  mock.clock(on)
  mock.store(on)
  on('session.measure', (_, e) => ({ changed: e.changed }))
  on('ui.toast', () => ({ value: undefined }))
  on('ui.render', ($, e) => {
    const { Text } = $.ui.resolve(e)

    return <Text>engine</Text>
  })

  await $.session.measure({
    context: { window: 200000, tokens: 40000, percent: 20 },
    rateLimits: [{ kind: 'five_hour', percentUsed: 12 }],
    changed: ['context', 'rateLimits'],
  })

  for (const surface of ['terminal', 'desktop'] as const) {
    const ui = await $.ui.mount({ ...BAND, surface })
    await ui.press({ key: 'hide' })
    expect((await ui.find({ type: 'Text', text: /engine/ }))?.text).toBe('engine')
    await ui.unmount()

    const shown = await $.command.run({ ...RUN, args: '' })
    expect(shown.text).toBe('Usage band shown.')
    const again = await $.ui.mount({ ...BAND, surface })
    expect(await again.find({ type: 'Button' })).toBeTruthy()
    await again.unmount()
  }

  expect((await $.command.run({ ...RUN, args: 'hide' })).text).toMatch(/hidden/)
})
