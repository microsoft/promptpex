---
title: Workflow
sidebar:
    order: 29
---

The diagram below shows the flow of test generation in PromptPex, starting from the PUT (database shape).

```mermaid
graph TD
    PUT[("Prompt Under Test (PUT)")]
    IS(["Input Specification (IS)"])
    OR(["Output Rules (OR)"])
    IOR(["Inverse Output Rules (IOR)"])
    ORG["Output Rules Groundedness (ORG)"]
    PUTI(["Prompt Under Test Intent (PUTI)"])
    PPT{{"PromptPex Tests (PPT)"}}
    SA["Spec Agreement (SA)"]
    SAE["Spec Agreement Evaluation (SAE)"]
    TO["Test Output (TO) for MUT"]
    TNC["Test Non-Compliance (TNC)"]
    TV["Test Validity (TV)"]
    TGS["Test Generation Scenario (TGS)"]
    BT{{"Baseline Tests (BT)"}}

    PUT ==> IS

    PUT ==> OR
    OR ==> IOR

    OR --> ORG
    PUT --> ORG

    PUT --> PUTI

    PUT --> PPT
    IS ==> PPT
    OR ==> PPT
    IOR ==> PPT

    PPT --> TV
    IS --> TV

    TGS --> PPT

    PPT --> SA
    PUTI --> SA
    OR --> SA

    SA --> SAE
    PUT --> SAE

    PPT -->|"Test Expansion (TE)"| PPT

    PPT --> TO
    PUT --> TO

    TO --> TNC
    PUT --> TNC

    PUT --> BT
    BT --> TNC
```

<br />

- Every node is created by a LLM call (aside from the PUT).
- Rounded nodes can be edited by the user.
- Square nodes are evaluations.
- Diamond nodes are outputs.
- Lines represent data dependencies.
- Bolded lines are the minimum path to generate tests.
