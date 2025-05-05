---
title: Custom instructions
sidebar:
    order: 27
---

You can provide custom instructions for the test generation for each step
in the prompty front-matter.

```yaml title="summarize.prompty"
instructions:
    inputSpec: "Do not generate input rules for the 'locale' input."
    outputRules: "The chatbot output should always be in English."
```

