# Trading Signals Framework

## Signal Categories

### 1. Trend Signals (Weight: High)

| Condition | Signal | Score |
|-----------|--------|-------|
| Price > MA20 > MA50 > MA200 | Strong Bullish | +3 |
| Price > MA20 > MA50 | Bullish | +2 |
| Price > MA20 | Weak Bullish | +1 |
| Price < MA20 | Weak Bearish | -1 |
| Price < MA20 < MA50 | Bearish | -2 |
| Price < MA20 < MA50 < MA200 | Strong Bearish | -3 |

### 2. Momentum Signals (Weight: Medium)

**RSI (if available)**
| RSI Value | Signal | Score |
|-----------|--------|-------|
| > 70 | Overbought (caution) | -1 |
| 50-70 | Bullish momentum | +1 |
| 30-50 | Bearish momentum | -1 |
| < 30 | Oversold (potential bounce) | +1 |

**Price Action Momentum**
| Condition | Signal | Score |
|-----------|--------|-------|
| Higher highs + higher lows | Bullish | +2 |
| Consolidation near highs | Neutral-Bullish | +1 |
| Consolidation near lows | Neutral-Bearish | -1 |
| Lower highs + lower lows | Bearish | -2 |

### 3. Volume Signals (Weight: Medium)

| Condition | Signal | Score |
|-----------|--------|-------|
| Rising price + rising volume | Strong confirmation | +2 |
| Rising price + falling volume | Weak rally (caution) | 0 |
| Falling price + rising volume | Distribution (bearish) | -2 |
| Falling price + falling volume | Weak selling | 0 |
| Volume spike at support | Potential reversal | +1 |
| Volume spike at resistance | Potential rejection | -1 |

### 4. News/Catalyst Signals (Weight: High)

| Catalyst Type | Signal | Score |
|---------------|--------|-------|
| Earnings beat + raised guidance | Strong Bullish | +3 |
| Earnings beat | Bullish | +2 |
| Positive analyst upgrade | Bullish | +1 |
| No significant news | Neutral | 0 |
| Negative analyst downgrade | Bearish | -1 |
| Earnings miss | Bearish | -2 |
| Earnings miss + lowered guidance | Strong Bearish | -3 |
| Upcoming earnings (within 7 days) | High volatility expected | ±0 (flag risk) |

### 5. Support/Resistance Signals (Weight: Medium)

| Condition | Signal | Score |
|-----------|--------|-------|
| Breakout above resistance + volume | Bullish | +2 |
| Testing resistance (multiple times) | Potential breakout | +1 |
| Holding support | Neutral-Bullish | +1 |
| Breakdown below support + volume | Bearish | -2 |
| Testing support (multiple times) | Potential breakdown | -1 |

## Overall Signal Calculation

### Score Interpretation

| Total Score | Bias | Confidence |
|-------------|------|------------|
| +6 or higher | Strong Bullish | High |
| +3 to +5 | Bullish | Medium |
| +1 to +2 | Lean Bullish | Low |
| -1 to +1 | Neutral | - |
| -2 to -1 | Lean Bearish | Low |
| -5 to -3 | Bearish | Medium |
| -6 or lower | Strong Bearish | High |

### Confidence Modifiers

Increase confidence when:
- Multiple signals align (trend + momentum + volume)
- Clear catalyst supports direction
- Price action confirms with clean patterns

Decrease confidence when:
- Signals conflict (bullish trend, bearish volume)
- Major event approaching (earnings, Fed meeting)
- Low volume / illiquid conditions
- Extreme overbought/oversold readings

## Signal Output Template

```
## Trading Signals Summary

| Signal | Status | Score |
|--------|--------|-------|
| Trend | [Status] | [+/-X] |
| Momentum | [Status] | [+/-X] |
| Volume | [Status] | [+/-X] |
| News/Catalyst | [Status] | [+/-X] |
| Support/Resistance | [Status] | [+/-X] |
| **Total** | | **[Sum]** |

**Overall Bias**: [Bullish/Bearish/Neutral]
**Confidence**: [High/Medium/Low]

### Key Levels
- **Entry**: $X.XX
- **Stop-Loss**: $X.XX (risk: X%)
- **Target 1**: $X.XX (reward: X%)
- **Target 2**: $X.XX (reward: X%)
- **Risk/Reward**: X:1

### Catalysts to Watch
- [Catalyst 1 with date if applicable]
- [Catalyst 2]

### Risk Factors
- [Risk 1]
- [Risk 2]
```

## Time Horizon Considerations

### Day Trade (same day)
- Focus: Intraday momentum, volume, support/resistance
- Ignore: Fundamentals, long-term trends
- Key: Tight stop-losses, quick decisions

### Swing Trade (days to weeks)
- Focus: Daily trend, upcoming catalysts, technical patterns
- Balance: Technical + near-term fundamental catalysts
- Key: Define entry/exit before trade

### Position Trade (weeks to months)
- Focus: Weekly trend, earnings trajectory, sector strength
- Heavy: Fundamental analysis, valuation
- Key: Wider stops, patience for thesis to play out
