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

## Azure AI Foundry Portal

- Open [Azure AI Foundry](https://ai.azure.com/) and select your Azure OpenAI resource.
- Navigate to the **Azure OpenAI Evaluation** section.
- You should see the evaluations created by PromptPex listed there.

## Common errors

- Make sure that the **Model Under Tests** are deployment names in your Azure OpenAI service. They are should something like `azure:gpt-4.1-mini`, `azure:gpt-4.1-nano`, or `azure:gpt-4o-mini`.
- Make sure to check the `createEvalRuns` parameter is set to `true` in the web interface or on the command line.
