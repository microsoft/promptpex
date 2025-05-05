---
title: Overview
sidebar:
    order: 30
---

This section provides documentation for developers who want to use PromptPex in their own projects or infrastructure.

## Bring Your Own Inference Library

PromptPex is workflow of LLM prompts that implement the test generation process.
The template are stored in a [markdown-ish, framework agnostic, template format](/promptpex/reference/prompt-format/).

- [prompts directory](https://github.com/microsoft/promptpex/tree/main/src/prompts)

**PromptPex is designed to be used with any LLM library.** The only requirement is that the library must be able to execute the Prompty templates.

## GenAIScript

[GenAIScript](/promptpex/dev/genaiscript/) implementation of the test generation process using the prompt templates.

## Python

A [Python](/promptpex/dev/python/) implementation of the test generation process using the prompt templates.

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft
trademarks or logos is subject to and must follow
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
