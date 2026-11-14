import type { ThemeSetArgs } from 'claude-code'

import { makeColors } from './make-colors.js'

type Look = {
  label: string
  scene: string
  accent: string
  pro: string
  danger?: string
  /** How opaque the frosted chat panel is over the scene; brighter scenes need more. */
  glassOpacity?: number
  surfaces: [string, string, string, string]
  text: [string, string, string]
}

// Every scene is dark or sits behind a dark frosted panel, so each look is dark only.
const LOOKS = {
  space: {
    label: 'Space shuttle',
    scene: 'space-shuttle',
    accent: '#4da3ff',
    pro: '#b48cff',
    surfaces: ['#070a14', '#0d1220', '#121828', '#171e30'],
    text: ['#eef2fb', '#c3cbe0', '#93a0bd'],
  },
  fuji: {
    label: 'Mt Fuji',
    scene: 'mt-fuji',
    accent: '#e85d8a',
    pro: '#b48cff',
    danger: '#ff6b4a',
    surfaces: ['#120f1f', '#191528', '#1f1a31', '#25203a'],
    text: ['#f6eff6', '#d6c8da', '#a898b0'],
  },
  paris: {
    label: 'Paris',
    scene: 'paris',
    accent: '#e8b04a',
    pro: '#9aa6ff',
    surfaces: ['#070b1d', '#0d1228', '#121831', '#171e3a'],
    text: ['#f3f1ea', '#d0cbbd', '#a39d8d'],
  },
  rome: {
    label: 'Rome',
    scene: 'rome',
    accent: '#e0714a',
    pro: '#b48cff',
    surfaces: ['#160f14', '#1d151a', '#241a20', '#2a1f26'],
    text: ['#f7efe8', '#dac8bb', '#ad998b'],
  },
  alps: {
    label: 'Swiss Alps',
    scene: 'swiss-alps',
    accent: '#7fb2ff',
    pro: '#c19cff',
    surfaces: ['#070c1a', '#0d1424', '#121a2e', '#172036'],
    text: ['#eef3ff', '#c6d1ea', '#95a3c4'],
  },
  tokyo: {
    label: 'Tokyo Shibuya',
    scene: 'tokyo-shibuya',
    accent: '#ff3d8b',
    pro: '#3de1ff',
    danger: '#ff6b4a',
    surfaces: ['#0a0812', '#110e1b', '#161224', '#1b162c'],
    text: ['#f4f0ff', '#d2cbe6', '#a59cc0'],
  },
  matrix: {
    label: 'Matrix',
    scene: 'matrix',
    accent: '#00e060',
    pro: '#7dffb2',
    surfaces: ['#020a04', '#06120a', '#0a1a0f', '#0e2214'],
    text: ['#d6ffe0', '#a4e8b4', '#6fbf82'],
  },
  retro80s: {
    label: 'Retro 80s',
    scene: 'retro-80s',
    accent: '#ff3ea5',
    pro: '#3ee6ff',
    surfaces: ['#12061f', '#1a0a2c', '#210e38', '#281244'],
    text: ['#fdf0ff', '#e0c3f0', '#b18fc9'],
  },
  winxp: {
    label: 'Windows XP',
    scene: 'windows-xp',
    accent: '#3c8dff',
    pro: '#b48cff',
    glassOpacity: 0.62,
    surfaces: ['#0b1a33', '#10223f', '#152a4b', '#1a3257'],
    text: ['#f2f6ff', '#c8d6f0', '#98aacb'],
  },
  win98: {
    label: 'Windows 98',
    scene: 'windows-98',
    accent: '#3a6fd8',
    pro: '#19b3b3',
    glassOpacity: 0.58,
    surfaces: ['#081c1c', '#0d2626', '#122f2f', '#163838'],
    text: ['#f2f2f2', '#cfd8d8', '#9fb0b0'],
  },
  mac: {
    label: 'Macintosh retro',
    scene: 'macintosh-retro',
    accent: '#7c8cff',
    pro: '#c19cff',
    glassOpacity: 0.58,
    surfaces: ['#121212', '#1a1a1a', '#222222', '#2a2a2a'],
    text: ['#f5f5f5', '#d0d0d0', '#a0a0a0'],
  },
  linux: {
    label: 'Linux',
    scene: 'linux',
    accent: '#f5a623',
    pro: '#5ec8ff',
    surfaces: ['#070b12', '#0d131c', '#121a25', '#17212e'],
    text: ['#e8eef5', '#c0ccd8', '#8fa0b3'],
  },
  xmasFire: {
    label: 'Christmas fireplace',
    scene: 'christmas-fireplace',
    accent: '#e8b04a',
    pro: '#6fcf7a',
    surfaces: ['#140808', '#1c0d0d', '#231212', '#2a1616'],
    text: ['#f8efe9', '#dcc9c0', '#ad978d'],
  },
  xmasVillage: {
    label: 'Christmas village',
    scene: 'christmas-village',
    accent: '#ffcc66',
    pro: '#9ad1ff',
    surfaces: ['#060b1c', '#0c1428', '#111b32', '#16223c'],
    text: ['#eef3ff', '#c6d1ea', '#95a3c4'],
  },
  xmasGlobe: {
    label: 'Christmas snow globe',
    scene: 'christmas-snowglobe',
    accent: '#3fbf8f',
    pro: '#ff8ad8',
    surfaces: ['#051014', '#0a181d', '#0f2026', '#13282f'],
    text: ['#ecf7f6', '#c3dbd8', '#93aeaa'],
  },
  nyc: {
    label: 'New York',
    scene: 'new-york',
    accent: '#ffb84a',
    pro: '#9aa6ff',
    surfaces: ['#060818', '#0c0f24', '#11152e', '#161b38'],
    text: ['#eef0fb', '#c6cbe6', '#959cc0'],
  },
  london: {
    label: 'London',
    scene: 'london',
    accent: '#c9a86a',
    pro: '#7fb2ff',
    surfaces: ['#080b14', '#0e121e', '#131828', '#181e32'],
    text: ['#eef1f6', '#c8cfdc', '#98a2b6'],
  },
  santorini: {
    label: 'Santorini',
    scene: 'santorini',
    accent: '#4f8fe8',
    pro: '#ff9a6a',
    surfaces: ['#120d22', '#19122e', '#201839', '#271e44'],
    text: ['#fbf2f6', '#ddcde0', '#ad9bb3'],
  },
  aurora: {
    label: 'Northern lights',
    scene: 'northern-lights',
    accent: '#3dffb0',
    pro: '#c46bff',
    surfaces: ['#030712', '#081020', '#0c162a', '#111c34'],
    text: ['#eaf6f4', '#c2dcd8', '#8fb0aa'],
  },
  newyear: {
    label: "New Year's Eve",
    scene: 'new-year',
    accent: '#ffd23d',
    pro: '#ff4d8b',
    surfaces: ['#05050f', '#0b0b1c', '#101028', '#151534'],
    text: ['#f4f2ff', '#cfcbe6', '#a19cc0'],
  },
  cafe: {
    label: 'Rainy café',
    scene: 'rainy-cafe',
    accent: '#e0a060',
    pro: '#9ad1ff',
    surfaces: ['#100c0a', '#171210', '#1e1714', '#251d19'],
    text: ['#f6efe8', '#d8cbbf', '#aa9a8c'],
  },
  library: {
    label: 'Cabin library',
    scene: 'cabin-library',
    accent: '#d98a3a',
    pro: '#7fb2ff',
    surfaces: ['#120b06', '#19100a', '#20150e', '#271a12'],
    text: ['#f7efe6', '#dacbbc', '#ab988a'],
  },
  reef: {
    label: 'Underwater reef',
    scene: 'underwater-reef',
    accent: '#ff7a5a',
    pro: '#3de1c8',
    surfaces: ['#04121c', '#081a28', '#0c2234', '#102a40'],
    text: ['#e8f7fb', '#bfdde6', '#8bb2be'],
  },
  deepspace: {
    label: 'Deep space',
    scene: 'deep-space',
    accent: '#c46bff',
    pro: '#3de1c8',
    surfaces: ['#04030c', '#0a0816', '#100c20', '#15102a'],
    text: ['#f2eeff', '#cbc4e6', '#9d95c0'],
  },
  arcade: {
    label: 'Pixel arcade',
    scene: 'pixel-arcade',
    accent: '#3de1ff',
    pro: '#ff4d8b',
    surfaces: ['#040410', '#0a0a1a', '#0f0f24', '#14142e'],
    text: ['#eef0ff', '#c6cae6', '#959cc0'],
  },
  vapor: {
    label: 'Vaporwave',
    scene: 'vaporwave',
    accent: '#ff71ce',
    pro: '#01cdfe',
    surfaces: ['#120826', '#190c33', '#201040', '#27144c'],
    text: ['#fdf0ff', '#e0c3f0', '#b18fc9'],
  },
  blueprint: {
    label: 'Blueprint',
    scene: 'blueprint',
    accent: '#7fb2ff',
    pro: '#ffd23d',
    glassOpacity: 0.55,
    surfaces: ['#06142e', '#0a1c3c', '#0e244a', '#122c58'],
    text: ['#eef4ff', '#c6d4ee', '#94a8cc'],
  },
  dos: {
    label: 'DOS prompt',
    scene: 'dos-prompt',
    accent: '#55ffff',
    pro: '#ffff55',
    glassOpacity: 0.6,
    surfaces: ['#04042a', '#08083a', '#0c0c48', '#101056'],
    text: ['#f2f2ff', '#cfcfee', '#9f9fd0'],
  },
  holland: {
    label: 'Netherlands',
    scene: 'netherlands',
    accent: '#ff7a1a',
    pro: '#5aa0e8',
    glassOpacity: 0.6,
    surfaces: ['#0b1410', '#101b16', '#15231c', '#1a2b22'],
    text: ['#eef6ef', '#c6d8cb', '#94ab9b'],
  },
} satisfies Record<string, Look>

