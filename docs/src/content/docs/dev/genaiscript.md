---
title: GenAIScript
sidebar:
    order: 31
---

[GenAIScript](https://microsoft.github.io/genaiscript) is a tool for generating and executing scripts using LLMs. It is used in PromptPex to generate the test generation scripts.

## Try PromptPex

- Install [Node.js v20+](https://nodejs.org/)
- Configure your LLM credentials in `.env`. You can use OpenAI, Azure OpenAI, or Ollama.

```sh
npx --yes genaiscript configure
```

- Launch promptpex remotely

```sh
npx --yes genaiscript@latest serve --remote microsoft/promptpex --remote-branch dev
```

## GitHub Codespaces

Use CodeSpaces / dev container to get a fully configured environment, including access to LLMs through GitHub Marketplace Models.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=microsoft/promptpex)

## Local development

- Clone this repository
- Install [Node.js v20+](https://nodejs.org/)
- Install dependencies

```sh
npm install
```

### Dockerized

Clone this repository and run the following command to run genaiscript in a docker container:

```sh
docker run --name genaiscript --rm -it --expose 8003 -p 8003:8003 -v ${PWD}:/workspace -w /workspace node:20-alpine npx --yes genaiscript@latest serve --network
```

## Configure the eval, rules, baseline aliases

PromptPex defines the following model aliases for the different phases of the test generation:

- `rules`: rule, inverse rules, test generation
- `eval`: rule and test quality evaluations
- `baseline`: baseline test generation

If you are using a specific set of models, you can use a `.env` file to override the eval/rules/baseline aliases

```text
GENAISCRIPT_MODEL_EVAL="azure:gpt-4o_2024-11-20"
GENAISCRIPT_MODEL_RULES="azure:gpt-4o_2024-11-20"
GENAISCRIPT_MODEL_BASELINE="azure:gpt-4o_2024-11-20"
```

## Web interface

- Launch web interface

```sh
npm run serve
```

- Open localhost

## Development

The development of PromptPex is done using [GenAIScript](https://microsoft.github.io/genaiscript).

- Install [Node.js v20+](https://nodejs.org/)
- Configure your LLM credentials in `.env`

## Typecheck scripts

Use Visual Studio Code to get builtin typechecking from TypeScript or

```sh
npm run build
```

## Create a commit

For convenience,

```sh
npm run gcm
```

## Debug

- Open a `JavaScript Debug Terminal` in Visual Studio Code
- Put a breakpoint in your script
- Launch the script

## Upgrade dependencies

```sh
npm run upgrade
```

## Diagnostics mode

Set the `DEBUG=promptpex:*` environment variable to enable additional logging.

```sh
DEBUG=promptpex:* npm run ...
```

To pipe the stderr, stdout to a file,

```sh
DEBUG=* npm run ... > output.txt 2>&1
```

## Caching

Add `--vars cache=true` to the command line to enable caching of LLM calls.
