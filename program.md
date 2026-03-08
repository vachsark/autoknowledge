# Research Pipeline Strategy

<!-- Inspired by: https://github.com/karpathy/autoresearch -->
<!-- Credit: Andrej Karpathy, 2025 -->
<!-- Adapted: Standalone strategy doc that humans edit directly. Agents read this and execute it. -->

This document defines the full multi-wave research pipeline strategy. The `/research-session` command reads this file and executes it. Edit this file to change how research sessions work — the command is just a launcher.

**Design principle**: Human edits strategy (`program.md`), agents execute it, results accumulate in `results.tsv`.

---

## Overview

This pipeline runs a multi-wave, multi-agent research session over a Zettelkasten-style `Knowledge/` folder. It consumes topics from a queue file, produces atomic notes following a standardized template, and synthesizes cross-domain connections. Each wave has a time budget proportional to the total session length. The orchestrator runs every wave in sequence, spawning subagents, and writing the final report.

**Time budget formula** (all percentages of total session time):

| Wave | Name                 | Budget                     |
| ---- | -------------------- | -------------------------- |
| 0    | Pre-Flight           | 15 min (fixed, not scaled) |
| 1    | Parallel Research    | 40%                        |
| 2    | Quality Gate         | 15%                        |
| 3    | Synthesis + Skeptic  | 20%                        |
| 4    | Iterative Refinement | 10%                        |
| 5    | Final Report         | 15%                        |

For a 4-hour session: Wave 1 = 96 min, Wave 2 = 36 min, Wave 3 = 48 min, Wave 4 = 24 min, Wave 5 = 36 min.

Scale all non-fixed budgets linearly. For sessions under 2h, collapse Wave 4 (skip refinement) and reduce Wave 3 to 15%.

---

## Wave 0: Pre-Flight (15 min, fixed)

**Goal**: Understand what already exists before spending tokens researching it.

### Steps

1. **Parse session parameters** from arguments. Extract duration (default 4h) and convert to minutes. Calculate wave budgets using the table above. Log the plan.

2. **Pull unchecked topics from the queue file**. Read the file and collect all lines matching `- [ ]` (unchecked checkboxes). These are the candidates.

3. **Determine target topic count** based on session length:
   - 2h session: 20-25 topics
   - 4h session: 35-45 topics
   - 6h session: 55-65 topics
   - Override with `topics=N` argument if provided.
     Select the top N unchecked topics in queue order (earlier = higher priority).

4. **Run semantic search for each candidate topic** to find existing notes (score > 0.6 = relevant coverage). This step prevents duplicating notes that already exist.

5. **Categorize each topic** into one of three buckets:
   - **NEW**: No existing note with score > 0.6. Must be created from scratch.
   - **UPDATE**: Existing note found with score 0.4-0.6, or note exists but is shallow. Target: add sections, improve connections, add recent citations.
   - **SKIP**: Existing note with score > 0.8 and good depth. Already well-covered; do not research.

6. **Cluster topics into research teams**. Group by domain prefix and thematic relatedness. Form 3-4 clusters of 8-12 topics each.

7. **Log pre-flight results** to stdout.

8. **Write pre-flight plan** with full categorization and team assignments.

---

## Wave 1: Parallel Research (40% of session time)

**Goal**: Create and update Knowledge notes in parallel across multiple agent teams.

### Setup

Spawn 3-4 research agents in parallel, one per cluster from Wave 0. Each agent receives:

- Its assigned topic list (with NEW/UPDATE designation per topic)
- The search results from pre-flight (what already exists)
- The note template (see agent definition in `agents/research-team.md`)

**Model**: Sonnet 4.6 for all research teams.

### Inter-agent coordination

When a team discovers something relevant to another team's domain, they flag it in their output under "Inter-agent flags." The orchestrator collects these flags and includes them in Wave 3's synthesis input. Teams do not communicate with each other directly.

### Wave 1 completion

Collect all team outputs. Write a consolidated Wave 1 manifest containing all team reports.

---

