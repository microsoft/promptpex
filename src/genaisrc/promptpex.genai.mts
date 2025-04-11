import { checkConfirm } from "./src/confirm.mts"
import { diagnostics } from "./src/flags.mts"
import { generateInputSpec } from "./src/inputspecgen.mts"
import { generateInverseOutputRules } from "./src/inverserulesgen.mts"
import { loadPromptFiles } from "./src/loaders.mts"
import { outputFile, outputLines } from "./src/output.mts"
import { parseRulesTests, parseTestResults } from "./src/parsers.mts"
import { initPerf, reportPerf } from "./src/perf.mts"
import { computeOverview, generateReports } from "./src/reports.mts"
import { generateOutputRules } from "./src/rulesgen.mts"
import { generateTests } from "./src/testgen.mts"
import { runTests } from "./src/testrun.mts"
import type { PromptPexOptions } from "./src/types.mts"

script({
    title: "PromptPex Test Generator",
    description: `Generate tests for a LLM prompt using PromptPex.

<details><summary>Prompt format</summary>

PromptPex accepts prompts formatted in Markdown with a YAML frontmatter section (optional).

\`\`\`text
---
...
inputs:
  some_input:
    type: "string"
---
system:
This is your system prompt.

user:
This is your user prompt.
{{ some_input }}
 \`\`\`

- The content of the markdoown is the chat conversation. 
\`system:\` is the system prompt and \`user:\` is the user prompt.
- The input variables are defined in the frontmatter of the prompt.
- If not input variables are defined, PromptPex will append the generated test to the user prompt.

### Frontmatter

You can override parts of the test generation
process by providing values in the frontmatter of the prompt (all values are optional).

\`\`\`markdown
---
...
promptPex:
  inputSpec: "input constraints"
  outputRules: "output constraints"
  inverseOutputRules: "inverted output constraints"
  intent: "intent of the prompt"
  instructions:
    inputSpec: "Additional input specification instructions"
    outputRules: "Additional output rules instructions"
    inverseOutputRules: "Additional inverse output rules instructions"
    intent: "Additional intent of the prompt"
---
\`\`\`

</details>
`,
    accept: ".prompty,.md,.txt",
    parameters: {
        prompt: {
            type: "string",
            description:
                "Prompt template to analyze. You can either copy the source here or upload a file prompt.",
            required: false,
            uiType: "textarea",
        },
        out: {
            type: "string",
            description: "Output folder for the generated files",
        },
        cache: {
            type: "boolean",
            description: "Cache all LLM calls",
        },
        testRunCache: {
            type: "boolean",
            description: "Cache test run results",
        },
        evalCache: {
            type: "boolean",
            description: "Cache eval evaluation results",
        },
        testsPerRule: {
            type: "integer",
            description: "Number of tests to generate per rule",
            minimum: 1,
            maximum: 10,
            default: 3,
        },
        splitRules: {
            type: "boolean",
            description:
                "Split rules and inverse rules in separate prompts for generation",
            default: true,
        },
        maxRulesPerTestGeneration: {
            type: "integer",
            description: "Maximum number of rules to use per test generation",
            default: 3,
        },
        testGenerations: {
            type: "integer",
            description: "Number of times to amplify the test generation",
            default: 2,
            minimum: 1,
            maximum: 10,
        },
        runsPerTest: {
            type: "integer",
            description: "Number of runs to execute per test",
            minimum: 1,
            maximum: 100,
            default: 2,
        },
        disableSafety: {
            type: "boolean",
            description:
                "Do not include safety system prompts and do not run safety content service",
            default: false,
        },
        rulesModel: {
            type: "string",
            description:
                "Model used to generate rules (you can also override the model alias 'rules'",
            uiSuggestions: [
                "openai:gpt-4o",
                "ollama:gemma3:27b",
                "ollama:llama3.3:70b",
                "lmstudio:llama-3.3-70b",
            ],
        },
        evalModel: {
            type: "string",
            description:
                "Model used to evaluate rules (you can also override the model alias 'eval')",
            uiSuggestions: [
                "openai:gpt-4o",
                "ollama:gemma3:27b",
                "ollama:llama3.3:70b",
                "lmstudio:llama-3.3-70b",
            ],
        },
        baselineModel: {
            type: "string",
            description: "Model used to generate baseline tests",
            uiSuggestions: ["openai:gpt-4o"],
        },
        modelsUnderTest: {
            type: "string",
            description:
                "List of models to run the prompt again; semi-colon separated",
        },
        compliance: {
            type: "boolean",
            description: "Evaluate Test Result compliance",
            default: false,
            uiType: "runOption",
        },
        maxTestsToRun: {
            type: "number",
            description: "Maximum number of tests to run",
            required: false,
        },
        inputSpecInstructions: {
            type: "string",
            title: "Input Specification instructions",
            description:
                "These instructions will be added to the input specification generation prompt.",
        },
        outputRulesInstructions: {
            type: "string",
            title: "Output Rules instructions",
            description:
                "These instructions will be added to the output rules generation prompt.",
        },
        inverseOutputRulesInstructions: {
            type: "string",
            title: "Inverse Output Rules instructions",
            description:
                "These instructions will be added to the inverse output rules generation prompt.",
        },
        customMetric: {
            type: "string",
            title: "Custom Test Evaluation Template",
            required: false,
            uiType: "textarea",
            description: `This prompt will be used to evaluate the test results.
<details><summary>Template</summary>

\`\`\`text
---
name: Custom Test Result Evaluation
description: |
  A template for a custom evaluation of the results.
tags:
    - unlisted
inputs:
    prompt:
        type: string
        description: The prompt to be evaluated.
    intent:
        type: string
        description: The extracted intent of the prompt.
    inputSpec:
        type: string
        description: The input specification for the prompt.
    rules:
        type: string
        description: The rules to be applied for the test generation.
    input:
        type: string
        description: The input to be used with the prompt.
    output:
        type: string
        description: The output from the model execution.
---
system:

## Task

You are a chatbot that helps users evaluate the performance of a model. 
You will be given a evluation criteria <CRITERIA>, a LLM prompt <PROMPT>, output rules for the prompt <RULES>, a user input <INPUT>, and <OUTPUT> from the model. 
Your task is to evaluate the <CRITERIA> based on <PROMPT>, <INPUT>, and <OUTPUT> provided.

<CRITERIA>
The <OUTPUT> generated by the model complies with the <RULES> and the <PROMPT> provided.
</CRITERIA>

<PROMPT>
{{ prompt }}
</PROMPT>

<RULES>
{{ rules }}
</RULES>

## Output

**Binary Decision on Evaluation**: You are required to make a binary decision based on your evaluation:
- Return 'OK' if <OUTPUT> is compliant with <CRITERIA>.
- Return 'ERR' if <OUTPUT> is **not** compliant with <CRITERIA> or if you are unable to confidently answer.

user:
<INPUT>
{{ input }}
</INPUT>

<OUTPUT>
{{ output }}
</OUTPUT>
\`\`\`

</details>       
            `,
        },
    },
})

