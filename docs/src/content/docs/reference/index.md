---
title: Overview
sidebar:
    order: 20
    title: Reference
---

If we treat [LLM prompts as programs](/promptpex/reference/prompts-are-programs), then it makes sense to build tests for those.
This is exactly what started PromptPex: a test generator for LLM prompts.

From a templated prompt,

```md title="speech-tag.prompty" wrap
In this task, you will be presented with two items: 1) a sentence and 2) a word contained in that sentence. You have to determine the part of speech for a given word and return just the tag for the word's part of speech. ​

Return only the part of speech tag. If the word cannot be tagged with the listed tags, return Unknown. If you are unable to tag the word, return CantAnswer.
```

It generates a set of test cases and a compliance evaluation metric.

The generated test cases can be used to:

- distilatte a smaller model to run the prompt and reduce costs (using Azure OpenAI Stored Completions)
- evaluate the prompt performance when migrating to a new model (using OpenAI Evals API)
- evaluate the prompt performance when making changes to the prompt
...