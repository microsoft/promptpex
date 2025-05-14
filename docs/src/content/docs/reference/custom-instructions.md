---
title: Custom instructions
sidebar:
    order: 27
---

You can provide custom instructions for the test generation for each step
in the prompty front-matter.

```yaml title="summarize.prompty"
instructions:
    inputSpec: "..."
    outputRules: "..."
    inverseOutputRules: "..."
    intent: "..."
    testExpansion: "..."
```

## Example

You can influence the input specification generation by injecting prompting instructions.

```md wrap
---
instructions:
    outputRules: "Ignore the 'safety' section, it is handled elsewhere."
---
```
