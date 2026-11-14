import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register, ThemeSetArgs } from 'claude-code'

import { FERRARI_LOOK, MERCEDES_LOOK, SCENE, UNPAINTED } from './looks'
import { FERRARI_HAMILTON } from './scenes/f1-ferrari-hamilton'
import { MERCEDES_KIMI } from './scenes/f1-mercedes-kimi'
import { MATRIX } from './scenes/matrix'
import { RETRO_80S } from './scenes/retro-80s'
import { WINDOWS_XP } from './scenes/windows-xp'
import { WINDOWS_98 } from './scenes/windows-98'
import { MACINTOSH_RETRO } from './scenes/macintosh-retro'
import { LINUX } from './scenes/linux'
import { CHRISTMAS_FIREPLACE } from './scenes/christmas-fireplace'
import { CHRISTMAS_VILLAGE } from './scenes/christmas-village'
import { CHRISTMAS_SNOWGLOBE } from './scenes/christmas-snowglobe'
import { MT_FUJI } from './scenes/mt-fuji'
import { PARIS } from './scenes/paris'
import { ROME } from './scenes/rome'
import { SPACE_SHUTTLE } from './scenes/space-shuttle'
import { SWISS_ALPS } from './scenes/swiss-alps'
import { TOKYO_SHIBUYA } from './scenes/tokyo-shibuya'
import { TRAVEL_LOOKS, TRAVEL_SCENES } from './travel-looks'
import type { TravelTheme } from './travel-looks'

type Theme = 'mercedes' | 'ferrari' | TravelTheme
type Choice = Theme | 'plain'

// $.store outlives the session, so the last pick comes back next time.
const STORE_KEY = 'theme'

// What the picker above the prompt shows as selected; set at start and on each pick.
const current = atom({ plugin: 'backdrops', key: 'current' } as const, 'plain')

// The desktop app paints a backdrop as a still frame, and redrawing it on a
// timer flickers, so each scene is drawn once, at a moment where its moving
// parts (snow, petals, walkers, clouds) are spread across it. The scenes'
// CSS animation delays are offset by var(--t) (tools/smil.py).
const STILL_AT = ':root{--t:7s}'

// The picker's entries, in menu order.
const PICKER: { value: Choice; label: string }[] = [
  { value: 'plain', label: 'None' },
  { value: 'mercedes', label: 'Mercedes #12' },
  { value: 'ferrari', label: 'Ferrari #44' },
  { value: 'space', label: 'Space shuttle' },
  { value: 'fuji', label: 'Mt Fuji' },
  { value: 'paris', label: 'Paris' },
  { value: 'rome', label: 'Rome' },
  { value: 'alps', label: 'Swiss Alps' },
  { value: 'tokyo', label: 'Tokyo Shibuya' },
  { value: 'matrix', label: 'Matrix' },
  { value: 'retro80s', label: 'Retro 80s' },
  { value: 'winxp', label: 'Windows XP' },
  { value: 'win98', label: 'Windows 98' },
  { value: 'mac', label: 'Macintosh retro' },
  { value: 'linux', label: 'Linux' },
  { value: 'xmasFire', label: 'Christmas fireplace' },
  { value: 'xmasVillage', label: 'Christmas village' },
  { value: 'xmasGlobe', label: 'Christmas snow globe' },
]

const THEMES: Record<Theme, { look: ThemeSetArgs; title: string }> = {
  mercedes: { look: MERCEDES_LOOK, title: 'Mercedes #12 (Kimi Antonelli)' },
  ferrari: { look: FERRARI_LOOK, title: 'Ferrari #44 (Lewis Hamilton)' },
  space: { look: TRAVEL_LOOKS.space, title: 'Space shuttle' },
  fuji: { look: TRAVEL_LOOKS.fuji, title: 'Mt Fuji' },
  paris: { look: TRAVEL_LOOKS.paris, title: 'Paris' },
  rome: { look: TRAVEL_LOOKS.rome, title: 'Rome' },
  alps: { look: TRAVEL_LOOKS.alps, title: 'Swiss Alps' },
  tokyo: { look: TRAVEL_LOOKS.tokyo, title: 'Tokyo Shibuya' },
  matrix: { look: TRAVEL_LOOKS.matrix, title: 'Matrix' },
  retro80s: { look: TRAVEL_LOOKS.retro80s, title: 'Retro 80s' },
  winxp: { look: TRAVEL_LOOKS.winxp, title: 'Windows XP' },
  win98: { look: TRAVEL_LOOKS.win98, title: 'Windows 98' },
  mac: { look: TRAVEL_LOOKS.mac, title: 'Macintosh retro' },
  linux: { look: TRAVEL_LOOKS.linux, title: 'Linux' },
  xmasFire: { look: TRAVEL_LOOKS.xmasFire, title: 'Christmas fireplace' },
  xmasVillage: { look: TRAVEL_LOOKS.xmasVillage, title: 'Christmas village' },
  xmasGlobe: { look: TRAVEL_LOOKS.xmasGlobe, title: 'Christmas snow globe' },
}

