# skillsbento

Free agent skills, packaged as plugins you can install from this one repo in **Claude Code** and **Codex**.

## Install

**Claude Code**

```
/plugin marketplace add donvito/skillsbento
/plugin install stock-analyzer@skillsbento
```

**Codex**

```
codex plugin marketplace add donvito/skillsbento
codex plugin add stock-analyzer@skillsbento
```

Swap `stock-analyzer` for any plugin below. List what's available with `/plugin` (Claude Code) or `codex plugin list`. Update with `/plugin marketplace update skillsbento` (Claude Code) or `codex plugin marketplace upgrade` (Codex).

## Plugins

| Plugin | What it does |
|---|---|
| [`usage-graph`](plugins/usage-graph) | **Claude Code mod**: a band above the prompt with your 5-hour and weekly plan limits (with local reset times) and context window fill, each as a live card with a percentage and a bar. Claude Code only, see its [README](plugins/usage-graph/README.md). |
| [`devils-advocate`](plugins/devils-advocate) | Constructively challenge ideas: test assumptions, weigh counterarguments and alternative hypotheses, examine risks and second-order effects, and finish with an evidence-calibrated recommendation. |
| [`x-for-you-growth`](plugins/x-for-you-growth) | Organic X (Twitter) growth coaching grounded in the open-source For You / Phoenix ranking pipeline (`xai-org/x-algorithm`): weight tables, drafting checklists, first-hour reply ops, reach-death diagnosis, sample usage and live sample outputs. Drafts and coaches only: no spam or engagement pods. |
| [`stream-shorts`](plugins/stream-shorts) | **Stream Studio**: livestream to transcript, subtitles, chapters, one clip per feature, summary reels and animated 9:16 shorts (split-screen or full-frame overlay), with YouTube titles and descriptions. Built-in `grok` and `claude` styles alongside the default neon look. Versioned and reproducible. Claude Code also gets `/process-stream` and `/make-shorts`. Needs ffmpeg and Python, see its [README](plugins/stream-shorts/README.md). |
| [`product-launch-suite`](plugins/product-launch-suite) | Product launch document suite from a name and description: business and market strategy, competitive landscape and feasibility, roadmap and partnerships, sales deck, backed by live web research. |
| [`product-sales-analysis`](plugins/product-sales-analysis) | Sales/ecommerce CSV to an interactive HTML dashboard: KPIs, category performance, YoY growth, marketing ROI, recommendations. |
| [`social-media-analyzer`](plugins/social-media-analyzer) | Social exports (Twitter/X, Instagram, LinkedIn, TikTok) to engagement and conversion insights and a React dashboard. |
| [`x-twitter-stats-analyzer`](plugins/x-twitter-stats-analyzer) | X analytics exports to engagement composition, growth funnel, posting frequency insights and a React dashboard. |
| [`stock-analyzer`](plugins/stock-analyzer) | Chart pattern recognition, live news and technical signal scoring in one interactive HTML report. Not financial advice. |

Each plugin is a folder under `plugins/` with its skill in `skills/<name>/SKILL.md` (`usage-graph` is the exception: a mod, which draws in Claude Code's interface rather than answering requests). Skills trigger from plain requests, for example:

- *"Stress-test my plan and tell me what evidence would change your recommendation"* → devils-advocate
- *"How do I grow on X with the real algorithm?"* → x-for-you-growth
- *"Analyze AMZN stock"* → stock-analyzer
- *"Create a product launch kit for my SaaS tool"* → product-launch-suite
- *"Here's my sales CSV, give me insights"* → product-sales-analysis
- *"Process my stream and make a 30s short about the biggest announcement"* → stream-shorts
- *"Make a Claude-style short from this selfie clip, overlay, no box"* → stream-shorts

In Codex you can also name a skill explicitly, for example `$stock-analyzer analyze AMZN`.

## Repo layout

```
.claude-plugin/marketplace.json      Claude Code marketplace
.agents/plugins/marketplace.json     Codex marketplace
plugins/<name>/
  .claude-plugin/plugin.json         Claude Code manifest
  .codex-plugin/plugin.json          Codex manifest
  skills/<name>/SKILL.md             the skill (plus references/, scripts/, assets/)
  commands/                          optional, Claude Code slash commands
  hooks/                             a mod's hooks module (Claude Code only, e.g. usage-graph)
```

Both marketplaces list the same skill plugins and point at the same folders, so a skill is written once and works in both tools. Mods such as `usage-graph` are listed in the Claude Code marketplace only.

## Adding a plugin

1. Create `plugins/<name>/skills/<name>/SKILL.md` (frontmatter: `name`, `description`).
2. Add `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` (copy an existing pair; Codex's has `"skills": "./skills/"` and an `interface` block).
3. Add the plugin to **both** marketplace files.
4. Check it: `claude plugin validate .`, then `codex plugin marketplace add .` and `codex plugin list`.
5. Bump `version` in the manifests and the Claude marketplace entry when you change a plugin, so installed copies update.

## License

[Apache License 2.0](LICENSE). Copyright 2026 Melvin Dave Vivas. Fonts bundled in `stream-shorts` (Anton, Space Grotesk, JetBrains Mono, Source Serif 4, Inter) are under the SIL Open Font License; their texts are in `plugins/stream-shorts/skills/stream-studio/assets/fonts/`.
