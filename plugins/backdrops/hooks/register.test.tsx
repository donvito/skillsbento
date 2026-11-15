import type { CommandRunInput, On, ThemeSetArgs } from 'claude-code'
import { expect, test } from 'claude-code/testing'

// The test's hooks stand for the engine: they record each theme call.
function engine(on: On, entries?: Record<string, unknown>) {
  const calls: { set: ThemeSetArgs[]; clears: number; store: Record<string, unknown> } = {
    set: [],
    clears: 0,
    store: { ...entries },
  }

  // $.store, in memory, readable by the test.
  on('store.get', (_, e) => ({ value: calls.store[e.key] }))
  on('store.set', (_, e) => {
    calls.store[e.key] = e.value

    return { value: undefined }
  })
  on('command.register', (_, e) => ({ value: { command: e.name } }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('theme.set', (_, e) => {
    calls.set.push(e)

    return { value: { isDrawn: true, requestId: 'backdrop-1' } }
  })
  on('theme.clear', () => {
    calls.clears += 1

    return { value: { isDrawn: false, reason: 'cleared' } }
  })

  return calls
}

// The kit stamps `origin` and `presentation` as the engine would.
const typed = (command: string) => ({ command, args: '' }) as CommandRunInput

const sceneOf = (args: ThemeSetArgs | undefined) =>
  args?.backdrop !== undefined && 'scene' in args.backdrop ? args.backdrop.scene : undefined

test('each command switches the backdrop without a restart', async ($, on) => {
  const calls = engine(on)

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  expect(calls.set.length).toBe(0)

  const ferrari = await $.command.run(typed('backdrop-ferrari-hamilton'))
  expect(sceneOf(calls.set.at(-1))).toBe('f1-ferrari-hamilton')
  expect(ferrari.text).toMatch(/Ferrari #44/)
  expect(calls.store.theme).toBe('ferrari')

  await $.command.run(typed('backdrop-mercedes-kimi'))
  expect(sceneOf(calls.set.at(-1))).toBe('f1-mercedes-kimi')
  expect(calls.set.at(-1)?.colors?.label).toBe('Mercedes #12')
  expect(calls.store.theme).toBe('mercedes')

  await $.command.run(typed('backdrop-off'))
  expect(calls.clears).toBe(1)
  expect(calls.store.theme).toBe('plain')
})

test('the last pick comes back in a new session', async ($, on) => {
  const calls = engine(on, { theme: 'mercedes' })

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  expect(sceneOf(calls.set[0])).toBe('f1-mercedes-kimi')
})

test('plain at start leaves the look alone', async ($, on) => {
  const calls = engine(on, { theme: 'plain' })

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  expect(calls.set.length).toBe(0)
  expect(calls.clears).toBe(0)
})

const SCENES = [
  'f1-mercedes-kimi',
  'f1-ferrari-hamilton',
  'space-shuttle',
  'mt-fuji',
  'paris',
  'rome',
  'swiss-alps',
  'tokyo-shibuya',
  'matrix',
  'retro-80s',
  'windows-xp',
  'windows-98',
  'macintosh-retro',
  'linux',
  'christmas-fireplace',
  'christmas-village',
  'christmas-snowglobe',
  'new-york',
  'london',
  'santorini',
  'northern-lights',
  'new-year',
  'rainy-cafe',
  'cabin-library',
  'underwater-reef',
  'deep-space',
  'pixel-arcade',
  'vaporwave',
  'blueprint',
  'dos-prompt',
  'netherlands',
] as const

for (const scene of SCENES) {
  test(`the ${scene} backdrop draws as vector shapes, with no raster image`, async $ => {
    for (const surface of ['desktop', 'mobile'] as const) {
      const ui = await $.ui.mount({
        plugin: 'backdrops',
        component: 'Backdrop',
        requestId: 'backdrop-1',
        surface,
        props: { scene, plugin: 'backdrops', glass: { blur: 6, opacity: 0.5 } },
      })
      const svg = await ui.find({ type: 'Svg' })
      const source = String(svg?.props.source ?? '')

      expect(source.startsWith('<svg')).toBe(true)
      expect(source.includes('<image')).toBe(false)
      expect(/<(path|text|rect|circle)\b/.test(source)).toBe(true)
      expect(source.length < 131072).toBe(true)
      expect(svg?.props.isInteractive).toBe(undefined)
      await ui.unmount()
    }
  })
}

test('the menu entries from commands/ files switch the backdrop too', async ($, on) => {
  const calls = engine(on)

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  await $.command.run(typed('backdrops:ferrari-hamilton'))
  expect(sceneOf(calls.set.at(-1))).toBe('f1-ferrari-hamilton')
  await $.command.run(typed('backdrops:off'))
  expect(calls.clears).toBe(1)
  expect(calls.store.theme).toBe('plain')
})

const TRAVEL = [
  ['space-shuttle', 'space-shuttle', 'space'],
  ['mt-fuji', 'mt-fuji', 'fuji'],
  ['paris', 'paris', 'paris'],
  ['rome', 'rome', 'rome'],
  ['swiss-alps', 'swiss-alps', 'alps'],
  ['tokyo-shibuya', 'tokyo-shibuya', 'tokyo'],
  ['matrix', 'matrix', 'matrix'],
  ['retro-80s', 'retro-80s', 'retro80s'],
  ['windows-xp', 'windows-xp', 'winxp'],
  ['windows-98', 'windows-98', 'win98'],
  ['macintosh-retro', 'macintosh-retro', 'mac'],
  ['linux', 'linux', 'linux'],
  ['christmas-fireplace', 'christmas-fireplace', 'xmasFire'],
  ['christmas-village', 'christmas-village', 'xmasVillage'],
  ['christmas-snowglobe', 'christmas-snowglobe', 'xmasGlobe'],
  ['new-york', 'new-york', 'nyc'],
  ['london', 'london', 'london'],
  ['santorini', 'santorini', 'santorini'],
  ['northern-lights', 'northern-lights', 'aurora'],
  ['new-year', 'new-year', 'newyear'],
  ['rainy-cafe', 'rainy-cafe', 'cafe'],
  ['cabin-library', 'cabin-library', 'library'],
  ['underwater-reef', 'underwater-reef', 'reef'],
  ['deep-space', 'deep-space', 'deepspace'],
  ['pixel-arcade', 'pixel-arcade', 'arcade'],
  ['vaporwave', 'vaporwave', 'vapor'],
  ['blueprint', 'blueprint', 'blueprint'],
  ['dos-prompt', 'dos-prompt', 'dos'],
  ['netherlands', 'netherlands', 'holland'],
] as const

test('each travel theme switches from its command and its menu entry', async ($, on) => {
  const calls = engine(on)

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  for (const [command, scene, stored] of TRAVEL) {
    await $.command.run(typed(`backdrop-${command}`))
    expect(sceneOf(calls.set.at(-1))).toBe(scene)
    expect(calls.store.theme).toBe(stored)
    await $.command.run(typed('backdrop-off'))
    await $.command.run(typed(`backdrops:${command}`))
    expect(sceneOf(calls.set.at(-1))).toBe(scene)
  }
})

test('a travel pick comes back in a new session', async ($, on) => {
  const calls = engine(on, { theme: 'tokyo' })

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  expect(sceneOf(calls.set[0])).toBe('tokyo-shibuya')
})

const BAND = {
  plugin: 'backdrops',
  component: 'AbovePrompt',
  requestId: 'band-1',
  props: {
    hasSurvey: false,
    isCollapsed: false,
    isWorking: false,
    maxRows: 10,
    bodyColumns: 80,
    scroll: { offset: 0, bodyRows: 10 },
    view: {},
  },
} as const

test('the picker above the prompt switches the backdrop on desktop', async ($, on) => {
  const calls = engine(on, { theme: 'mercedes' })

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  const picker = await ui.find({ key: 'backdrop' })

  expect(picker?.type).toBe('Select')
  expect(picker?.props.value).toBe('mercedes')
  await ui.select({ key: 'backdrop', value: 'paris' })
  expect(sceneOf(calls.set.at(-1))).toBe('paris')
  expect(calls.store.theme).toBe('paris')
  expect((await ui.find({ key: 'backdrop' }))?.props.value).toBe('paris')
  await ui.select({ key: 'backdrop', value: 'plain' })
  expect(calls.clears).toBe(1)
  await ui.unmount()
})

test('the picker stays out of surfaces that draw no backdrop', async ($, on) => {
  engine(on)
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  const ui = await $.ui.mount({ ...BAND, surface: 'terminal' })

  expect(await ui.find({ key: 'backdrop' })).toBe(undefined)
  await ui.unmount()
})

test('each scene is drawn once, at a fixed moment, as a plain image', async ($, on) => {
  engine(on)
  const ui = await $.ui.mount({
    plugin: 'backdrops',
    component: 'Backdrop',
    requestId: 'backdrop-1',
    surface: 'desktop',
    props: { scene: 'paris', plugin: 'backdrops', glass: { blur: 6, opacity: 0.5 } },
  })
  const svg = await ui.find({ type: 'Svg' })

  expect(String(svg?.props.source ?? '').includes(':root{--t:7s}')).toBe(true)
  expect(svg?.props.isInteractive).toBe(undefined)
  await ui.unmount()
})
