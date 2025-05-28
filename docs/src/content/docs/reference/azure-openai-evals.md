---
title: Azure OpenAI Evaluations
sidebar:
    order: 28.1
---

PromptPex support exporting the generated tests into a [Azure OpenAI Evaluations](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/evaluations?tabs=question-eval-input).
PromptPex will generate an **eval** and launch an **eval run** for each Model Under Test (MUT) in the test generation.

## Azure OpenAI

To enable this mode, you need to

- set the `AZURE_OPENAI_ENDPOINT` environment variable to your Azure OpenAI API endpoint
- set the `createEvalRuns` parameter to true in the web interface or on the command line.

The Azure OpenAI models that can be used as **Model Under Test** are available at [Azure OpenAI Models](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/evaluations?tabs=question-eval-input).
