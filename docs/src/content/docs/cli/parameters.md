---
title: Parameters
description: Documentation of all parameters available to the PromptPex CLI and script interface.
sidebar:
    order: 27
---
This page documents all parameters available to the PromptPex CLI and script interface. Each parameter can be provided as a CLI flag (e.g., `--param value`) or via environment/configuration files. Default values and accepted types are indicated where applicable.

The first argument can be a Prompty file containing the prompt or a JSON file containing a saved PromptPex context, which will include all the tests, test runs, etc. saved in a previous invocation of PromptPex. If no argument is provided, the `--prompt` parameter must be specified.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--prompt` | string |         | Prompt template to analyze. Provide inline or via file. Supports [prompty](https://prompty.ai/) markdown format. |
| `--effort` | string |         | Effort level for test generation. One of: `min`, `low`, `medium`, `high`. Influences test count and complexity. |
| `--out` | string |         | Output folder for generated files. |
| `--cache` | boolean |         | Cache all LLM calls for faster experimentation. |
| `--testRunCache` | boolean |         | Cache test run results in files. |
| `--evalCache` | boolean |         | Cache evaluation results in files. |
| `--evals` | boolean | false   | Evaluate the test results. |
| `--testsPerRule` | integer | 3       | Number of tests to generate per rule (1-10). |
| `--splitRules` | boolean | true    | Split rules and inverse rules in separate prompts for test generation. |
| `--maxRulesPerTestGeneration` | integer | 3 | Max rules per test generation (affects test complexity). |
| `--testGenerations` | integer | 2       | Number of times to amplify test generation (1-10). |
| `--runsPerTest` | integer | 2       | Number of runs per test during evaluation (1-100). |
| `--disableSafety` | boolean | false   | Disable safety system prompts and content safety checks. |
| `--rateTests` | boolean | false   | Generate a report rating the quality of the test set. |
| `--rulesModel` | string |         | Model used to generate rules (can override 'rules' alias). |
| `--baselineModel` | string |         | Model used to generate baseline tests. |
| `--modelsUnderTest` | string |         | Semicolon-separated list of models to run the prompt against. |
| `--evalModel` | string |         | Semicolon-separated list of models to use for test evaluation. |
| `--compliance` | boolean | false   | Evaluate test result compliance. |
| `--maxTestsToRun` | number  |         | Maximum number of tests to run. |
| `--inputSpecInstructions` | string |         | Additional instructions for input specification generation. |
| `--outputRulesInstructions` | string |         | Additional instructions for output rules generation. |
| `--inverseOutputRulesInstructions` | string |         | Additional instructions for inverse output rules generation. |
| `--testExpansionInstructions` | string |         | Additional instructions for test expansion generation. |
| `--storeCompletions` | boolean |         | Store chat completions using Azure OpenAI stored completions. |
| `--storeModel` | string |         | Model used to create stored completions (can override 'store' alias). |
| `--groundtruthModel` | string |         | Model used to generate groundtruth outputs. |
| `--customMetric` | string |         | Custom test evaluation template (as a prompt). |
| `--createEvalRuns` | boolean |         | Create an Evals run in OpenAI Evals (requires `OPENAI_API_KEY`). |
| `--testExpansions` | integer | 0       | Number of test expansion phases (0-5). |
| `--testSamplesCount` | integer |         | Number of test samples to include for rules/test generation. |
| `--testSamplesShuffle` | boolean |         | Shuffle test samples before generating tests. |
| `--filterTestCount` | integer | 5       | Number of tests to include in filtered output of evalTestCollection. |
| `--loadContext` | boolean | false   | Load context from a file. |
| `--loadContextFile` | string | promptPex_context.json | Filename to load PromptPexContext from before running. |

## Usage Example

```sh
promptpex {file.prompty|file.json>} --prompt myprompt.prompty --effort=medium --out=results/ --evals=true --modelsUnderTest="openai:gpt-4o;ollama:llama3.3:70b" --evalModel="openai:gpt-4o" --rateTests=true
```

## Notes

- For more details on prompt format and advanced usage, see the main documentation.
