# autoknowledge

A multi-agent research pipeline for building personal knowledge bases. Uses Claude Code to orchestrate parallel research teams, quality gates, and adversarial evaluation of cross-domain connections.

Produces [Zettelkasten](https://zettelkasten.de/overview/)-style atomic notes with verified citations, wikilinks, and cross-domain synthesis.

## How It Works

Three files define the system:

1. **`program.md`** — The research strategy. You edit this. It defines wave structure, time budgets, model selection, quality standards, and rules. The agents execute whatever this file says.

2. **`agents/`** — Agent definitions. Each agent has a specific role (research, verification, adversarial evaluation). They read `program.md` and follow its instructions.

3. **`results.tsv`** — Append-only session log. After each session, one row is added with metrics: topics processed, notes created, connections found, cost, duration.

## Pipeline Architecture

```
Wave 0: Pre-Flight (15 min)
  └─ Vault search to find existing coverage → categorize topics as NEW/UPDATE/SKIP

Wave 1: Parallel Research (40% of session time)
  └─ 3-4 Sonnet agents research topics in parallel → produce atomic notes

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
   claude "/research-session duration=2h"
   ```

### Adapting to Your Setup

The agent files reference `$VAULT_ROOT` as a placeholder. Replace it with your actual vault path. Key paths to configure:

- Knowledge note directory
- Queue file location
- Scratch/output directory
- Vault search script (or remove pre-flight if you don't have one)

## Companion Projects

- [vault-search](https://github.com/vachsark/vault-search) — Local semantic search over markdown vaults. Powers the pre-flight deduplication in Wave 0.

## License

MIT — see [LICENSE](LICENSE).

## Credits

See [CREDITS.md](CREDITS.md) for attribution of external inspirations.
