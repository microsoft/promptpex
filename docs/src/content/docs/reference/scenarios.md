---
title: Scenarios
sidebar:
    order: 25
---

PromptPex supports specify a set of additional input constraints (scenario)
to generate specific test suites. A canonical example would be
localization testing: `generate English, generate French`.

```mermaid
graph TD
    PUT(["Prompt Under Test (PUT)"])
    IS["Input Specification (IS)"]
    OR["Output Rules (OR)"]
    IOR["Inverse Output Rules (IOR)"]
    PPT["PromptPex Tests (PPT)"]
    TO["Test Output (TO) for MUT"]
    TGS[["Test Generation Scenario (TGS)"]]

    PUT --> IS

    PUT --> OR
    OR --> IOR

    PUT --> PPT
    IS --> PPT
    OR --> PPT
    IOR --> PPT

    PPT -->|"Test Expansion (TE)"| PPT

    TGS ==> PPT

    PPT --> TO
    PUT --> TO
```

## Configuration

The test generation scenarios are configured in the prompt front-matter. You can decide to fill in any of the 
template variables in each scenario.

```yaml wrap
scenarios:
    - name: English
      instructions: The user speaks and writes in English.
    - name: French
      instructions: The user speaks and writes in French.
      parameters:
          locale: fr-FR
```
