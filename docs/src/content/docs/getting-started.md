---
title: Getting Started
sidebar:
    order: 1
---

PromptPex is a test generation tool for LLM prompts. It uses a workflow of prompts
to generate test cases. These prompts can be orchestrated by **any LLM library**.

In this section, we will show you how to try out PromptPex using your LLM credentials.

## Try PromptPex

- Install [Node.js v20+](https://nodejs.org/)
- Configure your LLM credentials in `.env`. You can use OpenAI, Azure OpenAI, or Ollama.

```sh
npx --yes genaiscript configure
```

- Launch promptpex remotely

```sh
npx --yes genaiscript serve --remote microsoft/promptpex
```
