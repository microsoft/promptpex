---
title: Azure OpenAI Evaluations
sidebar:
    order: 28.1
---

PromptPex support exporting the generated tests into a [Azure OpenAI Evaluations](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/evaluations?tabs=question-eval-input).
PromptPex will generate an **eval** and launch an **eval run** for each Model Under Test (MUT) in the test generation.

![Screenshot of the Azure AI Foundry platform showing evaluation results for a project named "speech-tag (promptpex)." Two model runs are listed: "gpt-4o-mini-2024-07-18" with a score of 93.33% and "gpt-4.1-nano-2025-04-14" with a score of 96.15%. Both runs display green status boxes indicating the number of tests passed. The left sidebar shows navigation options like Home, Model catalog, Chat, Images, and Azure OpenAI Evaluation.](azure-openai-evals.png)

## Configuration

PromptPex uses the Azure OpenAI credentials configured either in environment variables
or through the Azure CLI / Azure Developer CLI. See [GenAIScript Azure OpenAI Configuration](https://microsoft.github.io/genaiscript/configuration/azure-openai/).

The Azure OpenAI models that can be used as **Model Under Test** are the deployments available in your Azure OpenAI service.
