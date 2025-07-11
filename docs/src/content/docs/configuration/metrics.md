---
title: Custom Metrics
sidebar:
    order: 62
---

You can provide custom metrics for the test result evaluation step. Metric can be qualitative (`ok`, `err`, `unknown`) or quantitative (e.g. `0` to `100` good).

A metric should be a `.metric.prompty` in the same folder as the prompt under test.

```markdown wrap title="custom.metric.prompty"
---
name: Custom Test Result Evaluation
description: |
    A template for a custom evaluation of the results.
tags:
    - unlisted
inputs:
    prompt:
        type: string
        description: The prompt to be evaluated.
    intent:
        type: string
        description: The extracted intent of the prompt.
    inputSpec:
        type: string
        description: The input specification for the prompt.
    rules:
        type: string
        description: The rules to be applied for the test generation.
    input:
        type: string
        description: The input to be used with the prompt.
    output:
        type: string
        description: The output from the model execution.
---

system:

## Task

You are a chatbot that helps users evaluate the performance of a model.
Your task is to evaluate the <CRITERIA> based <OUTPUT> provided.

<CRITERIA>
The <OUTPUT> is in English.
</CRITERIA>

## Output

**Binary Decision on Evaluation**: You are required to make a binary decision based on your evaluation:

- Return 'OK' if <OUTPUT> is compliant with <CRITERIA>.
- Return 'ERR' if <OUTPUT> is **not** compliant with <CRITERIA> or if you are unable to confidently answer.

user:
<OUTPUT>
{{output}}
</OUTPUT>
```
