---
name: x-for-you-growth
description: Grow on X (Twitter) using the open-source For You / Phoenix ranking signals. Use when the user wants more reach, impressions, followers, or replies; asks how the X algorithm works for creators; needs draft audits, hooks, threads, reply strategy, posting cadence, or a "why did my reach die" diagnosis grounded in xai-org/x-algorithm weights—not engagement pods or spam tactics.
---

# X For You Growth

Turn the open-source X **For You** algorithm (`xai-org/x-algorithm`) into practical drafting, posting, and engagement coaching. Prefer primary sources (repo README + `home-mixer/params/param.rs`) over third-party blogs. Production defaults are mirrored into the repo on a cadence; **re-check weights** before giving numeric advice.

This skill does **not** post, spam, buy engagement, or game safety systems. It drafts and coaches. Confirm before any live publish.

## When to Use

- User wants more reach, impressions, followers, or replies on X/Twitter
- User asks how the X / For You / Phoenix algorithm works for creators
- Drafting hooks, threads, reply strategy, or a posting cadence for X
- Auditing a draft or account against ranking signals
- Comparing formats (text, image, video, quote, thread, link)

**Don't use for:** LinkedIn-only growth, ad buying playbooks, engagement pods/bots, mass follow-unfollow, or circumventing visibility/safety labels.

## Prerequisites

- Optional: fetch latest weights from the public repo before numeric claims
  - https://raw.githubusercontent.com/xai-org/x-algorithm/main/home-mixer/params/param.rs
  - https://raw.githubusercontent.com/xai-org/x-algorithm/main/README.md
  - Scoring math: `home-mixer/scorers/ranking_scorer.rs`
- See also `references/param-baselines-2026-08.md` in this skill (snapshot; may go stale)

## Core model (what actually ranks)

```
Sources (parallel)
  Thunder          → in-network (accounts viewer follows), recent posts
  Phoenix retrieval→ out-of-network two-tower similarity
  SimClusters      → community / engagement-cluster OON
       ↓
Pre-filters (age ≤ ~48h, blocks/mutes, muted keywords, already seen/served, duplicates, OON retweet/reply rules, …)
       ↓
Phoenix ranker     → P(favorite), P(reply), P(repost), P(quote), P(share…), P(dwell…), P(follow), P(negatives…)
       ↓
Final Score ≈ Σ (weight_i × P(action_i))
       ↓
Adjustments: author diversity decay · OON discount · new-author/cold-start boost · VM-ranker diversity reorder
       ↓
Visibility filtering can DROP / interstitial after rank (spam, safety, labels)
```

**Implications:**

1. You need **candidate selection** (followers + OON retrieval/clusters) **and** a high weighted score.
2. The model optimizes **predicted viewer actions**, not abstract "quality."
3. **Negative feedback** (report/mute/not interested/block) crushes score.
4. Content older than the age filter (~**48 hours**) is out of For You consideration.
5. Multiple posts from the same author in one feed are **decayed** (diversity).
6. Out-of-network posts are **discounted** vs in-network (need stronger predicted engagement to surface).

## Published weight baselines (mirror ~2026-08-12)

Re-fetch `param.rs` before treating these as current. Relative to **favorite = 0.5**:

| Signal | Default weight | ≈ × favorite | Creator takeaway |
|--------|----------------|--------------|------------------|
| Share via copy link | 20.0 | 40× | Make something people save/forward |
| Bidirectional-follow **reply** boost | +15.0 on reply path | huge | Mutuals replying (and deep reply chains with people who follow each other) are elite |
| Reply | 5.0 | 10× | Optimize for conversation, not likes |
| Quote | 5.0 | 10× | Quotable, disagreeable, specific takes |
| Share via DM | 5.0 | 10× | Private "you need to see this" value |
| Follow author | 4.0 | 8× | Profile-worthy posts convert lurkers |
| Share (general) | 2.0 | 4× | Shareable one-liners / frames |
| Retweet | 1.0 | 2× | Amplification still matters |
| Favorite (like) | 0.5 | 1× | Weak alone; vanity metric |
| Click | 0.4 | 0.8× | Curiosity / expand still helps |
| Open link | 0.2 | 0.4× | External links are **weak positives** in-score (and often hurt stay-on-platform behavior in practice) |
| Photo expand / video open / VQV | ~0.05 | tiny | Media helps via dwell/expand, not as a magic multiplier alone |
| Continuous dwell time | 0.004 | tiny per unit | Long readable content still compounds via attention heads |
| Not dwelled | -0.02 | small neg | Instant skips hurt |
| Not interested | -43.2 | catastrophic | Topic mismatch / bait fatigue |
| Block author | -31.2 | catastrophic | Polarizing-to-hostile is risky |
| Mute author | -58.8 | catastrophic | |
| Report | -234.0 | nuke | Spam, scams, harassment, policy breaks |

