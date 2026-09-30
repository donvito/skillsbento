---
name: stock-analyzer
description: "Comprehensive stock analysis and research tool for technical analysis, fundamental research, and trading signals. Use when user asks to analyze a stock or ticker, uploads a stock chart image, asks about stock news or catalysts, wants buy/sell signals or trading setups, asks should I buy/sell a stock, or wants to understand price action or chart patterns. Triggers on keywords like stock, ticker, AMZN, AAPL, chart, buy, sell, trade, technical analysis, price target, earnings."
---

# Stock Analyzer

Analyze stocks using technical analysis, fundamental research, and generate actionable trading signals. Outputs a downloadable PDF or Markdown report.

## Workflow

### Step 1: Identify the Stock

Extract ticker symbol from:
- User message (e.g., "analyze AMZN")
- Uploaded chart image (look for ticker in header/title)
- Context clues (e.g., "Amazon stock" → AMZN)

### Step 2: Chart Analysis (if image provided)

Analyze the chart for:

**Price Action**
- Current price, daily change ($ and %)
- Intraday high/low range
- Key price levels (support/resistance)

**Trend Analysis**
- Moving averages (MA5, MA10, MA20, MA50, MA200)
- Price position relative to MAs
- Trend direction (bullish/bearish/neutral)

**Patterns**
- Consolidation, breakout, breakdown
- Double top/bottom, head & shoulders
- Flags, pennants, wedges

**Volume**
- Volume relative to average
- Volume confirmation of price moves
- Distribution vs accumulation

### Step 3: Research Recent News

Use web_search to find:
- News from today/this week affecting the stock
- Earnings dates and expectations
- Analyst upgrades/downgrades
- Sector/industry news
- Macroeconomic factors

**Search queries to use:**
```
{TICKER} stock news today
{TICKER} stock news {CURRENT_MONTH} {CURRENT_YEAR}
{TICKER} earnings date
{TICKER} analyst rating upgrade downgrade
```

### Step 4: Generate Trading Signals

Evaluate and present signals using the framework in `references/signals.md`.

### Step 5: Generate Report

Create an interactive HTML report using the template in `references/report-template.html`.

**Report generation steps:**
1. Copy the HTML template structure
2. Replace all `{PLACEHOLDER}` values with actual analysis data
3. Calculate signal scores and overall bias
4. Generate position sizing calculator with user's risk budget (or default examples)
5. Save as HTML file: `{TICKER}_analysis_{DATE}.html`
6. Present the file to the user

**File naming convention:**
- `AMZN_analysis_2026-01-28.html`
- `TSLA_analysis_2026-01-28.html`

**Key features of HTML report:**
- Tabbed navigation (Summary, Technical, Signals, News, Trade Setup, Calculator)
- Color-coded signal indicators (green=bullish, red=bearish, yellow=neutral)
- Interactive position sizing calculator
- Highlighted key levels and suggestions
- Mobile-responsive design

### Step 6: Position Sizing (if requested)

Help calculate position size:
```
Risk per share = Entry - Stop Loss
Shares = Risk Budget ÷ Risk per share
Position Value = Shares × Entry Price
```

Include in report if user specifies risk budget.

## Important Guidelines

### What NOT to Do
- Never give definitive "buy" or "sell" advice
- Never claim to predict the future
- Never ignore risk management
- Never forget the disclaimer

### Always Include
- Risk disclaimer for trading decisions
- Note that past performance ≠ future results
- Remind user to do their own due diligence
- Offer to explain any concepts

## Reference Files

- **signals.md**: Detailed signal definitions and scoring framework
- **patterns.md**: Chart pattern recognition guide
- **indicators.md**: Technical indicator interpretations
- **report-template.html**: Interactive HTML report template with tabs and calculator
