script({ system: ["system", "system.fs_read_file", "system.files", "system.changelog"]})
def("MESSAGES", { filename: "messages.txt" })

$`Your are an expert prompt engineer using the Prompty file format

## Task

The MESSAGES file contains a list of .prompty file and correspoding generated messages pairs.

For each .prompty file referenced in MESSAGES:
  - update the .prompty file template with the provided sample data

## Guidance

Follow these rules when updating the .prompty files:

- DO NOT MODIFY THE PROMPT SECTION
- only update the frontmatter
- ignore model, tags, version fields
- update the name field with a more descriptive name, if needed
- update the description field with a more descriptive text, if needed
- extract and update sample section if missing
- ignore files that do not need updates
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
