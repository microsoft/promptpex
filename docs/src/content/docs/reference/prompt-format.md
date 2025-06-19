---
title: Prompt Format
sidebar:
    order: 29.05
---

PromptPex supports markdown-based prompt format based on [Prompty](https://www.prompty.ai/); these are just markdown with a bit of syntax to
represent messages and the input/output signature of the prompt.

The `demo` prompt below defines a set of parameters (`inputs` as a set of JSON schema types).
The `system`/`user` messages are separate by `system:`, `user:` markers in the markdown body.
It uses the Jinja2 template engine to insert values (`{{joke}}`).
The `scenarios` array is used to expand the test generation with further input specification and optional input values.

```md wrap
---
name: A demo
inputs:
    joke: "how do you make a tissue dance? You put a little boogie in it."
    locale: "en-us"
---

system:
You are an assistant
and you need to categorize a joke as funny or not.
The input local is {{locale}}.

user:
{{joke}}
```

## Messages

You can represent entire chat conversations in the prompt using the `system`, `user` and `assistant` messages.

```md wrap "user:" "system:" "assistant:"
---
name: A travel assistant
input:
    answer: "Next week."
---
system:
You are a travel assistant.

user:
I want to go to Paris.

assistant:
Where do you want to go in Paris?

user:
{{answer}}
```

## Frontmatter 

The frontmatter is a YAML block at the beginning of the markdown file. It contains metadata about the prompt, such as the name, inputs, and other properties. It starts and ends with `---` lines.

PromptPex supports most of the [Prompty frontmatter](https://www.prompty.ai/docs/prompt-frontmatter) properties with a few additions.

```yaml
---
name: A demo
inputs:
    # shortcut syntax: provide a value
    joke: "how do you make a tissue dance? You put a little boogie in it."
    # JSON schema syntax
    locale:
        type: string
        description: The locale of the joke.
        default: "en-us"
outputs:
    # JSON schema for expected output format
    sentiment:
        type: string
        description: The sentiment of the joke
        enum: ["funny", "not_funny"]
    confidence:
        type: number
        description: Confidence score between 0 and 1
---
```

### Output Specification

PromptPex supports output specifications using JSON schema in the `outputs` field. When specified, the LLM will be automatically prompted to format its response according to the schema.

```yaml
outputs:
    word_count:
        type: integer
        description: Number of words in the text
    first_word:
        type: string
        description: The first word in the text
    categories:
        type: array
        description: List of categories
        items:
            type: string
```

The output specification supports standard JSON schema types including:
- `string` - Text values
- `number` / `integer` - Numeric values  
- `boolean` - True/false values
- `array` - Lists of items
- `object` - Complex nested structures

When an `outputs` field is present, PromptPex automatically adds instructions to the LLM requesting JSON output that conforms to the specified schema.

### Schema

The JSON schema of the prompt front matter is available at [https://microsoft.github.io/promptpex/schemas/prompt.json](https://microsoft.github.io/promptpex/schemas/prompt.json).

The TypeScript types are available at [https://github.com/microsoft/promptpex/blob/dev/src/genaisrc/src/types.mts](https://github.com/microsoft/promptpex/blob/dev/src/genaisrc/src/types.mts).

## Converting your prompt

The [promptpex-importer](https://github.com/microsoft/promptpex/blob/dev/src/genaisrc/prompty-importer.genai.mts) script is a tool that uses an LLM to convert your prompt to the prompty format.

Follow the [GenAIScript](/promptpex/dev/genaiscript) instructions to launch the web server
and the run `promptpex-importer` command to convert your prompt.