Also important (not a simple weight):

- **Author diversity:** `decay=0.5`, `floor=0.25` → 2nd post from same author heavily attenuated in one feed build.
- **OON factor:** `0.75` (topic OON `0.5`) → discovery posts need stronger predicted engagement than follower feed posts.
- **Cold-start / new-author boost** exists for low-impression authors (quality + early velocity still required).
- **OON-style discount** can also hit **in-network replies/reposts** when that rescoring flag is on.

Third-party "author reply = 150 likes" lore comes from older hand-tuned systems. **Current public Phoenix weights emphasize reply/quote/share/copy-link/follow and mutual-reply boosts** — treat old absolute multipliers as directional only unless you re-derive them from live `param.rs` + scorer code.

## Procedure

### 1) Refresh algorithm facts when stakes are high

If the user needs numeric claims or the repo may have moved, re-read `param.rs` and the README scoring section.

Completion: you can state last-synced defaults and whether reply/share/report weights changed.

### 2) Diagnose the growth goal

Capture: niche, audience, current follower band, posting frequency, best/worst recent posts, link-in-bio needs, Premium or not, primary KPI (followers vs site clicks vs authority).

Completion: one-sentence goal + constraint list.

### 3) Account hygiene (candidate + trust layer)

Coach, do not automate abuse:

- Clear niche bio + pinned proof post (raises follow conversion when `P(follow)` fires)
- Healthy follow graph (engage real peers; avoid mass follow/unfollow patterns that look inauthentic — behavioral detection / cred systems exist)
- Check **Under the Hood** labels if reach suddenly dies: https://x.com/i/under_the_hood
- Remove spammy media, engagement bait templates, misleading claims that drive reports/mutes

Completion: short account checklist with pass/fail.

### 4) Draft for high-weight actions

When writing or reviewing a post, force these properties:

1. **Reply bait without empty "thoughts?"** — specific claim, prediction, tradeoff, or sharp question a niche peer can answer in one line.
2. **Quotable core** — one sentence others can quote-tweet with their own spin.
3. **Copy-link / DM worthiness** — "send this to X role" utility (checklist, non-obvious number, crisp framework).
4. **Follow reason** — reader should know what they get by following (series, beat, POV).
5. **Dwell** — short paragraphs, concrete nouns, media that rewards expand; threads when depth beats a blob.
6. **Minimize negatives** — no scrape-bait, fake urgency, tag-spam, or topic bait-and-switch.

**Format defaults:**

| Format | Use when | Notes |
|--------|----------|--------|
| Single text | Hot take / news reaction | Highest reply rate if opinionated and specific |
| Image + text | Diagram, screenshot, before/after | Photo expand is a real head; keep text self-contained |
| Native video | Demo, talking head, screen record | Optimize completion / VQV; native upload, not YouTube link as the post |
| Thread (3–7) | Teaching / story | First tweet is the ad; each line earns the next; end with a reply prompt |
| Quote-tweet | Commentary on a primary source | Your frame must stand alone if parent is collapsed |
| Link | Distribution of off-platform asset | Prefer **value in main post**, link in **first reply** (or later) so ranking is not wedded to weak `open_link` |

**Link policy:** score weight for open-link is low; many creators still see weaker distribution with external URLs in the root post. Default: native insight first, URL in reply unless user insists otherwise.

Completion: draft has hook, body, CTA-to-reply or follow, and optional media note.

### 5) Timing and first-hour ops (velocity)

For You still needs early positive actions so OON retrieval/social proof can fire:

1. Post when **core followers are online** (use their history / analytics if available).
2. Block **20–40 minutes** after posting for real replies (not emoji spam).
3. Reply in ways that **add information** (extends dwell + more reply probability on the thread).
4. Soft-seed: reply thoughtfully on 3–5 niche posts before/after your post (human, on-topic — not "great post!" spam).
5. Do **not** blast the same link 10 times; author diversity + spam labels will punish.

Completion: post plan includes time window + reply SOP.

### 6) Cadence vs diversity penalty

- Prefer **fewer stronger posts** over many near-duplicates the same hour.
- There is **author diversity decay** inside a single feed assembly: back-to-back near-identical posts cannibalize each other.
- There is a **~48h age cutoff** for For You candidates — evergreen recycling only helps if reposted/refreshed as a new candidate with new engagement, not as infinite old inventory.

Completion: weekly calendar with spacing, not a firehose.

### 7) Growth loops that match the math

Priority order for organic growth:

1. **Conversation density** on your posts (replies + your substantive replies)
2. **Quotes and copy-link shares** (high weights)
3. **Follow conversions** from profile-worthy posts
4. **In-network amplification** from mutuals (bidirectional reply boost path)
5. **Cluster belonging** via consistent niche (SimClusters + Phoenix history)
6. Likes last (lowest positive engagement weight)

