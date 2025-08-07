---
title: GitHub Models Evals
sidebar:
    order: 28.5
---

[GitHub Models](https://github.com/marketplace/models) is a service that allows to run inference through your GitHub
subscription. PromptPex was integrated as the [generate](https://github.com/github/gh-models/tree/main/cmd/generate) command.

## gh models generate

PromptPex is integrated in the [models extension](https://github.com/github/gh-models) for the GitHub CLI.

```sh
gh models generate summarizer.prompt.yml
```

## Install the runner

- install the [GitHub CLI](https://cli.github.com/) (already installed in the GitHub Codespace)

- install the [GitHub Models extension](https://github.com/github/gh-models)

```bash wrap
gh extension install https://github.com/github/gh-models
```
