---
title: Test Samples
sidebar:
    order: 25
---

It is possible to define test samples in the `testSamples` section of the YAML file. This section allows you to specify a list of test cases and expected output.
The test samples are used in the test generation process to generate tests that mimic actual user input.

```mermaid
graph TD
    PUT["Prompt Under Test (PUT)"]
    IS["Input Specification (IS)"]
    OR["Output Rules (OR)"]
    IOR["Inverse Output Rules (IOR)"]
    PPT["PromptPex Tests (PPT)"]
    TS[["Test Samples (TS)"]]
    TE["Test Expansion (TE)"]


    PUT --> IS
    TS ==> IS

    PUT --> OR
    OR --> IOR

    OR --> TE
    IOR --> TE
    TS ==> TE

    PUT --> PPT
    IS --> PPT
    TE --> PPT
    TS ==> PPT
```

## Configuration

You can specify `testSamples` in the prompt frontmatter as an array of objects.

```yaml wrap
---
testSamples:
    - locale: "en-us"
      joke: "Why did the scarecrow win an award? Because he was outstanding in his field."
      output: "funny"
    - locale: "fr-FR"
      joke: "Pourquoi les plongeurs plongent-ils toujours en arrière et jamais en avant? Parce que sinon ils tombent dans le bateau."
      output: "funny"
---
```

## Parameters

When invoking PromptPex, you can also provide filters to limit the number of test samples used
in the generation:

- `testSamplesCount`: The number of test samples to use in the generation. This is useful to limit the amount of test samples used in the generation.
- `testSamplesShuffle`: Whether to shuffle the test samples before using them in the generation. This is useful to ensure that the test samples are not used in the same order every time.
