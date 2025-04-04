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
  some_imput:
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
        customTestEvalTemplate: {
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
    input:
        type: string
        description: The input to be used with the prompt.
    output:
        type: string
        description: The output from the model execution.
---
system:

You are a chatbot that helps users evaluate the performance of a model. 
You will be given a prompt, an input, and the output from the model. 
Your task is to evaluate the output based on the prompt and input provided.

**Update this message with your own instructions to the model**

<PROMPT>
{{ prompt }}
</PROMPT>

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
        customTestEvalModel: {
            type: "string",
            description:
                "Model used to evaluate custom test results (you can also override the model alias 'usereval')",
            uiSuggestions: [
                "openai:gpt-4o",
                "ollama:gemma3:27b",
                "ollama:llama3.3:70b",
                "lmstudio:llama-3.3-70b",
            ],
        },
    },
})

const { output, meta, vars } = env
const {
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
    customTestEvalTemplate,
    customTestEvalModel,
    runsPerTest,
    splitRules,
    maxRulesPerTestGeneration,
    testGenerations,
} = vars as PromptPexOptions & {
    prompt?: string
    inputSpecInstructions?: string
    outputRulesInstructions?: string
    inverseOutputRulesInstructions?: string
}
const modelsUnderTest = (vars.modelsUnderTest || "")
    .split(/;/g)
    .filter((m) => !!m)
const options: PromptPexOptions = {
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
    customTestEvalTemplate,
    customTestEvalModel,
    compliance,
    baselineTests: false,
    modelsUnderTest,
    splitRules,
    maxRulesPerTestGeneration,
    testGenerations,
}

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

output.itemValue(`model`, meta.model)
output.detailsFenced(`options`, options, "yaml")

// prompt info
output.heading(3, `Prompt Under Test`)
output.itemValue(`filename`, files.prompt.filename)
output.fence(files.prompt.content, "md")

// generate input spec
output.heading(3, "Input Specification")
files.inputSpec.content = await generateInputSpec(files, options)
outputFile(files.inputSpec)

// generate rules
output.heading(3, "Output Rules")
files.rules.content = await generateOutputRules(files, options)
outputLines(files.rules, "rule")

// generate inverse rules
output.heading(3, "Inverse Output Rules")
files.inverseRules.content = await generateInverseOutputRules(files, options)
outputLines(files.inverseRules, "generate inverse output rule")

// generate tests
output.heading(3, "Tests")
files.tests.content = await generateTests(files, options)
const tests = parseRulesTests(files.tests.content).map(
    ({ scenario, testinput, expectedoutput }) => ({
        scenario,
        testinput,
        expectedoutput,
    })
)
output.table(tests)
output.detailsFenced(`tests (json)`, tests, "json")
output.detailsFenced(`generated`, files.tests.content)

if (!modelsUnderTest?.length) {
    output.warn(`No modelsUnderTest specified. Skipping test run.`)
} else {
    // run tests against the model(s)
    output.heading(3, `Test with Models Under Test`)
    output.itemValue(`models under test`, modelsUnderTest.join(", "))
    files.testOutputs.content = await runTests(files, options)
    const results = parseTestResults(files)
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
