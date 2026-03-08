# Credits

External inspirations and how they influenced this project.

| Pattern                                      | Source                                                                                                       | How We Used It                                                                                                                                        |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `program.md` as human-editable strategy file | [autoresearch](https://github.com/karpathy/autoresearch) by Andrej Karpathy                                  | Extracted pipeline strategy from command file into standalone `program.md` that humans edit directly. Agents execute whatever the file says.          |
| `results.tsv` append-only experiment log     | [autoresearch](https://github.com/karpathy/autoresearch) by Andrej Karpathy                                  | Added session-level metrics logging after each run. One row per session, never edited.                                                                |
| Single-metric evaluation (vs. multi-rubric)  | [autoresearch](https://github.com/karpathy/autoresearch) by Andrej Karpathy                                  | Replaced 4-dimension scoring rubric (Insight/Evidence/Value/Falsifiability, each /5) with single 1-10 scale asking one composite question.            |
| Remove hard attempt limits ("never stop")    | [autoresearch](https://github.com/karpathy/autoresearch) by Andrej Karpathy                                  | Removed auto-blocking after 3 failed attempts. Goals now escalate notifications on 4+ attempts but are never automatically abandoned — human decides. |
| Zettelkasten atomic notes                    | [Niklas Luhmann](https://en.wikipedia.org/wiki/Niklas_Luhmann) / [zettelkasten.de](https://zettelkasten.de/) | Note template: one concept per note, standardized frontmatter, explicit connections section with mechanistic descriptions.                            |
| Adversarial evaluation pipeline              | General practice in ML evaluation                                                                            | Separate skeptic agent with adversarial calibration (target 30-50% KEEP rate) to filter overconfident synthesis.                                      |

## Inline Attribution Convention

For future additions, we use inline comments at the point of implementation:

```markdown
<!-- Inspired by: [URL] -->
<!-- Credit: [author], [date] -->
<!-- Adapted: [what we changed] -->
```

For shell scripts:

```bash
# Inspired by: [URL]
# Credit: [author], [date]
# Adapted: [what we changed]
```