Avoid: pods, reply-guy spam under huge accounts, engagement bait that triggers not-interested/report.

### 8) Deliverables by request type

| User ask | Deliver |
|----------|---------|
| Explain algorithm | Short pipeline + weight table + caveats + links to repo |
| Write a post | 2–3 variants optimized for reply/quote/share; hook graded |
| Content audit | Score draft on reply, quote, share, follow, dwell, negative risk |
| 30-day plan | Niche pillars, cadence, reply hours, metrics to watch |
| Thread | Outline + tweet-by-tweet with completion CTA |
| "Why did reach die?" | Checklist: age, labels/UTH, spam patterns, link-only posts, diversity spam, topic drift, negatives |

## Quick drafting checklist

- [ ] Specific audience + one clear POV in line 1
- [ ] Invites a **real reply** (not generic engagement bait)
- [ ] One **quotable** line
- [ ] Useful enough to **copy link / DM**
- [ ] Media native if used; text works if media fails
- [ ] External link deferred to reply (default)
- [ ] No multi-post spam in the same window
- [ ] Plan to **answer replies** in first hour
- [ ] Topic matches account niche (reduces not-interested)
- [ ] Nothing that invites mass report/mute

## Metrics that matter (coach the user)

Watch for 24–48h per post:

1. **Replies** and reply rate (primary)
2. **Quotes + shares** (incl. soft signals if available)
3. **Profile visits → follows**
4. **Bookmark / share behavior** if shown in analytics
5. Dwell proxies: detail expands, video completion
6. Negative: "not interested," blocks, reports (if visible), sudden distribution cliffs → Under the Hood

Deprioritize raw like count as the success metric.

## Pitfalls

1. **Stale third-party weight tables.** Always prefer live `param.rs`. Blogs often mix 2023 hand-tuned weights with 2026 Phoenix.
2. **Like farming.** Favorite weight is low; reply/quote/share/follow dominate.
3. **Link-in-root habit.** Weak score contribution; often worse distribution in practice.
4. **Thread-as-essay dump.** First tweet must earn the click; each hop needs a reason.
5. **Engagement bait** ("like if you agree") → not-interested and mute risk.
6. **Spam replies under celebrities.** Short-term impressions, long-term cred/label risk.
7. **Ignoring negatives.** One report weight dwarfs many likes.
8. **Posting 8 near-duplicates daily.** Author diversity + filters + fatigue.
9. **Topic whiplash.** Phoenix user history + SimClusters reward coherent niches; random viral formats train the wrong retrieval neighbors.
10. **Promising guaranteed virality.** System is personalized per viewer; same post scores differently for every user.

## Verification

- Algorithm summary cites **repo paths** and notes param sync uncertainty.
- Every growth recommendation maps to a **named signal** (reply, quote, share_via_copy_link, follow_author, OON discount, age filter, diversity decay, VF/labels).
- Drafts pass the **Quick drafting checklist**.
- If user reports dead reach: include Under the Hood + hygiene checklist before "just post more."


## Sample usage

Worked prompts and abbreviated ideal answers live in [`references/sample-usage.md`](references/sample-usage.md).

Full freeze-dried agent outputs from a live skill test: [`references/sample-output-live.md`](references/sample-output-live.md).

| Prompt | What you should get |
|--------|---------------------|
| "How does For You actually rank posts?" | Pipeline + weight hierarchy + 48h/OON/diversity caveats + repo links |
| "Rewrite: Excited to share my blog… link in bio" | 2–3 variants optimized for reply/quote/share; URL moved to reply; signal map |
| "Audit this draft before I send" | Scored rubric (reply, quote, copy-link, follow, dwell, negative risk) + fix list |
| "First-hour plan after I post at 8am" | Timed SOP (seed replies, stay present, no spam duplicates) |
| "Impressions collapsed — same niche" | Ordered diagnosis (Under the Hood → bait/links → topic drift → cadence) |
| "7-day plan for a small personal-AI account" | Day-by-day format + target signal + KPI focus on replies/follows |

**Quick invoke lines**

- Explain X For You ranking like a creator coach.
- Rewrite this tweet for replies and quotes; put the link in a reply.
- Audit this draft against Phoenix weights.
- My reach died — run the diagnosis checklist.

## Reference links

- Repo: https://github.com/xai-org/x-algorithm
- README scoring section (How It Works → Scoring and Ranking)
- Params: `home-mixer/params/param.rs`
- Scorer: `home-mixer/scorers/ranking_scorer.rs`
- DeepWiki index: https://deepwiki.com/xai-org/x-algorithm
- Under the Hood: https://x.com/i/under_the_hood
- Local snapshot: `references/param-baselines-2026-08.md`
- Sample prompts/outputs: `references/sample-usage.md`
- Live freeze-dried run: `references/sample-output-live.md`
