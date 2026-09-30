#!/usr/bin/env python3
"""
Product Sales Analysis Script
Analyzes sales data and outputs metrics as JSON for dashboard generation.

Usage:
    python analyze_sales.py <input_csv> [--output metrics.json]

Expected CSV columns (flexible naming):
    - Date: date, Date, DATE, order_date, Order_Date
    - Category: Product_Category, category, Category, product_category
    - Revenue: Revenue, revenue, Sales, sales, Actual_Revenue
    - Units: Units_Sold, units_sold, Quantity, quantity, units
    - Marketing: Marketing_Spend, marketing_spend, marketing (optional)
    - Segment: Customer_Segment, customer_segment, segment (optional)
    - Region: Region, region (optional)
"""

import pandas as pd
import numpy as np
import json
import sys
from datetime import datetime

def find_column(df, candidates):
    """Find first matching column from candidates list."""
    for col in candidates:
        if col in df.columns:
            return col
        if col.lower() in [c.lower() for c in df.columns]:
            return [c for c in df.columns if c.lower() == col.lower()][0]
    return None

def analyze_sales(csv_path, output_path=None):
    """Analyze sales data and return metrics dictionary."""

    # Load data
    df = pd.read_csv(csv_path)

    # Identify columns
    date_col = find_column(df, ['Date', 'date', 'DATE', 'order_date', 'Order_Date'])
    category_col = find_column(df, ['Product_Category', 'category', 'Category', 'product_category'])
    revenue_col = find_column(df, ['Revenue', 'revenue', 'Sales', 'sales', 'Actual_Revenue'])
    units_col = find_column(df, ['Units_Sold', 'units_sold', 'Quantity', 'quantity', 'units'])
    marketing_col = find_column(df, ['Marketing_Spend', 'marketing_spend', 'marketing'])
    segment_col = find_column(df, ['Customer_Segment', 'customer_segment', 'segment'])
    region_col = find_column(df, ['Region', 'region'])
    price_col = find_column(df, ['Price', 'price', 'Avg_Price', 'avg_price'])
    discount_col = find_column(df, ['Discount', 'discount', 'Discount_Pct', 'discount_pct'])

    # Calculate revenue if not present
    if revenue_col is None and price_col and units_col:
        if discount_col:
            df['_Revenue'] = df[price_col] * df[units_col] * (1 - df[discount_col]/100)
        else:
            df['_Revenue'] = df[price_col] * df[units_col]
        revenue_col = '_Revenue'

    # Parse dates
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], dayfirst=True, errors='coerce')
        df['Year'] = df[date_col].dt.year
        df['Month'] = df[date_col].dt.month
        df['Quarter'] = df[date_col].dt.quarter

    metrics = {
        'generated_at': datetime.now().isoformat(),
        'data_info': {
            'rows': len(df),
            'date_range': {
                'start': df[date_col].min().strftime('%Y-%m-%d') if date_col else None,
                'end': df[date_col].max().strftime('%Y-%m-%d') if date_col else None
            },
            'categories': df[category_col].nunique() if category_col else 0,
            'columns_found': {
                'date': date_col,
                'category': category_col,
                'revenue': revenue_col,
                'units': units_col,
                'marketing': marketing_col,
                'segment': segment_col,
                'region': region_col
            }
        }
    }

    # Overall KPIs
    metrics['kpis'] = {
        'total_revenue': round(df[revenue_col].sum(), 2) if revenue_col else 0,
        'total_units': int(df[units_col].sum()) if units_col else 0,
        'total_marketing': round(df[marketing_col].sum(), 2) if marketing_col else 0,
        'avg_revenue_per_day': round(df[revenue_col].sum() / df[date_col].nunique(), 2) if revenue_col and date_col else 0
    }

    if marketing_col and revenue_col:
        metrics['kpis']['overall_marketing_roi'] = round(
            df[revenue_col].sum() / df[marketing_col].sum(), 2
        )

    # Category Performance
    if category_col and revenue_col:
        cat_metrics = df.groupby(category_col).agg({
            revenue_col: 'sum',
            units_col: 'sum' if units_col else 'count',
            **(({marketing_col: 'sum'}) if marketing_col else {})
        }).round(2)

        cat_metrics['revenue_share'] = (cat_metrics[revenue_col] / cat_metrics[revenue_col].sum() * 100).round(1)

        if marketing_col:
            cat_metrics['marketing_roi'] = (cat_metrics[revenue_col] / cat_metrics[marketing_col]).round(2)

        metrics['category_performance'] = cat_metrics.reset_index().to_dict('records')

    # YoY Growth
    if date_col and category_col and revenue_col:
        years = sorted(df['Year'].dropna().unique())
        if len(years) >= 2:
            y1, y2 = years[-2], years[-1]
            yearly = df.groupby(['Year', category_col])[revenue_col].sum().unstack(fill_value=0)

            growth = {}
            for cat in yearly.columns:
                if y1 in yearly.index and y2 in yearly.index:
                    v1, v2 = yearly.loc[y1, cat], yearly.loc[y2, cat]
                    if v1 > 0:
                        growth[cat] = round(((v2 - v1) / v1) * 100, 1)

            metrics['yoy_growth'] = growth
            metrics['years_compared'] = [int(y1), int(y2)]

    # Monthly Trends
    if date_col and revenue_col:
        monthly = df.groupby('Month')[revenue_col].sum().round(2)
        metrics['monthly_revenue'] = monthly.to_dict()

        if category_col:
            monthly_by_cat = df.groupby(['Month', category_col])[revenue_col].sum().unstack(fill_value=0).round(2)
            metrics['monthly_by_category'] = monthly_by_cat.to_dict()

    # Quarterly Performance
    if date_col and revenue_col:
        quarterly = df.groupby('Quarter')[revenue_col].sum()
        total = quarterly.sum()
        metrics['quarterly'] = {
            f'Q{q}': {'revenue': round(v, 2), 'share': round(v/total*100, 1)}
            for q, v in quarterly.items()
        }

    # Segment Analysis
    if segment_col and revenue_col:
        seg = df.groupby(segment_col).agg({
            revenue_col: 'sum',
            units_col: 'sum' if units_col else 'count'
        }).round(2)
        seg['avg_order_value'] = (seg[revenue_col] / seg[units_col]).round(2) if units_col else 0
        metrics['segments'] = seg.reset_index().to_dict('records')

    # Region Analysis
    if region_col and revenue_col:
        reg = df.groupby(region_col)[revenue_col].sum().round(2)
        metrics['regions'] = reg.to_dict()

    # Generate Insights
    insights = []

    if 'yoy_growth' in metrics:
        # Top grower
        top = max(metrics['yoy_growth'].items(), key=lambda x: x[1])
        if top[1] > 20:
            insights.append({
                'type': 'success',
                'title': f"{top[0]}: Rising Star (+{top[1]}% YoY)",
                'description': f"Highest growth category with strong momentum.",
                'action': "Increase inventory and marketing allocation"
            })

        # Declining
        for cat, growth in metrics['yoy_growth'].items():
            if growth < -10:
                insights.append({
                    'type': 'danger',
                    'title': f"{cat}: Declining ({growth}% YoY)",
                    'description': f"Revenue dropped significantly year-over-year.",
                    'action': "Reassess product mix and reduce marketing spend"
                })

    if 'quarterly' in metrics:
        q4 = metrics['quarterly'].get('Q4', {})
        if q4.get('share', 25) < 22:
            insights.append({
                'type': 'warning',
                'title': f"Q4 Weakness (only {q4.get('share', 0)}% of annual)",
                'description': "Missing holiday season opportunity.",
                'action': "Develop Q4-specific promotional strategy"
            })

    if 'category_performance' in metrics and marketing_col:
        cats = metrics['category_performance']
        avg_roi = sum(c.get('marketing_roi', 0) for c in cats) / len(cats)
        for c in cats:
            roi = c.get('marketing_roi', 0)
            if roi < avg_roi * 0.9:
                insights.append({
                    'type': 'warning',
                    'title': f"{c[category_col]}: Low Marketing ROI (${roi}/$ spent)",
                    'description': f"Below average efficiency. Average is ${avg_roi:.2f}.",
                    'action': "Optimize targeting or reduce marketing budget"
                })
                break

    metrics['insights'] = insights

    # Output
    if output_path:
        with open(output_path, 'w') as f:
            json.dump(metrics, f, indent=2, default=str)
        print(f"Metrics saved to {output_path}")

    return metrics

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python analyze_sales.py <input_csv> [--output metrics.json]")
        sys.exit(1)

    csv_path = sys.argv[1]
    output_path = None

    if '--output' in sys.argv:
        idx = sys.argv.index('--output')
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    metrics = analyze_sales(csv_path, output_path)

    if not output_path:
        print(json.dumps(metrics, indent=2, default=str))
