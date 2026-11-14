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
