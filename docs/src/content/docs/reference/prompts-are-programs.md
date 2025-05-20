---
title: Prompts are Programs
sidebar:
    order: 20.1
---

**Prompts** are an important part of any software project that incorporates
the power of AI models. As a result, tools to help developers create and maintain
effective prompts are increasingly important.

- [Prompts Are Programs - ACM Blog Post](https://blog.sigplan.org/2024/10/22/prompts-are-programs/)

**PromptPex** is a tool for exploring and testing AI model prompts. PromptPex is
intended to be used by developers who have prompts as part of their code base.
PromptPex treats a prompt as a function and automatically generates test inputs
to the function to support unit testing.

- [PromptPex technical paper](http://arxiv.org/abs/2503.05070)

## Part of Speech Tagging Example

Let's look at a prompt that is designed to identify the [part of speech of a word in a sentence](https://github.com/microsoft/promptpex/blob/dev/samples/speech-tag/speech-tag.prompty).

```text wrap
In this task, you will be presented with two items: 1) a sentence and 2) a word contained in that sentence. You have to determine the part of speech for a given word and return just the tag for the word's part of speech. ​

Return only the part of speech tag. If the word cannot be tagged with the listed tags, return Unknown. If you are unable to tag the word, return CantAnswer.
...list of tags...
```

When the user enters 

```text wrap
"The brown fox was lazy", lazy`
``` 

the LLM responds 

```text wrap
JJ
```

If we look closely at the prompt, we can observe the following sections.

- define **inputs**. 

```text wrap ins="two items: 1) a sentence and 2) a word contained in that sentence"
In this task, you will be presented with two items: 1) a sentence and 2) a word contained in that sentence. You have to determine the part of speech for a given word and return just the tag for the word's part of speech. ​

Return only the part of speech tag. If the word cannot be tagged with the listed tags, return Unknown. If you are unable to tag the word, return CantAnswer.
```

- **compute** an intermediate result

```text wrap ins="determine the part of speech"
In this task, you will be presented with two items: 1) a sentence and 2) a word contained in that sentence. You have to determine the part of speech for a given word and return just the tag for the word's part of speech. ​

Return only the part of speech tag. If the word cannot be tagged with the listed tags, return Unknown. If you are unable to tag the word, return CantAnswer.
```

- return an **output**

```text wrap ins="return just the tag for the word's part of speech."
In this task, you will be presented with two items: 1) a sentence and 2) a word contained in that sentence. You have to determine the part of speech for a given word and return just the tag for the word's part of speech. ​

Return only the part of speech tag. If the word cannot be tagged with the listed tags, return Unknown. If you are unable to tag the word, return CantAnswer.
```

- **structure**, assertions

```text wrap ins="If the word cannot be tagged with the listed tags, return Unknown."
In this task, you will be presented with two items: 1) a sentence and 2) a word contained in that sentence. You have to determine the part of speech for a given word and return just the tag for the word's part of speech. ​

Return only the part of speech tag. If the word cannot be tagged with the listed tags, return Unknown. If you are unable to tag the word, return CantAnswer.
```

- **constraints**

```text wrap ins="Return only the part of speech tag."
In this task, you will be presented with two items: 1) a sentence and 2) a word contained in that sentence. You have to determine the part of speech for a given word and return just the tag for the word's part of speech. ​

Return only the part of speech tag. If the word cannot be tagged with the listed tags, return Unknown. If you are unable to tag the word, return CantAnswer.
```
