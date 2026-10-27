export type Sample = {
  t: number
  fiveHour?: number
  fiveHourResetsAt?: string
  sevenDay?: number
  sevenDayResetsAt?: string
  context?: number
  tokens?: number
  window?: number
  usd?: number
}

declare module 'claude-code' {
  interface PluginState {
    'usage-graph': { history: Sample[] }
  }
}
