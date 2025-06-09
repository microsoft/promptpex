---
title: GitHub Models
sidebar:
    order: 28.5
---

[GitHub Models](https://github.com/marketplace/models) is a service that allows to run inference through your GitHub 
subscription. Recently, GitHub Models added support for running evals.

## Install the runner

- install the [GitHub CLI](https://cli.github.com/) (already installed in the GitHub Codespace)

- install the [GitHub Models extension](https://github.com/github/gh-models)

```bash
gh extension install https://github.com/github/gh-models
```

## Generated eval file

For each model under test, PromptPex will generate a `.prompt.yml` file that contains the test data and the metrics.
This file can be executed through the `gh models eval` command.

## Running generate prompt files