// Every scene is vector only; isInteractive lets its CSS animation run.
const DRAWINGS: Record<string, { source: string; alt: string }> = {
  [SCENE.mercedes]: {
    source: MERCEDES_KIMI,
    alt: 'A portrait of Kimi Antonelli, number 12, and a top-down view of his black and turquoise Mercedes',
  },
  [SCENE.ferrari]: {
    source: FERRARI_HAMILTON,
    alt: 'A portrait of Lewis Hamilton, number 44, and a top-down view of his red and white Ferrari',
  },
  [TRAVEL_SCENES.space]: { source: SPACE_SHUTTLE, alt: 'Earth below the windows of a space shuttle flight deck' },
  [TRAVEL_SCENES.fuji]: { source: MT_FUJI, alt: 'Mount Fuji at dusk over a lake, with a pagoda and falling cherry petals' },
  [TRAVEL_SCENES.paris]: { source: PARIS, alt: 'The Eiffel Tower sparkling at night over Paris rooftops' },
  [TRAVEL_SCENES.rome]: { source: ROME, alt: 'The Colosseum at golden hour with stone pines and swifts' },
  [TRAVEL_SCENES.alps]: { source: SWISS_ALPS, alt: 'A moonlit Matterhorn above a snowy chalet with falling snow' },
  [TRAVEL_SCENES.tokyo]: { source: TOKYO_SHIBUYA, alt: 'Shibuya crossing in Tokyo at night in the rain, with neon signs' },
  [TRAVEL_SCENES.matrix]: { source: MATRIX, alt: 'Green code raining down a black screen' },
  [TRAVEL_SCENES.retro80s]: { source: RETRO_80S, alt: 'A synthwave sunset over a neon grid with palm trees' },
  [TRAVEL_SCENES.winxp]: { source: WINDOWS_XP, alt: 'Rolling green hills under a blue sky with desktop icons and a blue taskbar' },
  [TRAVEL_SCENES.win98]: { source: WINDOWS_98, alt: 'A teal desktop with icons, a classic grey window and taskbar' },
  [TRAVEL_SCENES.mac]: { source: MACINTOSH_RETRO, alt: 'A dithered grey desktop with a menu bar, a pinstriped window and disk icons' },
  [TRAVEL_SCENES.linux]: { source: LINUX, alt: 'A cartoon penguin on an ice floe under an aurora, beside a terminal window' },
  [TRAVEL_SCENES.xmasFire]: { source: CHRISTMAS_FIREPLACE, alt: 'A cosy room with a crackling fire, stockings, a decorated Christmas tree and presents' },
  [TRAVEL_SCENES.xmasVillage]: { source: CHRISTMAS_VILLAGE, alt: 'A snowy village at night with string lights and a sleigh crossing the moon' },
  [TRAVEL_SCENES.xmasGlobe]: { source: CHRISTMAS_SNOWGLOBE, alt: 'A snow globe with a little house and tree, soft festive lights and hanging ornaments' },
}

const isChoice = (value: unknown): value is Choice =>
  value === 'plain' || (typeof value === 'string' && value in THEMES)

