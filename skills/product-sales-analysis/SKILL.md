---
name: product-sales-analysis
description: |
  Analyze product sales data and generate actionable insights with interactive HTML dashboards.
  MANDATORY TRIGGERS: sales analysis, analyze sales, product performance, sales insights, revenue analysis, sales report, sales dashboard, ecommerce analysis, product analytics, sales trends, category performance, sales metrics.
  Use when user uploads sales/ecommerce CSV data and wants insights, trends, recommendations, or dashboards.
---

# Product Sales Analysis Skill

Analyze sales data to extract actionable business insights and generate interactive HTML dashboards using pure CSS (no frameworks).

## Expected Data Format

CSV with columns like:
- `Date` — Daily/weekly/monthly date
- `Product_Category` — Category name
- `Units_Sold` / `Quantity` — Volume sold
- `Revenue` / `Sales` / `Price` × `Units` — Revenue figures
- `Profit` / `Margin` (optional) — Profitability
- `Marketing_Spend` (optional) — Marketing costs
- `Customer_Segment` / `Region` (optional) — Dimensions

## Analysis Workflow

### Step 1: Load & Explore Data
```python
import pandas as pd
df = pd.read_csv('sales_data.csv')
df['Date'] = pd.to_datetime(df['Date'])
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month
df['Quarter'] = df['Date'].dt.quarter
```

### Step 2: Compute Core Metrics

**By Category:** Total Revenue, Units Sold, Revenue Share (%), Marketing ROI

**Time-Based:** Monthly/Quarterly trends, YoY growth: `((Y2 - Y1) / Y1) * 100`

**By Segment:** Revenue by customer segment, Average order value

### Step 3: Identify Insights

| Pattern | Insight Type | Action |
|---------|--------------|--------|
| YoY Growth > 20% | 🟢 Success | Invest more, expand |
| YoY Growth < -10% | 🔴 Decline | Reassess, reduce spend |
| Marketing ROI < avg | 🟡 Warning | Optimize or cut |
| Q4 < 25% of annual | 🟡 Seasonal gap | Holiday strategy needed |

### Step 4: Generate Dashboard

Output single HTML file. See `assets/dashboard_template.html` for complete structure.

## Dashboard HTML Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    /* Include full CSS from template */
  </style>
</head>
<body>
  <div class="container"><!-- Components --></div>
  <script>/* Charts */</script>
</body>
</html>
```

## CSS Classes Reference

### Layout (prevent horizontal scroll)
```css
html, body { overflow-x: hidden; width: 100%; }
.container { max-width: 1200px; margin: 0 auto; padding: 24px; width: 100%; }
.grid { display: grid; gap: 16px; margin-bottom: 32px; width: 100%; }
.grid > * { min-width: 0; }
.grid-4 { grid-template-columns: repeat(4, 1fr); }
.grid-3 { grid-template-columns: repeat(3, 1fr); }
.grid-2 { grid-template-columns: repeat(2, 1fr); }
.chart-container { position: relative; height: 280px; width: 100%; max-width: 100%; }
.chart-container canvas { max-width: 100% !important; }
```

### Cards
```css
.card { background: #fff; border-radius: 12px; padding: 20px; border: 1px solid #e5e7eb; overflow: hidden; min-width: 0; }
.kpi-value { font-size: 1.75rem; font-weight: 700; margin: 4px 0; }
.kpi-label { font-size: 0.875rem; color: #6b7280; }
```

### Insight Cards
```css
.insight { padding: 16px; border-radius: 8px; display: flex; gap: 12px; }
.insight-success { background: #ecfdf5; border: 1px solid #a7f3d0; }
.insight-warning { background: #fffbeb; border: 1px solid #fde68a; }
.insight-danger { background: #fef2f2; border: 1px solid #fecaca; }
```

### Colors
```css
:root {
  --blue: #3b82f6; --green: #10b981; --amber: #f59e0b;
  --red: #ef4444; --purple: #8b5cf6; --pink: #ec4899;
}
```

## Component Templates

### KPI Card
```html
<div class="card">
  <span class="kpi-label">Total Revenue</span>
  <div class="kpi-value" style="color: var(--blue)">$11.2M</div>
  <span class="kpi-subtitle">+8% YoY</span>
</div>
```

### Insight Card
```html
<div class="insight insight-success">
  <span class="insight-icon">📈</span>
  <div>
    <strong>Category X: +54% YoY</strong>
    <p>Highest growth with strong momentum.</p>
    <p class="insight-action">→ Increase inventory allocation</p>
  </div>
</div>
```

### Progress Bar
```html
<div class="progress-item">
  <div class="progress-header">
    <span>Segment A</span><span>$3.9M (35%)</span>
  </div>
  <div class="progress-bar">
    <div class="progress-fill" style="width: 35%; background: var(--blue)"></div>
  </div>
</div>
```

### Recommendations Footer
```html
<div class="recommendations">
  <h2>📋 Recommendations</h2>
  <div class="rec-grid">
    <div>
      <h4>Invest More</h4>
      <ul><li><span class="check">✓</span> <strong>Action:</strong> Details</li></ul>
    </div>
    <div>
      <h4>Reduce / Reassess</h4>
      <ul><li><span class="cross">✗</span> <strong>Action:</strong> Details</li></ul>
    </div>
  </div>
</div>
```

## Chart.js Config
```javascript
const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];

new Chart(document.getElementById('chartId'), {
  type: 'bar',
  data: { labels: [...], datasets: [{ data: [...], backgroundColor: COLORS }] },
  options: {
    responsive: true,
    indexAxis: 'y',
    plugins: { legend: { display: false } },
    scales: { x: { ticks: { callback: v => '$' + (v/1e6).toFixed(1) + 'M' } } }
  }
});
```

## Output
Save dashboard to: `[name]_sales_dashboard.html`

## Analysis Script
Run `scripts/analyze_sales.py` for automated metric computation.
