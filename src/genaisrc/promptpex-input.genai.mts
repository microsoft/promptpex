script({
    title: "PromptPex Input Spec Generator",
    description: "Generate an input spec for a prompt template. Runs this script against a prompt authored in markdown or prompty format.",
    files: ["samples/speech-tag.prompty"]
})

const promptFile = env.files.find(({filename}) => /\.(md|prompty)$/i.test(filename))
const inputSpecFilename = path.join(path.dirname(promptFile.filename), path.basename(promptFile.filename) + ".inputspec.md")
const inputSpecFile = await workspace.readText(inputSpecFilename)

importTemplate("src/prompts/input_spec.prompty", { context: promptFile.content, input_spec: inputSpecFile?.content || "" })

$`Save LLM response to file ${inputSpecFilename} using FILE syntax.`

defFileOutput(inputSpecFilename, "Generated input spec")