const { output, vars } = env
const {
    out,
    cache,
    evalCache,
    disableSafety,
    testRunCache,
    inputSpecInstructions,
    outputRulesInstructions,
    inverseOutputRulesInstructions,
    compliance,
    baselineModel,
    rulesModel,
    evalModel,
    maxTestsToRun,
    prompt: promptText,
    testsPerRule,
    customMetric,
    runsPerTest,
    splitRules,
    maxRulesPerTestGeneration,
    testGenerations,
} = vars as PromptPexOptions & {
    customMetric?: string
    prompt?: string
    inputSpecInstructions?: string
    outputRulesInstructions?: string
    inverseOutputRulesInstructions?: string
}
const modelsUnderTest = (vars.modelsUnderTest || "")
    .split(/;/g)
    .filter((m) => !!m)
const options = {
    cache,
    testRunCache,
    evalCache,
    disableSafety,
    instructions: {
        inputSpec: inputSpecInstructions,
        outputRules: outputRulesInstructions,
        inverseOutputRules: inverseOutputRulesInstructions,
    },
    workflowDiagram: !process.env.DEBUG,
    baselineModel,
    rulesModel,
    evalModel,
    testsPerRule,
    maxTestsToRun,
    runsPerTest,
    customMetric,
    compliance,
    baselineTests: false,
    modelsUnderTest,
    splitRules,
    maxRulesPerTestGeneration,
    testGenerations,
    out,
} satisfies PromptPexOptions

if (env.files[0] && promptText)
    cancel(
        "You can only provide either a prompt file or prompt text, not both."
    )
if (!env.files[0] && !promptText)
    cancel("No prompt file or prompt text provided.")

initPerf({ output })
const file = env.files[0] || { filename: "", content: promptText }
const files = await loadPromptFiles(file, options)

if (diagnostics) await generateReports(files)

output.detailsFenced(`options`, options, "yaml")

// prompt info
output.heading(3, `Prompt Under Test`)
output.itemValue(`filename`, files.prompt.filename)
output.fence(files.prompt.content, "md")

// generate input spec
output.heading(3, "Input Specification")
await generateInputSpec(files, options)
outputFile(files.inputSpec)
await checkConfirm("inputspec")

// generate rules
output.heading(3, "Output Rules")
await generateOutputRules(files, options)
outputLines(files.rules, "rule")
await checkConfirm("rule")

// generate inverse rules
output.heading(3, "Inverse Output Rules")
await generateInverseOutputRules(files, options)
outputLines(files.inverseRules, "generate inverse output rule")
await checkConfirm("inverse")

// generate tests
output.heading(3, "Tests")
const tests = await generateTests(files, options)

output.table(
    tests.map(({ scenario, testinput, expectedoutput }) => ({
        scenario,
        testinput,
        expectedoutput,
    }))
)
output.detailsFenced(`tests (json)`, tests, "json")
output.detailsFenced(`test data (json)`, files.testData.content, "json")
await checkConfirm("test")

if (!modelsUnderTest?.length) {
    output.warn(`No modelsUnderTest specified. Skipping test run.`)
} else {
    // run tests against the model(s)
    output.heading(3, `Test with Models Under Test`)
    output.itemValue(`models under test`, modelsUnderTest.join(", "))
    const results = await runTests(files, options)

    output.startDetails(`results (table)`)
    output.table(
        results.map(
            ({
                scenario,
                rule,
                inverse,
                model,
                input,
                output,
                compliance: testCompliance,
            }) => ({
                rule,
                model,
                scenario,
                input,
                output,
                compliance: compliance
                    ? testCompliance === "ok"
                        ? "✓"
                        : testCompliance === "err"
                          ? "✗"
                          : "?"
                    : undefined,
                inverse: inverse ? "✓" : "",
            })
        )
    )
    output.endDetails()
    output.detailsFenced(`results`, results, "csv")
}

const { overview } = await computeOverview(files, { percent: true })
output.table(overview)

reportPerf()
