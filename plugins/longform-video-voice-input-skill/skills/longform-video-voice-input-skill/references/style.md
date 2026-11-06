# Default house style

Learned from creator feedback while making a real explainer ("What are AI Agents"). Treat as defaults; ask if the user wants a different look.

## Look
- **Palette:** monochrome only (black, white and grays), like the user's Grok Bot screens. They rejected the warm Claude look ("this is not a Claude video") and they rejected cobalt blue.
- **Colour:** comes only from photos, footage and the user's real app screens.
- **Backgrounds:** plain. No grid, dot pattern or grain ("make it plain").
- **No logos:** no Claude-style starburst and no robot mascot. The agent is `spark()`: a solid dot with a thin ring, and the ring spins while it's "working".
- **No small headings:** no mono caps kickers ("IMAGINE", "CHAPTER 02", "MESSAGE YOUR AGENT"), no top-left breadcrumb, no "ILLUSTRATIVE" tags. A thin progress bar at the bottom is fine.
- **Fonts:** Bricolage Grotesque for headlines (600 normal, 800 for emphasis words in gray `C.clay`) and Inter for UI text.
- **First frame:** fully composed at t=0 with no entrance. A big headline sits beside three tilted phones showing the real app screens.

## Sound
- **Voice only.** A synth music bed was "distracting": its sidechain ducking pumped back up in every pause. No whooshes or accents either ("remove the sounds of transitions and accents").
- **Clean-up:** light by default. The user preferred their own Adobe Podcast enhancement over aggressive local denoising. When unsure, make 10–15 s A/B clips.
- **Loudness:** −14 LUFS, true peak −1.5 dB.

## Keep it entertaining (non-technical audience)
- **Something always moves:** every second needs a meaningful visual. Run `blank_scan.py`. When a scene opens on a spoken phrase ("In this video…", "Having said that…", "My suggestion?"), show that phrase big and centered (`bigSay`), then hand over to the content.
- **Word sync:** headlines rise word by word on the spoken word (`richLine` with VO times, `phraseTimes`, `syncPara`). Key words get the gray emphasis plus an underline marker.
- **Real proof beats diagrams:**
  - the user's own app screens in phone mockups, with a magnified panel of the important line;
  - real web pages (an Amazon search → product → cart flow, the villa's own listing);
  - real photos of the places named (Mt Fuji, Kyoto, BGC Manila, a ryokan in Japan).
- **B-roll:** use full-bleed clips for scene changes and moods (Tokyo streets for "a vacation in Japan", an airplane for "book a flight", a doorstep delivery for "think about that"). Put a dark scrim under the white text.
- **Photo cards:** photos inside cards (tasks, sub-task trees, the "you, doing something else" card) beat icon tiles.
- **Concept animations that worked:**
  - a goal splitting into sub-tasks, then tools, then checks;
  - chatbot vs agent side by side;
  - an "answers → actions" track: a chat bubble travels across the stops and picks up tool badges;
  - the agent steps ticking off next to the real app screen;
  - "you don't have to explain every little step": manual steps get struck through, then checked off by the agent;
  - "can ≠ should";
  - permission toggles;
  - an agent card with a spending limit vs the main card.

## Layout checks the user caught (check these yourself)
- **Text overflowing cards:** wrap long labels onto their own line, or widen the card.
- **Collisions:** labels under a moving token, a chip touching the card above it, badges orbiting into labels.
- **Hotel photos must match the story:** Japan for a Japan trip. Use the specific villa's listing when the narration refers to it.

## Honesty
- **Disclose:** illustrative flights, prices, emails and replies, carts, and permission screens; real third-party screenshots (and when they were captured); and assumed app names.
- **Never invent stats** or claims the narration doesn't make.
