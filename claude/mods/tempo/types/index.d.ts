export type Mode = 'off' | 'go'

declare module 'claude-code' {
  interface PluginState {
    tempo: { mode: Mode }
  }
}
