script({
    system: ["system", "system.files", "system.changelog"],
    temperature: 0
})
def("LLMFrontEnd.py", await workspace.readText("src/LLMFrontEnd.py"));
$`
## Task
Find 1 function that does NOT use 'render_prompt' and calls get_bot_response
refactor the code that generates the messages into a prompty template + call to 'render_prompt'.
Update or create files with results.

## Rules

- do not convert functions that already use 'render_prompt'
- make sure to migrate the prompt text precisely.
- prompty uses markdown with frontmatter and jinja2 templating syntax.
- save prompty files under src/prompts/
`

def("PROMPTY_EXAMPLE", 
`---
description: "prompt description"
sample:
    name: value
    name2: value2
---
system:
<the system prompt jinja2 template>
user:
<the user prompt jinja2 template>
`
, { language: "markdown"}
)
def("PROMPTY_EXAMPLE", await workspace.readText("src/rules_global.prompty"));
