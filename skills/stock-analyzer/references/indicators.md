# Technical Indicators Reference

## Moving Averages

### Simple Moving Average (SMA)
- **Calculation**: Average of closing prices over N periods
- **Common periods**: 5, 10, 20, 50, 100, 200

| MA Period | Use Case |
|-----------|----------|
| MA5/MA10 | Very short-term trend, day trading |
| MA20 | Short-term trend, swing trading |
| MA50 | Medium-term trend |
| MA200 | Long-term trend, institutional reference |

### MA Crossover Signals

| Crossover | Name | Signal |
|-----------|------|--------|
| MA20 crosses above MA50 | Golden cross (minor) | Bullish |
| MA50 crosses above MA200 | Golden cross (major) | Strong Bullish |
| MA20 crosses below MA50 | Death cross (minor) | Bearish |
| MA50 crosses below MA200 | Death cross (major) | Strong Bearish |

### MA as Support/Resistance
- Price often bounces off key MAs in trending markets
- MA200 is watched by institutions → self-fulfilling
- First touch of MA after distance = likely bounce
- Multiple touches of MA = weakening, likely break

## Relative Strength Index (RSI)

**Calculation**: Measures speed/change of price movements (0-100)

| RSI Range | Interpretation |
|-----------|----------------|
| > 80 | Extremely overbought |
| 70-80 | Overbought |
| 50-70 | Bullish momentum |
| 40-50 | Neutral |
| 30-40 | Bearish momentum |
| 20-30 | Oversold |
| < 20 | Extremely oversold |

### RSI Signals
- **Bullish divergence**: Price makes lower low, RSI makes higher low → potential reversal up
- **Bearish divergence**: Price makes higher high, RSI makes lower high → potential reversal down
- **Failure swing**: RSI breaks its own support/resistance → confirms momentum shift

## MACD (Moving Average Convergence Divergence)

**Components**:
- MACD Line: 12 EMA - 26 EMA
- Signal Line: 9 EMA of MACD Line
- Histogram: MACD Line - Signal Line

### MACD Signals

| Signal | Interpretation |
|--------|----------------|
| MACD crosses above Signal | Bullish |
| MACD crosses below Signal | Bearish |
| MACD crosses above zero | Bullish momentum confirmed |
| MACD crosses below zero | Bearish momentum confirmed |
| Histogram growing | Momentum increasing |
| Histogram shrinking | Momentum weakening |

## Bollinger Bands

**Components**:
- Middle band: 20-period SMA
- Upper band: SMA + 2 standard deviations
- Lower band: SMA - 2 standard deviations

### Bollinger Band Signals

| Condition | Interpretation |
|-----------|----------------|
| Price touches upper band | Overbought / strong trend |
| Price touches lower band | Oversold / weak trend |
| Bands squeezing (narrow) | Low volatility → breakout coming |
| Bands expanding (wide) | High volatility |
| Price outside bands | Extreme move, likely to revert |

## Volume Indicators

### Volume Analysis

| Pattern | Interpretation |
|---------|----------------|
| Price up + Volume up | Strong buying, trend confirmed |
| Price up + Volume down | Weak rally, potential reversal |
| Price down + Volume up | Strong selling, trend confirmed |
| Price down + Volume down | Weak selling, potential bounce |
| Volume spike | Significant event, watch direction |

### On-Balance Volume (OBV)
- Running total of volume (+ on up days, - on down days)
- **Rising OBV + rising price**: Confirmed uptrend
- **Falling OBV + falling price**: Confirmed downtrend
- **Divergence**: OBV direction differs from price → potential reversal

## Support and Resistance

### Identifying Levels
1. **Previous highs/lows**: Price memory
2. **Round numbers**: Psychological (e.g., $100, $250)
3. **Moving averages**: Dynamic S/R
4. **Volume clusters**: Where most trading occurred
5. **Gap fills**: Unfilled gaps act as magnets

### Level Strength
| Factor | Stronger Level |
|--------|----------------|
| Touches | More touches = stronger |
| Timeframe | Higher timeframe = stronger |
| Volume | More volume at level = stronger |
| Recency | Recent levels = more relevant |

## Indicator Combinations

### Trend Following Setup
- MA alignment (20 > 50 > 200 for bullish)
- MACD above zero and rising
- RSI between 50-70
- Volume confirming moves

### Mean Reversion Setup
- RSI extreme (< 30 or > 70)
- Price at Bollinger Band extreme
- Volume spike suggesting exhaustion
- Candlestick reversal pattern

### Breakout Setup
- Price consolidating (Bollinger squeeze)
- Volume declining during consolidation
- RSI neutral (40-60)
- Clear support/resistance to break

## Indicator Warnings

**Don't over-rely on indicators:**
- Indicators lag price (they're calculated FROM price)
- In strong trends, overbought/oversold can stay extreme
- Multiple indicators often say the same thing (redundancy)
- News/catalysts override technicals

**Best practice:**
- Use 2-3 complementary indicators max
- Combine with price action and patterns
- Consider the broader context (trend, news, sector)
