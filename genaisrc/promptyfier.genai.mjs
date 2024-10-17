const promptys = await workspace.findFiles("src/prompts/*.prompty", { readText: true })
def("FILE", promptys.slice(0, 2))
def("MESSAGES", "messages.txt")

$`Your are an expert prompt engineer using the Prompty file format

## Task

Analyze the .prompty files in FILE and update the frontmatter with improvements.

- you can find examples of .prompty file, generated messages pairs in the MESSAGES file.
- DO NOT MODIFY THE PROMPT SECTION
`

$`## Prompty file format

The .prompty file are markdown files with a frontmatter section that contains the metadata of the prompt. 

- The frontmatter is a YAML section that uses the PROMPTY_SCHEMA JSON schema.
- The body contains the prompt text in markdown format using the jinja2 templating language.
- The body is system, user, assistant sections.
`
def("PROMPTY_EXAMPLE",
`---
name: ExamplePrompt
description: A prompt that uses context to ground an incoming question
sample:
  firstName: Seth
  context: >
    The Alpine Explorer Tent boasts a detachable divider for privacy, 
    numerous mesh windows and adjustable vents for ventilation, and 
    a waterproof design. It even has a built-in gear loft for storing 
    your outdoor essentials. In short, it's a blend of privacy, comfort, 
    and convenience, making it your second home in the heart of nature!
  question: What can you tell me about your tents?

---
system:
You are an AI assistant who helps people find information. As the assistant, 
you answer questions briefly, succinctly, and in a personable manner using 
markdown and even add some personal flair with appropriate emojis.
# Customer

You are helping {{firstName}} to find answers to their questions.
Use their name to address them in your responses.
# Context

Use the following context to provide a more personalized response to {{firstName}}:
{{context}}
user:
{{question}}
`    , { language: "markdown"}
)

def("PROMPTY_SCHEMA", (await fetchText("https://raw.githubusercontent.com/microsoft/prompty/refs/heads/main/Prompty.yaml")).text)
