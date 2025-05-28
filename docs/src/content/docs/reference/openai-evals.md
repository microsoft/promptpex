---
title: OpenAI Evals
sidebar:
    order: 28
---

PromptPex support exporting the generated tests into a [OpenAI Evals Run](https://platform.openai.com/docs/api-reference/evals).
PromptPex will generate an **eval** and launch an **eval run** for each Model Under Test (MUT) in the test generation.

![Screenshot of an evaluation dashboard showing a model named "gpt-4o-mini" with performance scores of 96% for rules compliance and 100% for niceness, passing 29 out of 30 and 30 out of 30 tests respectively. The left sidebar lists navigation options such as Logs, Traces, Assistants, Batches, Evaluations, Fine-tuning, Storage, Usage, and API keys.](https://github.com/user-attachments/assets/988f9b7e-95a9-450f-9475-61a887a3f85f)

## Configuration

To enable this mode, you need to

- set the `OPENAI_API_KEY` environment variable to your OpenAI API key
- set the `createEvalRuns` parameter to true in the web interface or on the command line.

The OpenAI models that can be used as **Model Under Test** are available at [OpenAI Models](https://platform.openai.com/docs/models).
