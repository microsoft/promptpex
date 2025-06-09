---
title: Command Line
description: How to use PromptPex to evaluate prompts and models with generated tests.
sidebar:
    order: 21.6
---

## Basic examples

We start with simple examples of using PromptPex assume your prompt is in a file called `myprompt.prompty` and you want generate tests, run them, and evaluate the results.  More details about all the parameters you can specify can be found in the [CLI parameter documentation](/promptpex/reference/parameters).

### Generate, Run and Evaluate Tests

Suppose you want to generate tests, run them, and evaluate the results using the minimum effort level:

```sh wrap
promptpex myprompt.prompty --effort=min --out=results/ --evals=true --modelsUnderTest="ollama:llama3.3" --evalModel="ollama:llama3.3"
```

### Generate Only Tests

Suppose you only want to generate tests and not run them:

```sh
promptpex myprompt.prompty --effort=min --out=results/  --evals=false 
```

### Generate Only Tests with Groundtruth Outputs

Suppose you only want to generate tests and add groundtruth outputs from a specific model and not run them:

```sh
promptpex myprompt.prompty --effort=min --out=results/  --evals=false  --vars groundtruthModel="ollama:llama3.3"
```

### Run and Evaluate Tests from a Context File

Suppose you just ran the above command and the file `results/myprompt/promptpex_context.json` was created. (See [saving and restoring](/promptpex/reference/saving-restoring)) You can now load this context file to run and evaluate the tests:

```sh
promptpex results/myprompt/promptpex_context.json --evals=true --modelsUnderTest="ollama:llama3.3" --evalModel="ollama:llama3.3"
```


### Review Test Collection

Suppose you want to see a review of the [collection of tests](/promptpex/reference/test-collections) that were generated from the previous run and filter the tests to the top 10 most important tests base on this analysis:

```sh
promptpex results/myprompt/promptpex_context.json --evals=false --rateTests=true --filterTestCount=10
```

The test collection review output will be saved in `results/myprompt/test_collection_review.md`.  An example of the [output](/promptpex/reference/example-test-collection-review) is shown in the documentation.  With the `--filterTestCount` parameter, you specify how many of the most important tests you want to include in a filtered output. This is useful for focusing on the most critical tests based on the analysis.  The reduced set of tests will be saved in `results/myprompt/filtered_tests.json`.


## Notes

- For more details on prompt format and advanced usage, see the [overview](/promptpex/reference).

