---
title: Prompt Format
sidebar:
    order: 21
---

PromptPex supports markdown-based prompt format based on [Prompty](https://www.prompty.ai/); these are just markdown with a bit of syntax to
represent messages and the input/output signature of the prompt.

The `demo` prompt below defines a set of parameters (`inputs` as a set of JSON schema types).
The `system`/`user` messages are separate by `system:`, `user:` markers in the markdown body.
It uses the Jinja2 template engine to insert values (`{{joke}}`).
The `scenarios` array is used to expand the test generation with further input specification and optional input values.

```md
---
name: A demo
inputs:
    joke: "how do you make a tissue dance? You put a little boogie in it."
    locale: "en-us"
---

system:
You are an assistant
and you need to categorize a joke as funny or not.
The input local is {{locale}}.

user:
{{joke}}
```

## Schema

The JSON schema of the prompt front matter is available at [https://microsoft.github.io/promptex/schemas/prompt.json](ttps://microsoft.github.io/promptex/schemas/prompt.json).
