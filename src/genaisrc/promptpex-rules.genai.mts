script({
    title: "PromptPex Rules Generator",
    description: "Generate a rules file for a prompt template. Runs this script against a prompt authored in markdown or prompty format.",
    files: ["samples/speech-tag.prompty"],
    system: [],
    parameters: {
        allow: {
            type: "string",
            description: "Additional instructions for allowed rules.",
        },
        deny: {
            type: "string",
            description: "Additional instructions for denied rules.",
        },
        numRules: {
            type: "number",
            description: "Number of rules to generate.",
            default: 3
        }
    }
})

const { deny, allow, numRules } = env.vars
const promptFile = env.files.find(({filename}) => /\.(md|prompty)$/i.test(filename))
const dir = path.dirname(promptFile.filename)
const basename = path.basename(promptFile.filename)
const rulesPath = path.join(dir, basename + ".rules.md")
const instructions = await workspace.readText(path.join(dir, basename + ".instructions.md"))

importTemplate("src/prompts/generic_rules_global.prompty", {
    allow, deny, numRules, instructions: instructions?.content || "", inputData: promptFile.content
})

$`Save generated rules to file ${rulesPath} using FILE syntax.`
