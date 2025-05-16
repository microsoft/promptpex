import { checkConfirm } from "./src/confirm.mts"
import { generateEvals } from "./src/evals.mts"
import { diagnostics } from "./src/flags.mts"
import { generateInputSpec } from "./src/inputspecgen.mts"
import { generateIntent } from "./src/intentgen.mts"
import { generateInverseOutputRules } from "./src/inverserulesgen.mts"
import { loadPromptFiles } from "./src/loaders.mts"
import { outputFile, outputLines } from "./src/output.mts"
import { metricName } from "./src/parsers.mts"
import { initPerf, reportPerf } from "./src/perf.mts"
import { expandTests } from "./src/testexpand.mts"
import {
    computeOverview,
    generateReports,
    renderEvaluation,
    renderEvaluationOutcome,
} from "./src/reports.mts"
import { generateOutputRules } from "./src/rulesgen.mts"
import { generateTests } from "./src/testgen.mts"
import { runTests } from "./src/testrun.mts"
import type { PromptPexOptions } from "./src/types.mts"
import { EFFORTS, MODEL_ALIAS_STORE } from "./src/constants.mts"

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
{{some_input}}
 \`\`\`

- The content of the Markdown is the chat conversation. 
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
                "Prompt template to analyze. You can either copy the prompty source here or upload a file prompt. [prompty](https://prompty.ai/) is a simple markdown-based format for prompts.",
            required: false,
            uiType: "textarea",
        },
        effort: {
            type: "string",
            enum: ["low", "medium", "high"],
            required: false,
            description:
                "Effort level for the test generation. This will influence the number of tests generated and the complexity of the tests.",
        },
        out: {
            type: "string",
            description:
                "Output folder for the generated files. This flag is mostly used when running promptpex from the CLI.",
            uiGroup: "Cache",
        },
        cache: {
            type: "boolean",
            description:
                "Cache all LLM calls. This accelerates experimentation but you may miss issues due to LLM flakiness.",
            uiGroup: "Cache",
        },
        testRunCache: {
            type: "boolean",
            description: "Cache test run results in files.",
            uiGroup: "Cache",
        },
        evalCache: {
            type: "boolean",
            description: "Cache eval evaluation results in files.",
            uiGroup: "Cache",
        },
        testsPerRule: {
            type: "integer",
            description:
                "Number of tests to generate per rule. By default, we generate 3 tests to cover each output rule. You can modify this parameter to control the number of tests generated.",
            minimum: 1,
            maximum: 10,
            default: 3,
            uiGroup: "Generation",
        },
        splitRules: {
            type: "boolean",
            description:
                "Split rules and inverse rules in separate prompts for test generation.",
            default: true,
            uiGroup: "Generation",
        },
        maxRulesPerTestGeneration: {
            type: "integer",
            description:
                "Maximum number of rules to use per test generation which influences the complexity of the generated tests. Increase this value to generate tests faster but potentially less complex tests.",
            default: 3,
            uiGroup: "Generation",
        },
        testGenerations: {
            type: "integer",
            description:
                "Number of times to amplify the test generation. This parameter allows to generate more tests for the same rules by repeatedly running the test generation process, while asking the LLM to avoid regenerating existing tests.",
            default: 2,
            minimum: 1,
            maximum: 10,
            uiGroup: "Generation",
        },
        runsPerTest: {
            type: "integer",
            description:
                "Number of runs to execute per test. During the evaluation phase, this parameter allows to run the same test multiple times to check for consistency and reliability of the model's output.",
            minimum: 1,
            maximum: 100,
            default: 2,
            uiGroup: "Evaluation",
        },
        disableSafety: {
            type: "boolean",
            description:
                "Do not include safety system prompts and do not run safety content service. By default, system safety prompts are included in the prompt and the content is checked for safety. This option disables both.",
            default: false,
        },
        rulesModel: {
            type: "string",
            description:
                "Model used to generate rules (you can also override the model alias 'rules')",
            uiSuggestions: [
                "openai:gpt-4o",
                "azure:gpt-4o",
                "ollama:gemma3:27b",
                "ollama:llama3.3:70b",
                "lmstudio:llama-3.3-70b",
            ],
            uiGroup: "Generation",
        },
        evalModel: {
            type: "string",
            description:
                "Model used to evaluate rules (you can also override the model alias 'eval')",
            uiSuggestions: [
                "openai:gpt-4o",
                "azure:gpt-4o",
                "ollama:gemma3:27b",
                "ollama:llama3.3:70b",
                "lmstudio:llama-3.3-70b",
            ],
            uiGroup: "Evaluation",
        },
        baselineModel: {
            type: "string",
            description: "Model used to generate baseline tests",
            uiSuggestions: ["openai:gpt-4o", "azure:gpt-4o"],
            uiGroup: "Evaluation",
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
            uiGroup: "Evaluation",
        },
        maxTestsToRun: {
            type: "number",
            description: "Maximum number of tests to run",
            required: false,
            uiGroup: "Evaluation",
        },
        inputSpecInstructions: {
            type: "string",
            title: "Input Specification instructions",
            description:
                "These instructions will be added to the input specification generation prompt.",
            uiGroup: "Instructions",
        },
        outputRulesInstructions: {
            type: "string",
            title: "Output Rules instructions",
            description:
                "These instructions will be added to the output rules generation prompt.",
            uiGroup: "Instructions",
        },
        inverseOutputRulesInstructions: {
            type: "string",
            title: "Inverse Output Rules instructions",
            description:
                "These instructions will be added to the inverse output rules generation prompt.",
            uiGroup: "Instructions",
        },
        testExpansionInstructions: {
            type: "string",
            title: "Test Expansion instructions",
            description:
                "These instructions will be added to the test expansion generation prompt.",
            uiGroup: "Instructions",
        },
        storeCompletions: {
            type: "boolean",
            title: "Stored Completion",
            description:
                "Store chat completions using [stored completions](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/stored-completions).",
            uiGroup: "Azure OpenAI Evals",
        },
        storeModel: {
            type: "string",
            description:
                "Model used to create [stored completions](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/stored-completions) (you can also override the model alias 'store'). ",
            uiSuggestions: ["openai:gpt-4.1", "azure:gpt-4.1"],
            uiGroup: "Azure OpenAI Evals",
        },
        customMetric: {
            type: "string",
            title: "Custom Test Evaluation Template",
            required: false,
            uiType: "textarea",
            uiGroup: "Evaluation",
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
You will be given a evaluation criteria <CRITERIA>, a LLM prompt <PROMPT>, output rules for the prompt <RULES>, a user input <INPUT>, and <OUTPUT> from the model. 
Your task is to evaluate the <CRITERIA> based on <PROMPT>, <INPUT>, and <OUTPUT> provided.

<CRITERIA>
The <OUTPUT> generated by the model complies with the <RULES> and the <PROMPT> provided.
</CRITERIA>

<PROMPT>
{{prompt}}
</PROMPT>

<RULES>
{{rules}}
</RULES>

## Output

**Binary Decision on Evaluation**: You are required to make a binary decision based on your evaluation:
- Return 'OK' if <OUTPUT> is compliant with <CRITERIA>.
- Return 'ERR' if <OUTPUT> is **not** compliant with <CRITERIA> or if you are unable to confidently answer.

user:
<INPUT>
{{input}}
</INPUT>

<OUTPUT>
{{output}}
</OUTPUT>
\`\`\`

</details>       
            `,
        },
        createEvalRuns: {
            type: "boolean",
            description:
                "Create an Evals run in [OpenAI Evals](https://platform.openai.com/docs/guides/evals). Requires OpenAI API key in environment variable `OPENAI_API_KEY`.",
            uiGroup: "Azure OpenAI Evals",
        },
        testExpansions: {
            type: "integer",
            description:
                "Number of test expansion phase to generate tests. This will increase the complexity of the generated tests.",
            minimum: 0,
            default: 1,
            maximum: 5,
            uiGroup: "Generation",
        },
        testSamplesCount: {
            type: "integer",
            description:
                "Number of test samples to include for the rules and test generation. If a test sample is provided, the samples will be injected in prompts to few-shot train the model.",
            uiGroup: "Generation",
        },
        testSamplesShuffle: {
            type: "boolean",
            description:
                "Shuffle the test samples before generating tests for the prompt.",
            uiGroup: "Generation",
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
    testExpansionInstructions,
    compliance,
    baselineModel,
    rulesModel,
    evalModel,
    storeCompletions,
    storeModel,
    maxTestsToRun,
    prompt: promptText,
    testsPerRule,
    customMetric,
    runsPerTest,
    splitRules,
    maxRulesPerTestGeneration,
    testGenerations,
    createEvalRuns,
    testSamplesCount,
    testSamplesShuffle,
    testExpansions,
    effort,
} = vars as PromptPexOptions & {
    effort?: "low" | "medium" | "high"
    customMetric?: string
    prompt?: string
    inputSpecInstructions?: string
    outputRulesInstructions?: string
    inverseOutputRulesInstructions?: string
    testExpansionInstructions?: string
}
const efforts = EFFORTS[effort || ""] || {}
if (effort && !efforts) throw new Error(`unknown effort level ${effort}`)
const modelsUnderTest: string[] = (vars.modelsUnderTest || "")
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
        testExpansion: testExpansionInstructions,
    },
    workflowDiagram: !process.env.DEBUG,
    baselineModel,
    rulesModel,
    storeCompletions,
    evalModel,
    storeModel,
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
    createEvalRuns,
    testSamplesCount,
    testSamplesShuffle,
    testExpansions,
    out,
    ...efforts,
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

