---
title Test Samples
sidebar:
    order: 25
---

It is possible to define test samples in the `testSamples` section of the YAML file. This section allows you to specify a list of test cases and expected output. 
The test samples are used in the test generation process to generate tests that mimic actual user input.


```yaml
testSamples:
    - locale: "en-us"
      joke: "Why did the scarecrow win an award? Because he was outstanding in his field."
      output: "funny"
    - locale: "fr-FR"
      joke: "Pourquoi les plongeurs plongent-ils toujours en arrière et jamais en avant? Parce que sinon ils tombent dans le bateau."
      output: "funny"
```