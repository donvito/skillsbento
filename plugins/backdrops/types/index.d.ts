// The values backdrops keeps in $.state for the session.

/** A theme key such as 'paris', or 'plain' for none. */
export type BackdropChoice = string

declare module 'claude-code' {
  interface PluginState {
    'backdrops': {
      /** The theme the picker shows as selected. */
      current: BackdropChoice
    }
  }
}