/** Applies a pick, remembers it across sessions and says what happened. */
async function apply($: EngineInterface, choice: Choice): Promise<{ text: string }> {
  await $.store.set(STORE_KEY, choice)
  await update($, current, () => choice)

  if (choice === 'plain') {
    await $.theme.clear()

    return { text: 'Backdrop off: back to the default Claude Code look.' }
  }
  const { look, title } = THEMES[choice]
  const set = await $.theme.set(look)

  if (!set.isDrawn) {
    return {
      text: `${title} saved. It draws in the Claude desktop and mobile apps; here: ${set.reason}`,
    }
  }

  return { text: `${title} backdrop on. It stays on in new sessions until you pick None or run /backdrops:off.` }
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'backdrop-mercedes-kimi',
      description: "Backdrop: Kimi Antonelli's Mercedes #12 in black, silver and turquoise",
    })
    await $.command.register({
      name: 'backdrop-ferrari-hamilton',
      description: "Backdrop: Lewis Hamilton's Ferrari #44 in red, white and black",
    })
    await $.command.register({
      name: 'backdrop-space-shuttle',
      description: 'Backdrop: Earth from a space shuttle flight deck, with blinking panels',
    })
    await $.command.register({
      name: 'backdrop-mt-fuji',
      description: 'Backdrop: Mt Fuji at dusk, a pagoda and falling cherry petals',
    })
    await $.command.register({
      name: 'backdrop-paris',
      description: 'Backdrop: the Eiffel Tower sparkling at night',
    })
    await $.command.register({
      name: 'backdrop-rome',
      description: 'Backdrop: the Colosseum at golden hour, with swifts in flight',
    })
    await $.command.register({
      name: 'backdrop-swiss-alps',
      description: 'Backdrop: a moonlit Matterhorn and a chalet in falling snow',
    })
    await $.command.register({
      name: 'backdrop-tokyo-shibuya',
      description: 'Backdrop: Shibuya crossing at night in the rain, with neon',
    })
    await $.command.register({
      name: 'backdrop-matrix',
      description: 'Backdrop: green code raining down a black screen',
    })
    await $.command.register({
      name: 'backdrop-retro-80s',
      description: 'Backdrop: a synthwave sunset over a neon grid, with palms',
    })
    await $.command.register({
      name: 'backdrop-windows-xp',
      description: 'Backdrop: rolling green hills, blue sky, desktop icons and a blue taskbar',
    })
    await $.command.register({
      name: 'backdrop-windows-98',
      description: 'Backdrop: a teal desktop with a classic grey window and taskbar',
    })
    await $.command.register({
      name: 'backdrop-macintosh-retro',
      description: 'Backdrop: a classic dithered desktop, menu bar and pinstriped window',
    })
    await $.command.register({
      name: 'backdrop-linux',
      description: 'Backdrop: a penguin on an ice floe under an aurora, beside a terminal',
    })
    await $.command.register({
      name: 'backdrop-christmas-fireplace',
      description: 'Backdrop: a cosy fire with stockings, a decorated tree and presents',
    })
    await $.command.register({
      name: 'backdrop-christmas-village',
      description: 'Backdrop: a snowy village at night with a sleigh crossing the moon',
    })
    await $.command.register({
      name: 'backdrop-christmas-snowglobe',
      description: 'Backdrop: a snow globe with a little house and tree, and festive lights',
    })
    await $.command.register({
      name: 'backdrop-off',
      description: 'Remove the backdrop and go back to the default Claude Code look',
    })
    const unpainted = UNPAINTED[0]

    if (unpainted !== undefined) {
      $.ui.toast(unpainted)
    }
    // Bring back the last pick. 'plain' or nothing stored: leave the look alone,
    // so another mod's theme is never wiped at start.
    const stored = await $.store.get(STORE_KEY)

    if (isChoice(stored) && stored !== 'plain') {
      await $.theme.set(THEMES[stored].look)
      await update($, current, () => stored)
    }

    return next(e)
  })

  // Typed in full: /backdrop-<name>.
  on('command.run', { command: 'backdrop-mercedes-kimi' }, $ => apply($, 'mercedes'))
  on('command.run', { command: 'backdrop-ferrari-hamilton' }, $ => apply($, 'ferrari'))
  on('command.run', { command: 'backdrop-space-shuttle' }, $ => apply($, 'space'))
  on('command.run', { command: 'backdrop-mt-fuji' }, $ => apply($, 'fuji'))
  on('command.run', { command: 'backdrop-paris' }, $ => apply($, 'paris'))
  on('command.run', { command: 'backdrop-rome' }, $ => apply($, 'rome'))
  on('command.run', { command: 'backdrop-swiss-alps' }, $ => apply($, 'alps'))
  on('command.run', { command: 'backdrop-tokyo-shibuya' }, $ => apply($, 'tokyo'))
  on('command.run', { command: 'backdrop-matrix' }, $ => apply($, 'matrix'))
  on('command.run', { command: 'backdrop-retro-80s' }, $ => apply($, 'retro80s'))
  on('command.run', { command: 'backdrop-windows-xp' }, $ => apply($, 'winxp'))
  on('command.run', { command: 'backdrop-windows-98' }, $ => apply($, 'win98'))
  on('command.run', { command: 'backdrop-macintosh-retro' }, $ => apply($, 'mac'))
  on('command.run', { command: 'backdrop-linux' }, $ => apply($, 'linux'))
  on('command.run', { command: 'backdrop-christmas-fireplace' }, $ => apply($, 'xmasFire'))
  on('command.run', { command: 'backdrop-christmas-village' }, $ => apply($, 'xmasVillage'))
  on('command.run', { command: 'backdrop-christmas-snowglobe' }, $ => apply($, 'xmasGlobe'))
  on('command.run', { command: 'backdrop-off' }, $ => apply($, 'plain'))
  // The same commands from the plugin's commands/ files, which the desktop
  // app's slash menu lists as /backdrops:<name>; answered here, never by
  // the model.
  on('command.run', { command: 'backdrops:mercedes-kimi' }, $ => apply($, 'mercedes'))
  on('command.run', { command: 'backdrops:ferrari-hamilton' }, $ => apply($, 'ferrari'))
  on('command.run', { command: 'backdrops:space-shuttle' }, $ => apply($, 'space'))
  on('command.run', { command: 'backdrops:mt-fuji' }, $ => apply($, 'fuji'))
  on('command.run', { command: 'backdrops:paris' }, $ => apply($, 'paris'))
  on('command.run', { command: 'backdrops:rome' }, $ => apply($, 'rome'))
  on('command.run', { command: 'backdrops:swiss-alps' }, $ => apply($, 'alps'))
  on('command.run', { command: 'backdrops:tokyo-shibuya' }, $ => apply($, 'tokyo'))
  on('command.run', { command: 'backdrops:matrix' }, $ => apply($, 'matrix'))
  on('command.run', { command: 'backdrops:retro-80s' }, $ => apply($, 'retro80s'))
  on('command.run', { command: 'backdrops:windows-xp' }, $ => apply($, 'winxp'))
  on('command.run', { command: 'backdrops:windows-98' }, $ => apply($, 'win98'))
  on('command.run', { command: 'backdrops:macintosh-retro' }, $ => apply($, 'mac'))
  on('command.run', { command: 'backdrops:linux' }, $ => apply($, 'linux'))
  on('command.run', { command: 'backdrops:christmas-fireplace' }, $ => apply($, 'xmasFire'))
  on('command.run', { command: 'backdrops:christmas-village' }, $ => apply($, 'xmasVillage'))
  on('command.run', { command: 'backdrops:christmas-snowglobe' }, $ => apply($, 'xmasGlobe'))
  on('command.run', { command: 'backdrops:off' }, $ => apply($, 'plain'))

  // A small picker in the band above the prompt, where backdrops draw (the
  // desktop app); a pick applies and saves the theme at once.
  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.surface !== 'desktop' || e.props.hasSurvey) {
      return next(e)
    }
    const { Box, Select } = $.ui.resolve(e)
    const value = await read($, current)

    return (
      <Box>
        <Select
          key="backdrop"
          label="Backdrop"
          value={value}
          options={PICKER}
          onSelect={picked => {
            if (isChoice(picked)) {
              void apply($, picked)
            }
          }}
        />
      </Box>
    )
  })

  on('ui.render', { component: 'Backdrop' }, ($, e, next) => {
    if (e.surface !== 'desktop' && e.surface !== 'mobile') {
      return next(e)
    }
    const drawing = DRAWINGS[e.props.scene]

    if (drawing === undefined) {
      return next(e)
    }
    const { Svg } = $.ui.resolve(e)
    const source = drawing.source.replace('<style>', `<style>${STILL_AT}`)

    return <Svg source={source} alt={drawing.alt} />
  })
}
