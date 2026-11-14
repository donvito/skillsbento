import type { ThemeSetArgs } from 'claude-code'

import { makeColors } from './make-colors.js'

// Both looks are dark scenes, so each gives the dark half only.

const mercedes = makeColors({
  label: 'Mercedes #12',
  only: 'dark',
  roles: {
    accent: '#00a19c', // Petronas turquoise
    danger: '#e5484d',
    success: '#4caf50',
    warning: '#e0a526',
    pro: '#9aa6ff',
  },
  dark: {
    gray: {
      anchors: {
        'surface-0': '#0a0d0f',
        'surface-1': '#11161a',
        'surface-2': '#161c20',
        'surface-3': '#1b2226',
        'text-primary': '#eef3f4',
        'text-secondary': '#c3cdd0',
        'text-muted': '#95a2a6',
      },
    },
  },
})

const ferrari = makeColors({
  label: 'Ferrari #44',
  only: 'dark',
  roles: {
    accent: '#e10600', // Rosso
    danger: '#ff5c7a',
    success: '#4fae5a',
    warning: '#ffcc1a',
    pro: '#b48cff',
  },
  dark: {
    gray: {
      anchors: {
        'surface-0': '#100909',
        'surface-1': '#160f0f',
        'surface-2': '#1d1414',
        'surface-3': '#221818',
        'text-primary': '#f6efed',
        'text-secondary': '#d6c9c6',
        'text-muted': '#ab9b97',
      },
    },
  },
})

export const SCENE = {
  mercedes: 'f1-mercedes-kimi',
  ferrari: 'f1-ferrari-hamilton',
} as const

export const MERCEDES_LOOK: ThemeSetArgs = {
  colors: mercedes.theme,
  overrideColorScheme: 'dark',
  backdrop: { scene: SCENE.mercedes, glass: { blur: 6, tint: '#0a0d0f', opacity: 0.5 } },
}

export const FERRARI_LOOK: ThemeSetArgs = {
  colors: ferrari.theme,
  overrideColorScheme: 'dark',
  backdrop: { scene: SCENE.ferrari, glass: { blur: 6, tint: '#120a0a', opacity: 0.5 } },
}

/** Contrast lines that would stop Desktop painting a look; empty when both paint. */
export const UNPAINTED = [...mercedes.problems, ...ferrari.problems].filter(line =>
  line.startsWith("Desktop won't paint"),
)

export const PROBLEMS = { mercedes: mercedes.problems, ferrari: ferrari.problems }
