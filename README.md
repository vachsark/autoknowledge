# autoknowledge

A multi-agent research pipeline for building personal knowledge bases. Uses Claude Code to orchestrate parallel research teams, quality gates, and adversarial evaluation of cross-domain connections.

Produces [Zettelkasten](https://zettelkasten.de/overview/)-style atomic notes with verified citations, wikilinks, and cross-domain synthesis.

## Background

I built this system as part of a larger personal knowledge vault — an Obsidian-based workspace where I use Claude Code agents to automate research, note creation, and knowledge graph maintenance. The original version ran as scheduled background tasks: a "knowledge seeder" agent would pick topics from a queue, research them one at a time, and write notes overnight. It worked, but it was a single-agent pipeline with no quality control, no deduplication, and no way to find cross-domain connections.

Then I came across [Andrej Karpathy's post about autoresearch](https://x.com/karpathy/status/2029701092347630069) — his system for running autonomous ML experiments overnight with Claude Code. A few of his design decisions clicked immediately: using a `program.md` file as a human-editable strategy that agents execute, an append-only `results.tsv` for tracking experiments, and simplifying multi-rubric evaluation to a single-metric score. I decided to let Claude take some of these patterns and rebuild the pipeline around them.

The result is a system that's different from both what I had before and from Karpathy's original (which focuses on ML training experiments, not knowledge research). This repo is the extracted, standalone version of that pipeline.

## What Changed (Before → After)

The original system had been running for about a week when Karpathy's post came out. Here's what it looked like and what changed:

### Before (v1 — Heartbeat-Based Seeder)

```
Daily Schedule:
  14:00 — knowledge-seeder picks 3-5 topics from queue
           └─ Single Sonnet agent researches each sequentially
           └─ Writes notes directly to Knowledge/ folder
           └─ No deduplication check (duplicates happened)
           └─ No quality verification pass

  15:00 — knowledge-analyst (Opus) reviews new notes
           └─ Suggests improvements via goals system
           └─ Flags weak notes for manual review

  01:00 — knowledge-seeder-night (burst mode, 8-10 topics)
           └─ Same single-agent approach, just more topics

Weekly:
  Friday — topic-planner generates new queue items
  Saturday — knowledge-deepdive (single deep topic)
```

**What worked**: Notes got created consistently. The queue kept things organized. Over a few weeks, the vault grew from 0 to ~100 notes.

**What didn't work**: No deduplication — the seeder would sometimes create a note that overlapped heavily with an existing one. No cross-domain synthesis — connections were whatever the single research agent happened to notice. No adversarial filtering — every connection the agent proposed went into the vault, including weak structural analogies. Quality was inconsistent — some notes were detailed, others were stubs. No cost tracking.

### After (v2 — Multi-Wave Pipeline)

Patterns adopted from [autoresearch](https://github.com/karpathy/autoresearch):

| Pattern               | From Karpathy                                    | How We Used It                                                                                     |
| --------------------- | ------------------------------------------------ | -------------------------------------------------------------------------------------------------- |
| `program.md`          | Human-editable strategy file that agents execute | Extracted pipeline logic from command file into standalone doc                                     |
| `results.tsv`         | Append-only experiment log                       | One row per session with metrics (topics, cost, connections)                                       |
| Single-metric scoring | Replaced multi-rubric evaluation                 | Went from 4-dimension rubric (Insight/Evidence/Value/Falsifiability, each /5) to single 1-10 scale |

Patterns that were new (not from Karpathy):

| Pattern                         | Why                                                                               |
| ------------------------------- | --------------------------------------------------------------------------------- |
| Pre-flight vault search         | Search existing notes before researching — prevents duplicates, saves ~30% tokens |
| Parallel research teams         | 3-5 Sonnet agents research different domains simultaneously                       |
| Critique + Deepen (Wave 1.5)    | Critic agent catches weak claims before they become vault debt; +6% RACE on DRB   |
| Quality gate (Haiku verifier)   | Catches broken wikilinks, template violations, fabricated citations               |
| Adversarial skeptic agent       | Independently scores cross-domain connections; calibrated to reject 50-70%        |
| Opus synthesis wave             | Dedicated cross-domain analysis by the strongest model                            |
| Iterative refinement            | REVISE-rated connections get one chance to strengthen their argument              |
| Article output mode             | `output=article` produces 10-15k word research articles instead of atomic notes   |
| Model tiers (full/hybrid/local) | Cost control: full ($12-15/session), hybrid ($3-5), local ($0)                    |
| Queue auto-refill               | Watchdog detects dangling wikilinks and adds them as queue items                  |

## How It Works

Three files define the system:

1. **`program.md`** — The research strategy. You edit this. It defines wave structure, time budgets, model selection, quality standards, and rules. The agents execute whatever this file says.

2. **`agents/`** — Agent definitions. Each agent has a specific role (research, critique, verification, adversarial evaluation). They read `program.md` and follow its instructions.

3. **`results.tsv`** — Append-only session log. After each session, one row is added with metrics: topics processed, notes created, connections found, cost, duration.

## Pipeline Architecture

```
Wave 0: Pre-Flight (15 min, fixed)
  └─ Vault search to find existing coverage → categorize topics as NEW/UPDATE/SKIP

Wave 1: Parallel Research (30% of session time)
  └─ 3-4 Sonnet agents research topics in parallel → produce atomic notes

Wave 1.5: Critique + Deepen (10%)
  └─ Critic agent identifies weak claims, missing perspectives, unsourced facts
  └─ High-severity issues sent back to research teams for targeted deepening

Wave 2: Quality Gate (15%)
  └─ Haiku verifier checks wikilinks, template compliance, citation validity

Wave 3: Synthesis + Skeptic (20%)
  ├─ Opus synthesis agent finds cross-domain connections
  └─ Sonnet skeptic scores each connection 1-10, verdicts: KEEP/REVISE/CUT

Wave 4: Iterative Refinement (10%)
  └─ REVISE connections get one chance to strengthen their argument

Wave 5: Final Report (15%)
  └─ Opus writes session report, creates synthesis notes, logs results
```

## Design Choices

**Pre-flight deduplication**: Before researching anything, we search the existing vault for each topic. This prevents creating duplicate notes and identifies opportunities to deepen existing coverage instead. Saves ~30% of research tokens.

**Adversarial evaluation**: The skeptic agent is calibrated to reject 50-70% of proposed connections. This is intentional — most brainstormed cross-domain connections are surface analogies, not genuine structural insights. The pipeline's value is precisely that it filters aggressively.

**Single-metric skeptic scoring**: We tried a 4-dimension rubric (Insight, Evidence, Value, Falsifiability) and found that a single question — "Would a domain expert in both fields find this genuinely surprising, empirically grounded, and useful?" — produces better signal with less scoring noise.

**Append-only results log**: `results.tsv` never gets edited, only appended. This gives you a running record to track research productivity over time.

**Critique before quality gate**: Wave 1.5 runs a critic agent over all Wave 1 output, flagging weak claims, missing perspectives, unsourced assertions, and shallow sections. Only high-severity issues get sent back to research teams for targeted deepening (max 2 WebSearch calls per issue). This is the highest-impact quality lever in the pipeline — benchmarking on [DeepResearch Bench](https://github.com/google-deepmind/deep_research_bench) showed a +6% improvement in RACE scores.

**Article output mode**: The same pipeline can produce long-form research articles (10-15k words) instead of atomic notes. Pass `output=article prompt="your research question"` to switch modes. In article mode, research teams produce draft sections instead of notes, the critic evaluates argument flow and evidence gaps, synthesis writes the intro/conclusion/transitions, and the skeptic evaluates key claims. The pipeline does not interact with the knowledge queue or create vault notes in article mode.

**Cost-aware model selection**: Opus only runs for synthesis (Wave 3) and final report (Wave 5) — the two tasks where long-context cross-domain analysis justifies the cost. Everything else runs on Sonnet or Haiku.

## Quick Start

### Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI installed
- An Anthropic API key with access to Opus, Sonnet, and Haiku

### Setup

1. Clone this repo into your knowledge vault:

   ```bash
   git clone https://github.com/vachsark/autoknowledge.git
   ```

2. Copy agent files to your Claude Code agents directory:

   ```bash
   cp autoknowledge/agents/*.md .claude/agents/
   ```

3. Edit `program.md` to point at your vault's Knowledge directory and customize the strategy.

4. Create a `Knowledge/_queue.md` file with topics to research:

   ```markdown
   - [ ] Attention mechanisms in transformers
   - [ ] Prospect theory and loss aversion
   - [ ] Dopamine reward prediction error
   ```

5. Run a session:

   ```bash
   # Notes mode (default) — produces atomic Knowledge/ notes
   claude "/research-session duration=2h"

   # Article mode — produces a single long-form research article
   claude "/research-session output=article prompt=\"What are the mechanisms behind spaced repetition?\""
   ```

### Adapting to Your Setup

The agent files reference `$VAULT_ROOT` as a placeholder. Replace it with your actual vault path. Key paths to configure:

- Knowledge note directory
- Queue file location
- Scratch/output directory
- Vault search script (or remove pre-flight if you don't have one)

Agent files in `agents/`:

| Agent                  | Wave | Role                                                |
| ---------------------- | ---- | --------------------------------------------------- |
| `research-team.md`     | 1    | Parallel research (notes + article modes)           |
| `research-critic.md`   | 1.5  | Content quality critic (weak claims, gaps, sources) |
| `research-verifier.md` | 2    | Template/wikilink/citation verifier                 |
| `research-skeptic.md`  | 3    | Adversarial connection evaluator                    |

## Benchmarking with DeepResearch Bench

The pipeline can be evaluated against [DeepResearch Bench (DRB)](https://github.com/google-deepmind/deep_research_bench), a benchmark for long-form research article generation with RACE (comprehensiveness) and FACT (citation accuracy) metrics.

The `scripts/drb-run.sh` script automates this:

```bash
# Run specific DRB tasks through the pipeline (article mode)
bash scripts/drb-run.sh --tasks 52,67,77

# Run all 50 English tasks
bash scripts/drb-run.sh --tasks all-en --duration 1h

# Preview without executing
bash scripts/drb-run.sh --tasks 52,67 --dry-run

# Collect outputs into DRB-compatible JSONL for evaluation
bash scripts/drb-run.sh --collect
```

The script invokes `/research-session output=article` for each DRB task, collects the articles into JSONL format, and copies them to the DRB repo's evaluation directory. You then run DRB's own `run_benchmark.sh` for RACE/FACT scoring.

**Prerequisites**: Clone the DRB repo to `/tmp/deep_research_bench/` (or set `DRB_REPO` in the script). Requires `jq`.

**Configuration**: Edit `drb-run.sh` to set `VAULT_ROOT`, `DRB_REPO`, and `OUTPUT_DIR` for your setup.

## Companion Projects

- [vault-search](https://github.com/vachsark/vault-search) — Local semantic search + knowledge graph for markdown vaults. Powers pre-flight deduplication (Wave 0) and provides entity/relationship context for cross-domain synthesis.

## License

MIT — see [LICENSE](LICENSE).

## Credits

See [CREDITS.md](CREDITS.md) for attribution of external inspirations.
