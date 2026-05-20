# Engagement Tracking — Deferred Plan

**Status:** Parked. Revisit only after the site shows sustained readership (target: ~30 returning weekly visitors for ≥4 consecutive weeks, measured via GoatCounter Phase 1 if enabled, or via informal signal from colleagues / LinkedIn shares).

**Why deferred:** Counters are noise without an audience. Adding them too early risks rendering "0 / 0 / 0" everywhere, which signals abandonment more than it signals engagement. Validate traction first.

## Trigger to resume

Begin Phase 1 when **any** of the following is true:
- LinkedIn / colleague shares produce a recurring referrer pattern in raw GitHub Pages logs (if accessible) or anecdotal "I check this daily" feedback from ≥3 distinct readers
- Daily unique visitors exceed ~20 for two consecutive weeks
- A colleague specifically asks "what's getting clicked"

## Architecture (unchanged from original plan)

```
Reader → docs/index.html ──┬─→ GoatCounter (clicks, outbound links)
                           └─→ Cloudflare Worker (thumbs) → KV store

Daily 17:00 UTC Action: pull GoatCounter API + Worker /counts
                      → write docs/data/engagement-latest.json
                      → write docs/data/engagement-YYYY-MM-DD.json (history)
                      → rebuild index.html with badges
                      → commit & push
```

Both third-party services have free tiers comfortably above expected traffic. Site remains static.

## Phase 1 — Baseline (clicks only, no UI exposure)

Goal: ~1–2 weeks of click data before exposing counters, so we have a denominator and can sanity-check the pipeline.

- [ ] Create GoatCounter account → subdomain `clintrialist.goatcounter.com`
- [ ] Add tracker `<script data-goatcounter="..." async src="//gc.zgo.at/count.js">` to `docs/index.html`
- [ ] Enable outbound link tracking (GoatCounter setting)
- [ ] Stable item IDs: `sha1(canonical_url)[:12]` — new `pharma_report/engagement.py`
- [ ] GitHub repo secret `GOATCOUNTER_TOKEN` (read-only API token)
- [ ] New `scripts/snapshot_engagement.py`:
  - Fetches `GET /api/v0/stats/hits` for the previous UTC day
  - Maps URL → click count
  - Writes `docs/data/engagement-latest.json` and `docs/data/engagement-YYYY-MM-DD.json`
- [ ] Extend `.github/workflows/aggregate.yml`: run snapshot after `run.py`
- [ ] Tests: ID stability, snapshot file shape, handling of empty API response
- [ ] Do NOT render counts yet — accumulate data only

## Phase 2 — Worker + thumbs (read-only display first)

- [ ] Cloudflare account + Workers + KV namespace `clintrialist_votes`
- [ ] `worker/src/index.ts` endpoints:
  - `POST /vote` body `{id, v: "up"|"down"}` — increments KV, rate-limited by `CF-Connecting-IP` (e.g., 10 votes/IP/hour via KV TTL keys)
  - `GET /counts` → `{ "<id>": {up, down} }`, edge-cached 60s
  - CORS allowlist: `https://gcicc.github.io` only
- [ ] `worker/wrangler.toml` + `worker/README.md`
- [ ] Snapshot script also pulls `GET /counts` and merges into engagement JSON
- [ ] HTML builder renders `🖱 47 · 👍 12 · 👎 2` badge per item — read-only at first
- [ ] Threshold: hide badges below `n ≥ 5`

## Phase 3 — Interactive thumbs + sort

- [ ] Thumb buttons; client JS POSTs to Worker, optimistic UI update
- [ ] Sort toggle: Latest (default) / Most engaged (7d)
- [ ] "Top 10 this week" collapsible panel (default closed)
- [ ] Decision: accept that URL churn resets vote buckets; document it

## Out of scope

- Per-reader auth / dedup
- Comments
- Email digests of top items
- Engagement-weighted ranking of **Regulatory Watch** items — keep that section chronological regardless

## Open questions to resolve before Phase 1

1. GoatCounter subdomain name — `clintrialist`?
2. Show raw counts, or only relative rank ("top quartile this week")?
3. Apply engagement signals to all sections, or exclude Regulatory Watch?
4. Render badges below `n ≥ 5`?

## Effort estimate

- Phase 1: ~half a day
- Phase 2: ~1 day
- Phase 3: ~half a day

---

## Fine-print block (to render in site footer when Phase 2+ ships)

> **About the counters.** These are uncontrolled, self-selected engagement signals — not measures of scientific merit, methodological rigor, or clinical importance. Read them like a coffee-room straw poll: directionally interesting, never decisive.
>
> Specifically:
>
> - **Click counts conflate exposure with interest.** Items rendered near the top of the page or in the leftmost column are seen by more readers; this is position bias, not preference. No correction is applied.
> - **The denominator is unknown and unstable.** Daily visitor counts vary; a "12-click" item on a quiet Tuesday is not comparable to a "12-click" item the day a major guidance drops.
> - **Thumbs are anonymous and unauthenticated.** Votes are rate-limited per IP but not de-duplicated per reader. Treat them as susceptible to ballot stuffing, bot traffic, and the silent-majority problem — the people who liked something most are not necessarily the people who clicked the thumb.
> - **Engagement ≠ endorsement.** A high thumbs-down count may reflect controversy, surprise, or disagreement with the headline framing — not the underlying study.
> - **Selection bias is everywhere.** The aggregator chooses what readers see; the readership self-selects to be here; the voters self-select within that. Three layers of filtering before a single number is recorded.
> - **Small numbers are noise.** Differences below roughly `n = 30` are within the range you'd expect from random variation alone. Badges below `n = 5` are hidden for this reason.
> - **Data is captured once daily at 17:00 UTC** from third-party services and may lag, double-count on retries, or drop events during outages. No SLA. No reconciliation.
>
> If you find yourself using these numbers to make a real decision — about which method matters, which paper to read, which guidance to track — stop and find a better source.
