# Sample usage — x-for-you-growth

Concrete prompts and abbreviated ideal agent responses. Numbers are illustrative snapshots from `param.rs` (~2026-08); re-fetch before treating as live.

---

## 1) Explain the algorithm (creator plain English)

**User**

> How does the X For You algorithm actually rank posts? Keep it practical for creators.

**Agent should cover**

1. Two candidate pools: **in-network** (Thunder / accounts you follow) + **out-of-network** (Phoenix retrieval + SimClusters).
2. Phoenix predicts many actions (like, reply, repost, quote, share, dwell, follow, negatives…).
3. Score ≈ Σ(weight × probability), then diversity / OON discount / cold-start tweaks.
4. Hard cuts: ~**48h** age, blocks/mutes/keywords, already-seen, visibility labels can still **drop** after rank.
5. Weight hierarchy that matters for creators (order of magnitude, not magic):
   - Copy-link share ≫ reply/quote/DM-share/follow ≫ RT ≫ like ≫ open-link
   - Report / mute / not interested can wipe a pile of likes
6. Link to `xai-org/x-algorithm` + caveat that production weights sync into the repo on a cadence.

**Shape of a good answer (short)**

```text
For You is not "likes = reach."
1) Get into the candidate set (followers + discovery models).
2) Score high on predicted valuable actions (replies, quotes, shares, follows).
3) Avoid negatives and spam labels.
4) Stay fresh (~48h window) and don't flood the same author slot.

Priority: conversation + share-worthiness > vanity likes.
Re-check home-mixer/params/param.rs before quoting exact numbers.
```

---

## 2) Rewrite a weak draft for ranking signals

**User**

> Rewrite this for better X reach:
>
> "Excited to share my new blog post about AI agents! Link in bio. What do you think? 🚀🚀🚀"

**Agent should**

- Kill emoji spam and empty "what do you think?"
- Put **value in the root post** (claim, framework, tension)
- Move URL to **first reply** by default (weak `open_link` weight; stay-on-platform)
- Add a **specific reply hook** + one **quotable** line + follow reason
- Offer 2–3 variants (hot take / checklist / mini-thread opener)

**Example output shape**

**Variant A — hot take (single)**

```text
Most "AI agent" demos die the first time they touch a real calendar or inbox.

The ones that stick do three boring things well:
1) clear tool boundaries
2) human confirm on send
3) logs you can audit

If you ship agents for non-devs, which of the three do you still fake?
```

**First reply (if they need the link)**

```text
Write-up with the checklist + failure modes:
https://example.com/ai-agents
```

**Why this scores better (map to signals)**

| Change | Signal |
|--------|--------|
| Specific claim + numbered utility | reply, quote, copy-link |
| Question only a peer can answer | reply |
| No root external link | avoid weak/open-link distribution drag |
| No emoji/bait | lower not-interested / mute risk |

---

## 3) Draft audit checklist

**User**

> Audit this post before I hit send:
>
> "Unpopular opinion: your RAG pipeline is a liability.
> Vector DB + hope is not a product.
> Thread 🧵"

**Agent scores (example rubric)**

| Dimension | Score | Notes |
|-----------|-------|-------|
| Reply bait | 7/10 | Opinionated; add a sharper question or "disagree if…" |
| Quotable line | 8/10 | "Vector DB + hope is not a product" is QT fuel |
| Copy-link / DM worth | 4/10 | Promise a thread; need substance in T2–T5 |
| Follow reason | 3/10 | Unclear what following you yields |
| Dwell | 5/10 | Hook ok; deliver depth in thread body |
| Negative risk | 6/10 | Fine if you aren't bait-and-switching; avoid insulting readers |
| Link hygiene | 9/10 | No root link |

**Fix list**

1. Pin who it's for (founders / platform eng / consultants).
2. Deliver 3 concrete failure modes in the thread.
3. End with a non-empty CTA: "Reply with your retrieval eval — screenshot OK."
4. Soft follow cue once: "I post agent production postmortems, not tool bingo."

---

## 4) First-hour ops plan

**User**

> I'm posting this AI ops take at 8am SGT. What do I do in the first hour?

**Agent should deliver a timed SOP**

```text
T-15m  Reply thoughtfully on 3 niche posts (real substance, not "great post").
T0     Publish. Do not paste external link in root.
T0–5   Pin a self-reply only if needed (link / extra chart).
T5–40  Stay in replies. Every reply adds information (data, counterexample, clarification).
T10    If a mutual engages, reply fast (bidirectional-reply path is high value).
T40    One quote-worthy restatement only if conversation is alive — not a duplicate spam post.
Avoid  Mass-tagging, engagement pods, identical copy across alts.
```

---

## 5) "Reach died" diagnosis

**User**

> My impressions collapsed this week. Same niche. What should I check?

**Agent checklist (in order)**

1. **Under the Hood** labels: https://x.com/i/under_the_hood  
2. Sudden spike in **links-in-root**, tag spam, or engagement bait  
3. **Topic drift** (Phoenix/SimClusters neighbors changed)  
4. **Cadence spam** (many near-duplicates → author diversity decay + fatigue)  
5. Content that invites **not interested / mute / report**  
6. Posting only evergreen >48h without new candidates  
7. Compare last 10 posts: reply rate and profile→follow, not just likes  
8. Account hygiene: mass follow/unfollow, scraped media, misleading claims  

**Output:** ranked hypotheses + one experiment for the next 3 posts (e.g. "no root links, reply-optimized hooks, 30m reply block").

---

## 6) 7-day micro plan (sample)

**User**

> 7-day plan to grow a small account posting about personal AI / agents. KPI: followers + quality replies.

| Day | Post type | Goal signal |
|-----|-----------|-------------|
| 1 | Single sharp take + reply hour | replies |
| 2 | 5-tweet thread (checklist) | dwell + copy-link |
| 3 | Quote a primary source with your frame | quotes |
| 4 | Rest or light reply-day only | graph warmth |
| 5 | Native demo video <2–3 min | VQV / dwell |
| 6 | "Steal this prompt/SOP" utility post | copy-link + follows |
| 7 | Retrospective: what got replies; double down | learning |

Rules for the week: max 1–2 strong posts/day, niche-coherent, links in replies, 20–40m reply block after each post.

---

## 7) Install / invoke examples (skillsbento / Claude Code)

```text
"Explain X For You ranking like a creator coach."
"Rewrite this tweet for replies and quotes, link in reply."
"Audit this draft against Phoenix weights."
"First-hour playbook after I post at 7pm."
"My reach died — run the diagnosis checklist."
"7-day X plan for a personal-AI niche account."
```
