# skillsbento

A collection of Claude Code skills for business analytics, market research, and financial analysis.

## Skills

### [product-launch-suite](./skills/product-launch-suite)
Generates a complete product launch document suite from a product name and description. Produces four professional files: Business & Market Strategy, Competitive Landscape & Feasibility, Product Roadmap & Partnerships, and a Sales Deck — backed by live web research.

### [product-sales-analysis](./skills/product-sales-analysis)
Analyzes sales/ecommerce CSV data and generates an interactive HTML dashboard with KPIs, category performance, YoY growth trends, marketing ROI, and prioritized recommendations.

### [social-media-analyzer](./skills/social-media-analyzer)
Analyzes social media performance data (Twitter/X, Instagram, LinkedIn, TikTok) from CSV/Excel exports. Computes engagement rate, follow conversion, viral content patterns, and outputs a React dashboard with strategic recommendations.

### [stock-analyzer](./skills/stock-analyzer)
Comprehensive stock analysis tool combining chart pattern recognition, live news research, and technical signal scoring. Generates a downloadable interactive HTML report with a tabbed layout and position sizing calculator.

### [x-twitter-stats-analyzer](./skills/x-twitter-stats-analyzer)
Dedicated X (Twitter) analytics skill. Ingests X analytics exports and produces engagement composition analysis, growth funnel breakdowns, posting frequency insights, and an interactive React dashboard.

## Usage

Each skill lives in its own directory with a `SKILL.md` that defines its trigger phrases, workflow, and output format. To use a skill, install it in Claude Code and invoke it by describing your task — for example:

- *"Analyze AMZN stock"* → stock-analyzer
- *"Create a product launch kit for my SaaS tool"* → product-launch-suite
- *"Here's my sales CSV, give me insights"* → product-sales-analysis

## License

[MIT](./LICENSE)
