---
name: x-twitter-stats-analyzer
description: Analyzes social media performance data from X (Twitter/X) to extract insights, identify patterns, and generate actionable recommendations. Use when the user uploads CSV/Excel files containing social metrics (impressions, engagements, followers, likes, shares, etc.) and asks for analysis, trends, performance review, content strategy advice, or data visualization.
---

# X (Twitter/X) Analytics

Analyze social media data to extract insights and generate strategic recommendations.

## Analysis Framework

### 1. Data Ingestion & Validation

Read the uploaded file and identify available metrics. Common columns:

| Category | Metrics |
|----------|---------|
| Reach | Impressions, Reach, Views, Profile visits |
| Engagement | Likes, Comments, Replies, Shares, Reposts, Bookmarks, Saves |
| Growth | New followers, Unfollows, Net followers |
| Content | Posts created, Video views, Media views |

Validate data completeness. Note any missing or zero-value columns.

### 2. Calculate Key Performance Indicators
```
Engagement Rate = (Total Engagements / Total Impressions) × 100
Follow Conversion = (New Followers / Profile Visits) × 100
Net Growth = New Followers - Unfollows
Likes per Post = Total Likes / Posts Created
Impressions per Post = Total Impressions / Posts Created
```

### 3. Temporal Analysis

Identify patterns across time periods:

- **Best performing days**: Highest impressions, engagement rate, follower growth
- **Worst performing days**: Lowest metrics, potential issues
- **Posting frequency correlation**: Compare posts/day vs engagement/post
- **Viral content detection**: Days with 2x+ average performance

### 4. Engagement Composition Analysis

Break down total engagements by type:

- Likes (passive appreciation)
- Bookmarks/Saves (high-intent, reference value)
- Replies/Comments (active conversation)
- Shares/Reposts (amplification)

High bookmark rates suggest educational/reference content resonates. High reply rates indicate conversation-driving content.

### 5. Quality vs Quantity Assessment

Analyze the relationship between posting volume and performance:
```python
for each day:
    likes_per_post = likes / posts
    impressions_per_post = impressions / posts

# Compare high-volume vs low-volume days
# Often: fewer high-quality posts > many low-quality posts
```

### 6. Growth Funnel Analysis

Track the conversion funnel:
```
Impressions → Engagements → Profile Visits → New Followers
```

Calculate conversion rates at each stage. Identify bottlenecks.

## Visualization Guidelines

Create an interactive React dashboard with tabs:

1. **Overview**: Key metrics cards, impressions/engagement trend, engagement breakdown pie chart
2. **Engagement**: Daily engagement rate bar chart, likes per post analysis
3. **Growth**: Follower gains/losses, profile visit to follower conversion
4. **Insights**: Key findings cards with actionable recommendations

Use Recharts for charts:
- ComposedChart for dual-axis (impressions + engagements)
- BarChart for daily comparisons
- PieChart for engagement breakdown

## Recommendation Categories

### Posting Schedule Optimization
- Identify best/worst performing days
- Suggest optimal posting frequency based on quality vs quantity analysis
- Recommend content scheduling strategy

### Content Strategy
- Analyze which content types drive bookmarks (save-worthy)
- Identify viral content patterns
- Suggest content pillars based on engagement composition

### Growth Tactics
- Profile optimization suggestions based on follow conversion rate
- Engagement strategy (when to be active in replies)
- Audience retention insights from unfollow patterns

## Output Structure

1. **Summary metrics**: Total impressions, engagements, engagement rate, net followers
2. **Key findings**: 3-5 bullet points of critical insights
3. **Interactive dashboard**: React component with tabbed views
4. **Strategic recommendations**: Prioritized action items with rationale

## Example Insights

- "Monday drove 24% of weekly impressions—analyze what made it viral"
- "Tuesday underperformed despite 13 posts—consider reducing output"
- "30 posts yielded 99 likes/post vs 7 posts with 309 likes/post—quality over quantity"
- "5,312 bookmarks (6.8% of engagements) suggests save-worthy content resonates"
- "10.3% of profile visitors convert to followers—optimize bio for higher conversion"