export type TravelTheme = keyof typeof LOOKS

function build(look: Look): { args: ThemeSetArgs; problems: string[] } {
  const { theme, problems } = makeColors({
    label: look.label,
    only: 'dark',
    roles: {
      accent: look.accent,
      danger: look.danger ?? '#e5484d',
      success: '#4caf50',
      warning: '#e0a526',
      pro: look.pro,
    },
    dark: {
      gray: {
        anchors: {
          'surface-0': look.surfaces[0],
          'surface-1': look.surfaces[1],
          'surface-2': look.surfaces[2],
          'surface-3': look.surfaces[3],
          'text-primary': look.text[0],
          'text-secondary': look.text[1],
          'text-muted': look.text[2],
        },
      },
    },
  })
  const args: ThemeSetArgs = {
    colors: theme,
    overrideColorScheme: 'dark',
    backdrop: { scene: look.scene, glass: { blur: 6, tint: look.surfaces[0], opacity: look.glassOpacity ?? 0.5 } },
  }

  return { args, problems }
}

const built = Object.fromEntries(
  Object.entries(LOOKS).map(([key, look]) => [key, build(look)]),
) as Record<TravelTheme, { args: ThemeSetArgs; problems: string[] }>

export const TRAVEL_LOOKS = Object.fromEntries(
  Object.entries(built).map(([key, value]) => [key, value.args]),
) as Record<TravelTheme, ThemeSetArgs>

export const TRAVEL_SCENES = Object.fromEntries(
  Object.entries(LOOKS).map(([key, look]) => [key, look.scene]),
) as Record<TravelTheme, string>

export const TRAVEL_PROBLEMS = Object.fromEntries(
  Object.entries(built).map(([key, value]) => [key, value.problems]),
) as Record<TravelTheme, string[]>
