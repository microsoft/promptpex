---
title: Overview
description: How to use PromptPex to evaluate prompts and models with generated tests.
sidebar:
    order: 21.6
---

PromptPex is packaged as a [npm.js](https://www.npmjs.com/package/promptpex) command line tool that uses [GenAIScript](https://microsoft.github.io/genaiscript/).

## Configuration

- Install [Node.js v22+](https://nodejs.org/en/download/) (or later).
- Make sure you have the right version of Node.js:

```sh
node --version
```

- Run PromptPex configuration to set up your `.env` file:

```sh
npx promptpex configure
```

PromptPex supports many LLM providers, such as OpenAI, Azure OpenAI, GitHub Models, Ollama, and more. The configuration will prompt you to select the LLM provider you want to use and set up the necessary environment variables in a `.env` file.

## Running PromptPex

- Run PromptPex on your prompt file(s):

```sh
npx promptpex my_prompt.prompty
```

## Basic examples

We start with simple examples of using PromptPex assume your prompt is in a file called `myprompt.prompty` and you want generate tests, run them, and evaluate the results. More details about all the parameters you can specify can be found in the [CLI parameter documentation](/promptpex/cli/parameters).

### Generate, Run and Evaluate Tests

Suppose you want to generate tests, run them, and evaluate the results using the minimum effort level:

```sh wrap
npx promptpex my_prompt.prompty --effort=min --out=results/ --evals=true --modelsUnderTest="ollama:llama3.3" --evalModel="ollama:llama3.3"
```

### Generate Only Tests

Suppose you only want to generate tests and not run them:

```sh
npx promptpex my_prompt.prompty --effort=min --out=results/  --evals=false
```

### Generate Only Tests with Groundtruth Outputs

Suppose you only want to generate tests and add groundtruth outputs from a specific model and not run them:

```sh
npx promptpex my_prompt.prompty --effort=min --out=results/  --evals=false  --vars groundtruthModel="ollama:llama3.3"
```

### Run and Evaluate Tests from a Context File

Suppose you just ran the above command and the file `results/my_prompt/promptpex_context.json` was created. (See [saving and restoring](/promptpex/cli/saving-restoring)) You can now load this context file to run and evaluate the tests:

```sh
npx promptpex results/my_prompt/promptpex_context.json --evals=true --modelsUnderTest="ollama:llama3.3" --evalModel="ollama:llama3.3"
```

<!--
### Review Test Collection

Suppose you want to see a review of the [collection of tests](/promptpex/reference/test-collections) that were generated from the previous run and filter the tests to the top 10 most important tests base on this analysis:

```sh
promptpex results/my_prompt/promptpex_context.json --evals=false --rateTests=true --filterTestCount=10
```

The test collection review output will be saved in `results/my_prompt/test_collection_review.md`. An example of the [output](/promptpex/examples/test-collection-review) is shown in the documentation. With the `--filterTestCount` parameter, you specify how many of the most important tests you want to include in a filtered output. This is useful for focusing on the most critical tests based on the analysis. The reduced set of tests will be saved in `results/my_prompt/filtered_tests.json`.
-->

## Notes

- For more details on prompt format and advanced usage, see the [overview](/promptpex/reference).
