# X For You param baselines (repo mirror)

**Source:** `https://raw.githubusercontent.com/xai-org/x-algorithm/main/home-mixer/params/param.rs`  
**Comment in file:** mirrored from config feature-switch defaults; last sync noted in-file (~2026-08-12 when this note was written).  
**Re-fetch before numeric claims.**

## Positive / attention weights

| Param | Default |
|-------|---------|
| FavoriteWeight | 0.5 |
| ReplyWeight | 5.0 |
| BidirectionalFollowReplyWeightBoost | 15.0 |
| BidirectionalFollowDwellWeightBoost | 0.0 |
| RetweetWeight | 1.0 |
| QuoteWeight | 5.0 |
| ShareWeight | 2.0 |
| ShareViaDmWeight | 5.0 |
| ShareViaCopyLinkWeight | 20.0 |
| FollowAuthorWeight | 4.0 |
| ClickWeight | 0.4 |
| OpenLinkWeight | 0.2 |
| ProfileClickWeight | 0.0 |
| PhotoExpandWeight | 0.05 |
| VideoOpenWeight | 0.05 |
| VqvWeight | 0.05 |
| DwellWeight | 0.0 |
| ContDwellTimeWeight | 0.004 |
| ContClickDwellTimeWeight | 0.0 |
| QuotedClickWeight | 0.05 |
| QuotedVqvWeight | 0.0 |
| PostUnexploredWeight | 0.02 |

## Negative weights

| Param | Default |
|-------|---------|
| NotInterestedWeight | -43.2 |
| BlockAuthorWeight | -31.2 |
| MuteAuthorWeight | -58.8 |
| ReportWeight | -234.0 |
| NotDwelledWeight | -0.02 |

## Structural multipliers

| Param | Default | Meaning |
|-------|---------|---------|
| EnableAuthorDiversity | true | |
| AuthorDiversityDecay | 0.5 | per extra author appearance |
| AuthorDiversityFloor | 0.25 | min multiplier |
| OonWeightFactor | 0.75 | OON score multiplier |
| TopicOonWeightFactor | 0.5 | topic OON |
| EnableOonRescoreForInNetworkRepliesRetweets | true | discount path can hit IN replies/RTs |
| AgeFilter | ~48 hours | README pre-scoring filters |

## Score formula

```
Final Score = Σ (weight_i × P(action_i))
```

Then author diversity, OON discount, new-author/cold-start adjustments, VM-ranker diversity reorder. Visibility filtering can still DROP after rank.

## Pipeline reminder

Thunder (IN) + Phoenix retrieval (OON) + SimClusters (OON) → hydrate → pre-filters → Phoenix multi-action P() → RankingScorer weights → diversity/OON/cold-start → top-K → VF drop/interstitial → blend ads/WTF.
