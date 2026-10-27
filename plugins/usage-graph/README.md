# usage-graph

A Claude Code mod that shows your usage in a band above the prompt, so you can see how close you are to your limits without running `/usage`.

Each metric gets its own card with the current percentage and a bar:

- **5-hour limit**: with the local time it resets and how long until then, e.g. `Resets 4:14 PM · in 4h 40m`
- **Weekly limit**: same, e.g. `Resets Fri 5:34 AM · in 2d 18h`
- **Context**: how full the context window is, e.g. `28k / 200k tokens`

Plan limits are your account's, so the mod keeps your latest limit readings between sessions: a new session shows them straight away, and its own first reply brings them up to date.

The number turns amber at 75% and red at 90%. On an API key (no plan limits) the context card shows the session's cost instead. In the desktop app the band is drawn as cards; in a terminal, as text bars. Collapse the band with its `[-]`.

## Install

At the prompt of a Claude Code terminal session:

```
/plugin install usage-graph --marketplace donvito/skillsbento
```

From a shell:

```
claude plugin install usage-graph --marketplace donvito/skillsbento
```

In the desktop app: click **+** next to the prompt box, then **Plugins**, **Add marketplace** with `donvito/skillsbento`, then add **usage-graph**.

Claude Code only: this is a hooks module (a mod), not a skill, so it has no Codex version.

## Files

```
.claude-plugin/plugin.json   manifest
hooks/hooks.json             names the hooks module
hooks/register.tsx           the mod: records usage readings and draws the band
types/index.d.ts             the session state it keeps
tests/usage-graph.test.tsx   run with `claude plugin test plugins/usage-graph`
```
