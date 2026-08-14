# Live sample outputs — x-for-you-growth

Freeze-dried run from Hermes using this skill (2026-08-14).  
Weights rechecked against `home-mixer/params/param.rs` at run time: Reply 5.0, Quote 5.0, Favorite 0.5, OpenLink 0.2, Report -234.0.

These are **demo outputs**, not guarantees of reach. Re-fetch params before quoting numbers as current.

---

## Test 1 — Rewrite weak draft

### Prompt

> Rewrite for better X reach:
>
> "Excited to share my new blog post about personal AI setups! Link in bio. What do you think?"

### Output

**Variant A — hot take**

```text
Most "personal AI" setups fail the first real week.

Not because the model is weak.
Because nobody designed for:
1) one clear daily job
2) human confirm on send
3) a place the answer actually lands (chat, calendar, notes)

If you only pick one job for the next 7 days, what is it?
```

**Variant B — utility / copy-link**

```text
Steal this personal AI setup checklist (non-dev friendly):

- one job only for week 1
- tools the agent may touch (and may not)
- confirm before email/calendar/post
- log what it did
- kill switch

Reply "checklist" if you want the one-pager version.
```

**Variant C — mini-thread opener**

```text
I help people install a personal AI they actually use.

The pattern that works is boring:
narrow job → tight tools → human on send.

Thread: what breaks when you skip each step.
```

**First reply (link)**

```text
Full write-up:
https://example.com/personal-ai
```

| Change | Signal |
|--------|--------|
| Specific claim + list | reply, copy-link |
| Real question | reply |
| Link off root | avoid weak open_link drag |
| No "what do you think?" / emoji | lower not-interested risk |

---

## Test 2 — Draft audit

### Prompt

> Audit this before I send:
>
> "Unpopular opinion: your second brain app is useless without an agent that acts. Notes don't ship work."

### Output

| Dimension | Score | Notes |
|-----------|------:|-------|
| Reply bait | 8/10 | Clear fight; people will defend Notion/Obsidian |
| Quotable | 9/10 | "Notes don't ship work" is QT fuel |
| Copy-link / DM | 4/10 | No artifact to save yet |
| Follow reason | 3/10 | Unclear what you post next |
| Dwell | 5/10 | One-liner; needs proof or 3 beats |
| Negative risk | 6/10 | Fine if not insulting readers personally |
| Link hygiene | 10/10 | No root link |

**Fix list**

1. Name audience (busy parents / SMEs / solo founders).
2. Add 1 concrete act example (calendar book, invoice draft, research pack).
3. End with: "Reply with the last note you never acted on."
4. Soft follow: "I post personal AI installs that do jobs, not capture porn."

**Stronger root**

```text
Unpopular: your second brain is a graveyard without an agent that acts.

Notes don't ship work.
Calendar holds do.
Drafts in the right chat do.

What's the last note you never turned into a next step?
```

---

## Test 3 — First-hour ops

### Prompt

> First-hour plan after I post Variant A at 8:00 SGT. Niche: personal AI.

### Output

```text
T-15  Reply on 3 niche posts (real takes on agents / local LLMs / personal AI tools).
T0    Post Variant A. No link in root.
T0–5  Optional self-reply with link or screenshot only if needed.
T5–40 Stay in thread. Every reply adds info (example, counter, constraint).
T10   Mutual engages → reply fast (bidirectional reply path is high value).
T40   Stop duplicating the post. One quote only if the thread is alive.
Avoid pods, mass tags, "great post!" spam.
```

**Watch 24h:** replies first, then quotes/shares, profile→follow. Likes last.

---

## Skill health checklist (this run)

- [x] Skill loaded (`x-for-you-growth`)
- [x] Weight snapshot verified against public `param.rs`
- [x] Drafting checklist applied (reply / quote / copy-link / follow / negatives / link policy)
- [x] Coach-only (no live post published)
- [x] Recommendations mapped to named signals

## Related files

- Skill body: `../SKILL.md`
- Prompt catalog: `sample-usage.md`
- Param snapshot: `param-baselines-2026-08.md`
