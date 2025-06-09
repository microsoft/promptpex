---
title: GitHub Action
---

This repository is a custom dockerized action that can be used in a GitHub Action
workflow.

## Inputs

- `github_token`: GitHub token with `models: read` permission at least. (required)
- `debug`: Enable debug logging.

## Outputs

- `text`: The generated text output.
- `data`: The generated JSON data output, parsed and stringified.

## Usage

Add the following to your step in your workflow file:

```yaml
uses: microsoft/promptpex@main
with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
```

## Example

```yaml
name: My action
on:
    push:
permissions:
    contents: read
    # issues: write
    # pull-requests: write
    models: read
concurrency:
    group: ${{ github.workflow }}-${{ github.ref }}
    cancel-in-progress: true
jobs:
    run-script:
        runs-on: ubuntu-latest
        steps:
            - uses: actions/checkout@v4
            - uses: microsoft/promptpex@main
              with:
                  github_token: ${{ secrets.GITHUB_TOKEN }}
```
