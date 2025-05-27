---
title: Overview
sidebar:
    order: 30
---

This section provides documentation for developers who want to use PromptPex in their own projects or infrastructure.

## Bring Your Own Inference Library

PromptPex is workflow of LLM prompts that implement the test generation process.
The template are stored in a [markdown-ish, framework agnostic, template format](/promptpex/reference/prompt-format/).

- [prompts directory](https://github.com/microsoft/promptpex/tree/main/src/prompts)

**PromptPex is designed to be used with any LLM library.** The only requirement is that the library must be able to execute the Prompty templates.

## GenAIScript

[GenAIScript](/promptpex/dev/genaiscript/) implementation of the test generation process using the prompt templates.

## Python

A [Python](/promptpex/dev/python/) implementation of the test generation process using the prompt templates.