## Wave 2: Quality Gate (15% of session time)

**Goal**: Catch errors before they become permanent vault debt.

**Model**: Haiku 4.5 (read-only verification is cheap work).

Spawn one verifier agent (see `agents/research-verifier.md`) to check every note created or updated for:

1. Wikilink validity
2. Template compliance
3. Citation spot-check
4. Cross-reference consistency
5. Depth field accuracy

### Wave 2 completion

If verifier flags critical issues, send them back to the relevant research teams as targeted fix requests.

---

## Wave 3: Synthesis + Skeptic (20% of session time)

**Goal**: Find the highest-value cross-domain connections; filter out weak ones.

This wave runs two agents IN PARALLEL.

### Agent A: Opus Synthesis Agent

**Model**: Opus 4.6 (long-context cross-domain analysis earns the cost).

Tasks:

1. Read all team outputs holistically. Build a mental model of what was learned.
2. Look for structural isomorphisms — cases where a concept from domain A and a concept from domain B solve the same underlying problem.
3. Prioritize: cross-domain > within-domain. Surprising > obvious.
4. Produce 8-12 candidate connections, ordered by perceived novelty.
5. Identify 3-5 research gaps.

### Agent B: Skeptic Agent

**Model**: Sonnet 4.6 (adversarial evaluation).

The skeptic independently evaluates each connection on a single 1-10 scale (see `agents/research-skeptic.md`). Verdicts:

- **KEEP** (7-10): Add to vault as synthesis note.
- **REVISE** (4-6): Promising but needs tighter argument. Send to Wave 4.
- **CUT** (1-3): Surface analogy or unsupported speculation.

### Wave 3 completion

Filter connections by skeptic verdict: KEEP → final report, REVISE → Wave 4, CUT → logged with reasons.

---

## Wave 4: Iterative Refinement (10% of session time)

**Goal**: Rescue REVISE-rated connections with targeted criticism.

Skip this wave entirely if: session duration < 2h, or no REVISE connections exist.

### Steps

1. Collect all REVISE-rated connections from Wave 3.
2. For each, send to a Sonnet agent with the skeptic's critique. Options: strengthen, narrow scope, or abandon.
3. Run strengthened connections through the Skeptic again.
4. Final verdict: KEEP (7+) or CUT. No third chances.

**Model**: Sonnet 4.6 for both refinement and re-evaluation.

---

## Wave 5: Final Report (15% of session time)

**Goal**: Durable record of the session.

**Model**: Opus 4.6 (quality matters for this artifact).

### Steps

1. Write session report with: statistics, methodology, key discoveries, knowledge graph impact, research gaps, quality notes, rejected connections, cost breakdown.

2. Mark completed topics in queue file.

3. Create synthesis notes for KEEP-rated connections.

4. **Append to `results.tsv`** — one row:
   ```
   date	topics	created	updated	skipped	connections_kept	connections_rejected	cost_usd	duration_h	model_mix
   ```

---

## Rules

- **Never research a SKIP-categorized topic**. Pre-flight showed it's already covered.
- **Always use WebSearch for citations**. Never fabricate. Write "citation needed" if you can't find a real source.
- **Wikilinks to non-existent notes are a bug**, not a feature.
- **The skeptic's score is final**. Do not override CUT connections.
- **Write artifacts as you go**. Makes the session resumable if interrupted.
- **Cost matters**. Opus for synthesis + report only. Everything else on Sonnet or Haiku.
- **Time budgets are guidance, not hard stops**. But if a wave is 50% over, cut scope.

---

## Spawn Parameters

All subagents spawn with:

```
mode: "bypassPermissions"
subagent_type: "general-purpose"
run_in_background: true
```

Model per wave:

- Wave 0: Orchestrator (this agent)
- Wave 1: `sonnet` (research teams)
- Wave 2: `haiku` (verifier)
- Wave 3: `opus` (synthesis) + `sonnet` (skeptic), in parallel
- Wave 4: `sonnet` (refinement + re-evaluation)
- Wave 5: `opus` (report writer)
