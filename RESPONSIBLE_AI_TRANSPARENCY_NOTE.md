---
title: Transparency Note
sidebar:
    order: 99
description: PromptPex is a tool designed to assist developers by exploring and testing AI model prompts.
keywords: AI prompts, LLM testing, prompt engineering, AI development, responsible AI
lastUpdated: 2025-02-18
---

# PromptPex: Responsible AI Transparency Note

## What is PromptPex?

PromptPex (https://github.com/microsoft/promptpex) is an AI-driven tool developed to assist software developers in creating, managing, and testing prompts for large language models (LLMs). By treating prompts as functions, PromptPex automates the generation of test inputs and the extraction of functional specifications. It aims to enhance the efficiency and reliability of AI prompts, thereby improving their performance across various AI models.

## What can PromptPex do?

PromptPex provides a suite of functionalities including:

-   Automated rule extraction from natural language prompts.
-   Generation of diverse test cases to validate the performance of those prompts.
-   Support for testing prompts across multiple AI models, ensuring that developers understand how their inputs are interpreted and how outputs are generated.

## What is PromptPex's intended use?

The intended use of PromptPex, as identified through its impact assessment, is to simplify the development of AI prompts by providing structured and automated tools for prompt evaluation and testing. This is aimed at improving the reliability of AI interactions and facilitating better integration of AI capabilities within software applications.

The released version of PromptPex is intended as a research prototype and should be used primarily for research purposes. It is not intended for production use. The goal of the release is to highlight new tools to support the development of AI systems, and to solicit feedback from the community on the tool's capabilities and limitations.

## How was PromptPex evaluated? What metrics are used to measure performance?

PromptPex undergoes rigorous evaluations focused on its ability to generate valid and diverse test cases that accurately reflect the rules defined by the prompts. Effectiveness is measured using metrics such as:

-   Percentage of non-compliant outputs generated during testing.
-   Groundedness of the rules extracted from prompts, which assesses whether the rules are adequately supported by the prompt descriptions.
-   Validity of the test cases generated, ensuring they are relevant and applicable to the prompts being tested.

## What are the limitations of PromptPex? How can users minimize the impact of PromptPex's limitations when using the system?

Limitations include:

-   Dependence on the quality of initial prompt formulations, as vague or poorly defined prompts can lead to suboptimal performance.
-   Variance in rule extraction accuracy, especially with complex or idiomatic language.
    To minimize these impacts, users should focus on crafting clear and precise prompts, thoroughly test against a variety of input scenarios, and continually iterate on prompt designs as needed.

## What operational factors and settings allow for effective and responsible use of PromptPex?

Effective and responsible use of PromptPex requires:

-   Understanding of the underlying AI models that will be used with the prompts.
-   Continuous updates and adaptations to align with advancements in AI technologies.
-   Active engagement with the developer community to share insights and gathered feedback for improvements.

## How do I provide feedback on PromptPex?

We welcome feedback and collaboration from our audience. If you have suggestions, questions, or observe unexpected/offensive behavior in our technology, please contact us at: <jhalleux@microsoft.com>, <reshabh@cs.washington.edu>, <sbarke@microsoft.com>, <zorn@microsoft.com>.

If the team receives reports of undesired behavior or identifies issues independently, we will update this repository with appropriate mitigations.

## Foundation model best practices

We strongly encourage users to use LLMs/MLLMs that support robust Responsible AI mitigations, such as Azure Open AI (AOAI) services. Such services continually update their safety and RAI mitigations with the latest industry standards for responsible use. For more on AOAI’s best practices when employing foundations models for scripts and applications:

-   [Blog post on responsible AI features in AOAI that were presented at Ignite 2023](https://techcommunity.microsoft.com/t5/ai-azure-ai-services-blog/announcing-new-ai-safety-amp-responsible-ai-features-in-azure/ba-p/3983686)

-   [Overview of Responsible AI practices for Azure OpenAI models](https://learn.microsoft.com/en-us/legal/cognitive-services/openai/overview)

-   [Azure OpenAI Transparency Note](https://learn.microsoft.com/en-us/legal/cognitive-services/openai/transparency-note)

-   [OpenAI’s Usage policies](https://openai.com/policies/usage-policies)

-   [Azure OpenAI’s Code of Conduct](https://learn.microsoft.com/en-us/legal/cognitive-services/openai/code-of-conduct) "

## What kinds of issues may arise when using PromptPex?

Issues may arise from:

-   Inaccurate rule extraction, potentially leading to incorrect tests being generated.
-   Developers misapplying test cases without fully understanding their prompts' nuances.
-   Unexpected results due to testing models that were not part of the initial PromptPex testing suite.
    To mitigate these issues, it is crucial to thoroughly educate users on the prompt crafting process and the importance of contextual understanding. Please see the related technical paper for more details.

## Learn more about PromptPex

For more information, visit the PromptPex project page on GitHub.
Read the [PromptPex technical paper](http://arxiv.org/abs/2503.05070) for more details.
