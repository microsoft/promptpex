---
title: GitHub Models Evals
sidebar:
    order: 28.5
---

[GitHub Models](https://github.com/marketplace/models) is a service that allows to run inference through your GitHub 
subscription. Recently, GitHub Models added support for running evals.

## .prompt.yml support

PromptPex supports the GitHub Models `.prompt.yml` prompt format.

```sh
promptex summarizer.prompt.yml
```

## Install the runner

- install the [GitHub CLI](https://cli.github.com/) (already installed in the GitHub Codespace)

- install the [GitHub Models extension](https://github.com/github/gh-models)

```bash wrap
gh extension install https://github.com/github/gh-models
```

## Generated eval file

For each model under test, PromptPex will generate a `.prompt.yml` file that contains the model under test, the test data and the metrics.
This file can be executed through the `gh models eval` command.

```bash
gh models eval <modelname>.prompt.yml
```
