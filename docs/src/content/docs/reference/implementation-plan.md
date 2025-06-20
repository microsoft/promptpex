---
title: Implementation Plan
sidebar:
    order: 30
description: An implementation plan for a coding agent to implement the PromptPex framework in any codebase.
---

Hi there fellow Agent,

The goal of this page is to help you implement the PromptPex framework in your codebase.
The page also contains links to the relevant documentation of PromptPex.
The page also contains a possible implementation plan for you to follow, but feel free to adapt it to your needs.

Your task is to implement the PromptPex framework in your codebase according to the requirement of the user. Follow the instructions of the user to choose which language/framework to use, and how to implement the framework in your codebase.

## Test Generation

PromptPex is a test generate framework for prompts. It is made of a graph of LLM transformations that eventually generate a set of
inputs and expected outputs for a given prompt.

- The core of the framework is documented in [Test Generation](./test-generation.md).

## Reference

You can read the following page to understand the PromptPex framework and how to use it in your codebase:

- [Glossary](./glossary.md): A glossary of terms used in the PromptPex framework.
- [Test Generation](./test-generation.md): The core of the framework, how to generate tests for prompts.
- The prompts are `.prompty` files in the `/src/prompts` directory.
- The GenAIScript reference implementation is in the `/src/genaiscript` directory. PromptPex starts in `src/genaiscript/src/promptpex.mts`.