if (diagnostics) {
    await generateReports(files)
    await checkConfirm("diag")
}

output.itemValue(`effort`, effort)
output.detailsFenced(`options`, options, "yaml")

// prompt info
output.heading(3, `Prompt Under Test`)
output.itemValue(`filename`, files.prompt.filename)
output.fence(files.prompt.content, "md")

if (files.testSamples?.length) {
    output.startDetails("test samples")
    output.table(files.testSamples)
    output.endDetails()
}

// generate intent
output.heading(3, "Intent")
await generateIntent(files, options)
outputFile(files.intent)
await checkConfirm("intent")

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

if (testExpansions > 0) {
    output.heading(3, "Expanded Tests")
    await expandTests(files, tests, options)
    output.table(
        tests.map(({ scenario, testinput, expectedoutput }) => ({
            scenario,
            testinput,
            expectedoutput,
        }))
    )
    await checkConfirm("expansion")
    output.detailsFenced(`tests (json)`, tests, "json")
    output.detailsFenced(`test data (json)`, files.testData.content, "json")
}

await generateEvals(modelsUnderTest, files, tests, options)
await checkConfirm("evals")

if (createEvalRuns) {
    output.note(`Evals run created, skipping local evals...`)
} else if (!modelsUnderTest?.length && !storeCompletions) {
    output.warn(
        `No modelsUnderTest and storeCompletions is not enabled. Skipping test run.`
    )
} else {
    // run tests against the model(s)
    output.heading(3, `Test Runs with Models Under Test`)
    if (storeCompletions)
        output.itemValue(
            `stored completion model`,
            (await host.resolveLanguageModel(storeModel || MODEL_ALIAS_STORE))
                ?.model || "store"
        )
    output.itemValue(`models under test`, modelsUnderTest.join(", "))

    output.heading(4, `Metrics`)
    for (const metric of files.metrics)
        output.detailsFenced(metricName(metric), metric.content, "markdown")

    output.heading(4, `Test Results`)
    const results = await runTests(files, options)
    output.detailsFenced(`results (json)`, results, "json")

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
                metrics,
            }) => ({
                rule,
                model,
                scenario,
                inverse: inverse ? "🔄" : "",
                input,
                output,
                compliance: renderEvaluationOutcome(testCompliance),
                ...Object.fromEntries(
                    Object.entries(metrics).map(([k, v]) => [
                        k,
                        renderEvaluation(v),
                    ])
                ),
            })
        )
    )
}

output.heading(3, `Results Overview`)
const { overview } = await computeOverview(files, { percent: true })
output.table(overview)
if (files.writeResults)
    await workspace.writeText(
        path.join(files.dir, "overview.csv"),
        CSV.stringify(overview, { header: true })
    )

output.appendContent("\n\n---\n\n")

reportPerf()
