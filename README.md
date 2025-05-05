# PromptPex

> Test Generation for Prompts0

- [Read the documentation](https://microsoft.github.io/promptpex/)

**Prompts** are an important part of any software project that incorporates
the power of AI models. As a result, tools to help developers create and maintain
effective prompts are increasingly important.

- [Prompts Are Programs - ACM Blog Post](https://blog.sigplan.org/2024/10/22/prompts-are-programs/)

**PromptPex** is a tool for exploring and testing AI model prompts. PromptPex is
intended to be used by developers who have prompts as part of their code base.
PromptPex treats a prompt as a function and automatically generates test inputs
to the function to support unit testing.

- [PromptPex technical paper](http://arxiv.org/abs/2503.05070)

<https://github.com/user-attachments/assets/c9198380-3e8d-4a71-91e0-24d6b7018949>

PromptPex provides the following capabilities:

- It will **automatically extract output rules** that are expressed in natural language in the
  prompt. An example of a rule might be "The output should be formatted as JSON".
- From the rules, it will **generate unit test cases** specifically
  designed to determine if the prompt, for a given model, correctly
  follows the rule.
- Given a set of rules and tests, PromptPex will **evaluate the performance of the prompt on any given model**. For example,
  a user can determine if a set of unit tests succeeds on gpt-4o-mini
  but fails on phi3.
- PromptPex uses an LLM to automatically determine whether model outputs meet the specified requirements.
- Automatically export the generated tests and rule-based evaluations to the OpenAI Evals API.

## Intended Uses

PromptPex is shared for research purposes only. It is not meant to be used in practice. PromptPex was not extensively tested for its capabilities and properties, including its accuracy and reliability in practical use cases, security and privacy.

## Responsible AI Transparency Note

Please reference [RESPONSIBLE_AI_TRANSPARENCY_NOTE.md](./RESPONSIBLE_AI_TRANSPARENCY_NOTE.md) for more information.

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit <https://cla.opensource.microsoft.com>.

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
