---
title: Overview
description: How to use PromptPex to evaluate prompts and models with generated tests.
sidebar:
    order: 21.6
---

PromptPex is packaged as a [npm.js](https://www.npmjs.com/package/promptpex) command line tool that uses [GenAIScript](https://microsoft.github.io/genaiscript/).

## Local configuration

To use PromptPex locally, you need to have Node.js installed and set up your environment. Follow these steps:

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

- Run PromptPex on your prompt file(s):

```sh
npx promptpex my_prompt.prompty
```

PromptPex also supports the following file formats:

- `.md`, `.txt`, tread as a Jinja2 templated string (Markdown)
- `.prompty`, Prompty file format (default)
- `.prompt.yml`, GitHub Models format

## Docker configuration

If you prefer to run PromptPex in a Docker container, you can use the following command. This assumes you have [Docker](https://www.docker.com/) installed and running on your machine.

- Run the configuration command to set up your `.env` file.

```sh wrap
docker run -e GITHUB_TOKEN="$GITHUB_TOKEN" --rm -it -v "$PWD":/app -w /app node:lts-alpine npx --yes promptpex configure
```

- Run PromptPex on your prompt file(s) using Docker:

```sh wrap
docker run -e GITHUB_TOKEN="$GITHUB_TOKEN" --rm -it -v "$PWD":/app -w /app node:lts-alpine npx --yes promptpex my_prompt.prompty
```

You might need to pass more environment variables depending on your shell configuration.

## Effort levels

PromptPex supports different effort levels for test generation, which can be specified using the `--vars effort` flag. The available effort levels are:

- `min`: Minimal effort, generates a small number of simple tests.
- `low`: Low effort, generates a moderate number of tests with some complexity.
- `medium`: Medium effort, generates a larger number of more complex tests.
- `high`: High effort, generates the maximum number of tests with the highest complexity.

```sh "effort=min" wrap
npx promptpex my_prompt.prompty --vars effort=min
```

## Basic examples

We start with simple examples of using PromptPex assume your prompt is in a file called `my_prompt.prompty` and you want generate tests, run them, and evaluate the results. More details about all the parameters you can specify can be found in the [CLI parameter documentation](/promptpex/cli/parameters).

### Generate, Run and Evaluate Tests

Suppose you want to generate tests, run them, and evaluate the results using the minimum effort level:

```sh wrap
npx promptpex my_prompt.prompty --vars effort=min out=results evals=true modelsUnderTest="ollama:llama3.3" evalModel="ollama:llama3.3"
```

### Generate Only Tests

Suppose you only want to generate tests and not run them:

```sh
npx promptpex my_prompt.prompty --vars effort=min out=results evals=false
```

### Generate Only Tests with Groundtruth Outputs

Suppose you only want to generate tests and add groundtruth outputs from a specific model and not run them:

```sh
npx promptpex my_prompt.prompty --vars effort=min out=results evals=false "groundtruthModel=ollama:llama3.3"
```

### Run and Evaluate Tests from a Context File

Suppose you just ran the above command and the file `results/my_prompt/promptpex_context.json` was created. (See [saving and restoring](/promptpex/cli/saving-restoring)) You can now load this context file to run and evaluate the tests:

```sh
npx promptpex results/my_prompt/promptpex_context.json --vars evals=true "modelsUnderTest=ollama:llama3.3" "evalModel=ollama:llama3.3"
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
