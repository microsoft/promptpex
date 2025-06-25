# Implementation Plan

Hi there fellow Agent,

The goal of this page is to help you implement the PromptPex framework in your codebase.
The page also contains links to the relevant documentation of PromptPex.
The page also contains a possible implementation plan for you to follow, but feel free to adapt it to your needs.

Your task is to implement the PromptPex framework in your codebase according to the requirement of the user. Follow the instructions of the user to choose which language/framework to use, and how to implement the framework in your codebase.

## IMPORTANT

When implementing PromptPex, it is very important to reuse the existing prompts as is. Do not change the prompts unless you need to adapt the syntax for your template engine.

We strongly recommend keep the prompts in separate files and load them
at runtime, rather than hardcoding them in your codebase.

Whenever possible, use the original `.prompty` files from the `src/prompts` directory.

## Phase 1: Test Generation

PromptPex is a test generate framework for prompts. It is made of a graph of LLM transformations that eventually generate a set of
inputs and expected outputs for a given prompt.

- The core of the framework is documented in [Test Generation](docs/src/content/docs/reference/test-generation.md).

## Phase: Validate Test Generation

Once you have implemented the test generation, you should validate it on a prompt.

- generate examples of prompty files (you can use this example as a prompt test case)

```markdown
---
tags:
    - unlisted
---

system:
You need to categorize a joke as funny or not.
Respond with "funny" or "not funny".

user:
{{joke}}
```

- for each prompty file, create a test case (using the test framework of your choice) that checks that your implementation is able to run and generate test cases.

- run the tests cases and fix the code until all tests pass.

## Phase 3: Additional features

You will find additional features for promptpex generation that can be useful to add once the basic test generation is working.

- [Groundtruth](docs/src/content/docs/reference/groundtruth.md): how to generate groundtruth for prompts.
- [Test Samples](docs/src/content/docs/reference/test-samples.md): how to integrate existing test samples into the test generation process.
- [Test Expansion](docs/src/content/docs/reference/test-expansion.md): how to morph tests into more complex longer texts.
- [Scenarios](docs/src/content/docs/reference/scenarios.md): how to receive custom set of inputs instructions from the users and use it to guide the generation of tests.

### Notes

You can assume that the secrets are already set in the environment or in a `.env` file
that can be loaded using a library.

## Reference

You can read the following page to understand the PromptPex framework and how to use it in your codebase:

- [Glossary](docs/src/content/docs/reference/glossary.md): A glossary of terms used in the PromptPex framework.
- [Test Generation](docs/src/content/docs/reference/test-generation.md): The core of the framework, how to generate tests for prompts.
- The prompts are `.prompty` files in the [prompts directory](src/prompts).
- The **.prompty** format is documented in [Prompt Format](docs/src/content/docs/reference/prompt-format.md).

## Reference implementation

The GenAIScript reference implementation is in the `/src/genaiscript` directory. PromptPex starts in `src/genaiscript/src/promptpex.mts`.

It is implemented using [GenAIScript](https://microsoft.github.io/genaiscript/).

**Following the patterns and habits of the the target framework/language you are generating**.
The reference implementation is a good starting point but you should adapt it to the target framework/language you are generating.
