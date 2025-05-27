import frontmatterSchema from "./src/frontmatter.json" with { type: "json" }
script({
    title: "Converts an arbitrary prompt file to the .prompty format",
    description:
        "This script will get you started in converting your prompt files to the .prompty format so that you can run promptpex.",
})

const file = env.files[0]
if (!file) cancel("please provide a file")

const readme = def("README", await workspace.readText("README.md"))
const example = def(
    "EXAMPLE",
    await workspace.readText("samples/demo/demo.prompty")
)
const prompt = def("PROMPT", file)
const schema = defSchema("FRONTMATTER_SCHEMA", frontmatterSchema as JSONSchema)

$`You are an expert at using the test generator PromptPex, documented in ${readme}.

## Task

Convert the prompt file ${prompt} provided by the user to the .prompty PromptPex format.

## PromptPex format

PromptPex uses the Prompty format, which is a markdown file with a YAML frontmatter using the ${schema} JSON schema.
An example of the .prompty format is provided in ${example}.

## Requirements

To convert the prompt file to the .prompty format, you need to:
- Convert the prompt file to the .prompty format, following the example provided in ${example}.
- Ensure that the converted file is valid according to the ${schema} JSON schema.
- Provide a brief explanation of the conversion process and any assumptions made.
- Provide the converted file in the .prompty format.
- Ignore the 'intrusctions' field unless completely necessary.

Very important:
- Your task is the make sure the structure of the prompt file is correct; do not change the content of the prompt instructions.
- If you detect prompt instructions in ${prompt}, make sure to copy the instructions verbatim to the .prompty file. DO NOT MODIFY THE WORDING OF PROMPTING INSTRUCTIONS.
- Use the ${schema} JSON schema to validate the frontmatter of the .prompty file.
- As a description file, use "AI generated prompt file, please review".

## Output

- Replace the file extension with ".prompty" and save the converted file.

`
