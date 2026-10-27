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

test('the band graphs plan usage and context, on terminal and desktop', async ($, on) => {
  mock.clock(on)
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
  expect(await terminal.find({ type: 'Text', text: /[▁▂▃▄▅▆▇█]/ })).toBeTruthy()
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
