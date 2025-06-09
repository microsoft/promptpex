import { checkConfirm } from "./src/confirm.mts"
import { evalsListEvals, generateEvals } from "./src/evals.mts"
import { diagnostics } from "./src/flags.mts"
import { generateInputSpec } from "./src/inputspecgen.mts"
import { generateIntent } from "./src/intentgen.mts"
import { generateInverseOutputRules } from "./src/inverserulesgen.mts"
import { loadPromptFiles, updateOutput } from "./src/loaders.mts"
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
import { evaluateTestMetrics } from "./src/testevalmetric.mts"
import type {
    PromptPexContext,
    PromptPexOptions,
    PromptPexTest,
    PromptPexTestResult,
} from "./src/types.mts"
import {
    MODEL_ALIAS_EVAL,
    EFFORTS,
    MODEL_ALIAS_STORE,
    PROMPTPEX_CONTEXT,
} from "./src/constants.mts"
import { evalTestCollection } from "./src/testcollectioneval.mts"
import { saveContextState, restoreContextState } from "./src/context.mts"

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
    accept: ".prompty,.md,.txt,.json,.prompt.yml",
    parameters: {
        prompt: {
            type: "string",
            description:
                "Prompt template to analyze. You can either copy the prompty source here or upload a file prompt. [prompty](https://prompty.ai/) is a simple markdown-based format for prompts. prompt.yml is the GitHub Models format.",
            required: false,
            uiType: "textarea",
        },
        effort: {
            type: "string",
            enum: ["min", "low", "medium", "high"],
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
        evals: {
            type: "boolean",
            description: "Evaluate the test results",
            uiGroup: "Evaluation",
            default: false,
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
        rateTests: {
            type: "boolean",
            description:
                "Generate a report rating the quality of the test set.",
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
        evalModel: {
            type: "string",
            description:
                "List of models to use for test evaluation; semi-colon separated",
            uiSuggestions: [
                "openai:gpt-4o",
                "azure:gpt-4o",
                "ollama:gemma3:27b",
                "ollama:llama3.3:70b",
                "lmstudio:llama-3.3-70b",
            ],
            uiGroup: "Evaluation",
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
        groundtruthModel: {
            type: "string",
            description: "Model used to generate groundtruth",
            uiSuggestions: ["openai:gpt-4.1", "azure:gpt-4.1"],
            uiGroup: "Evaluation",
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
            default: 0,
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
        filterTestCount: {
            type: "integer",
            description:
                "Number of tests to include in the filtered output of evalTestCollection.",
            default: 5,
            uiGroup: "Evaluation",
        },
        loadContext: {
            type: "boolean",
            description: "Load contenxt from a file.",
            default: false,
            required: false,
            uiGroup: "Generation",
        },
        loadContextFile: {
            type: "string",
            description:
                "Filename to load PromptPexContext from before running.",
            default: PROMPTPEX_CONTEXT,
            required: false,
            uiGroup: "Generation",
        },
    },
})

const dbg = host.logger("promptpex:main")

const { output, vars } = env
const {
    out,
    cache,
    evalCache,
    evals,
    disableSafety,
    testRunCache,
    inputSpecInstructions,
    outputRulesInstructions,
    inverseOutputRulesInstructions,
    testExpansionInstructions,
    compliance,
    baselineModel,
    rulesModel,
    storeCompletions,
    storeModel,
    groundtruthModel,
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
    rateTests,
    filterTestCount,
    loadContext,
    loadContextFile,
} = vars as PromptPexOptions & {
    effort?: "min" | "low" | "medium" | "high"
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
    .filter(Boolean)
const evalModel: string[] = vars.evalModel?.split(/;/g).filter(Boolean)
const options = {
    cache,
    testRunCache,
    evalCache,
    evals,
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
    storeModel,
    groundtruthModel,
    testsPerRule,
    maxTestsToRun,
    runsPerTest,
    customMetric,
    compliance,
    baselineTests: false,
    modelsUnderTest,
    evalModel,
    splitRules,
    maxRulesPerTestGeneration,
    testGenerations,
    createEvalRuns,
    testSamplesCount,
    testSamplesShuffle,
    testExpansions,
    rateTests,
    filterTestCount,
    loadContext,
    loadContextFile,
    out,
    ...efforts,
} satisfies PromptPexOptions

// I need copy this - I'm not sure why
options.compliance = compliance ?? options.compliance

if (env.files[0] && promptText)
    cancel(
        "You can only provide either a prompt file or prompt text, not both."
    )
if (!env.files[0] && !promptText)
    cancel("No prompt file or prompt text provided.")

initPerf({ output })

// determine the source of the prompt to use
const file0 = env.files[0]
let file: any
if (file0 && file0.filename) {
    const ext = path.extname(file0.filename)
    if (ext === ".prompty") {
        file = file0
    } else if (ext === ".json") {
        // Set loadContext and loadContextFile to the path to env.files[0]
        options.loadContext = true
        options.loadContextFile = path.isAbsolute(file0.filename)
            ? file0.filename
            : path.join(process.cwd(), file0.filename)
    } else {
        file = file0
    }
} else {
    file = { filename: "CLI.prompty", content: promptText }
}

output.itemValue(`prompt file`, file.filename)
output.itemValue(`effort`, effort)
output.detailsFenced(`options`, options, "yaml")

// preliminary checking

if (modelsUnderTest?.length) {
    output.heading(3, `Models Under Test`)
    for (const modelUnderTest of modelsUnderTest) {
        const resolved = await host.resolveLanguageModel(modelUnderTest)
        if (!resolved) throw new Error(`Model ${modelUnderTest} not found`)
        output.item(`${resolved.provider}:${resolved.model}`)
    }
}

if (groundtruthModel?.length) {
    output.heading(3, `Groundtruth Model`)

    const resolved = await host.resolveLanguageModel(groundtruthModel)
    if (!resolved) throw new Error(`Model ${groundtruthModel} not found`)
    output.item(`${resolved.provider}:${resolved.model}`)
}

if (evals)
    if (evalModel?.length) {
        output.heading(2, `Evaluation Models`)
        for (const eModel of evalModel) {
            const resolved = await host.resolveLanguageModel(eModel)
            if (!resolved) throw new Error(`Model ${eModel} not found`)
            output.item(`${resolved.provider}:${resolved.model}`)
        }
    } else {
        cancel("No evaluation model defined.")
    }

// process the prompt file (or read the context file)

let files: PromptPexContext
if (!options.loadContext) files = await loadPromptFiles(file, options)

// use context state if available

if (options.loadContext) {
    output.heading(3, `Loading context from file`)
    const newOut = options.out
    output.appendContent(
        `loading PromptPexContext from ${options.loadContextFile}`
    )
    files = await restoreContextState(options.loadContextFile)
    updateOutput(newOut, files)

    // Save the contents of the prompt file to the out directory with the original prompt file name
    if (
        files.prompt &&
        files.prompt.filename &&
        files.prompt.content &&
        options.out
    ) {
        const promptOutPath = path.join(
            options.out,
            path.basename(files.prompt.filename)
        )
        await workspace.writeText(promptOutPath, files.prompt.content)
        dbg(`Saved prompt file to ${promptOutPath}`)
    }
} else {
    if (diagnostics) {
        output.heading(2, `PromptPex Diagnostics`)
        await generateReports(files)
        if (createEvalRuns) {
            const evals = await evalsListEvals()
            if (!evals.ok) throw new Error("evals configuration not found")
        }
        await checkConfirm("diag")
    }
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
    files.promptPexTests = await generateTests(files, options)

    output.table(
        files.promptPexTests.map(({ scenario, testinput, expectedoutput }) => ({
            scenario,
            testinput,
            expectedoutput,
        }))
    )
    output.detailsFenced(`tests (json)`, files.promptPexTests, "json")
    output.detailsFenced(`test data (json)`, files.testData.content, "json")
    await checkConfirm("test")
}

if (testExpansions > 0) {
    output.heading(3, "Expanded Tests")
    await expandTests(files, files.promptPexTests, options)
    output.table(
        files.promptPexTests.map(({ scenario, testinput, expectedoutput }) => ({
            scenario,
            testinput,
            expectedoutput,
        }))
    )
    await checkConfirm("expansion")
    output.detailsFenced(`tests (json)`, files.promptPexTests, "json")
    output.detailsFenced(`test data (json)`, files.testData.content, "json")
}

// After test expansion, before evals
if (rateTests) {
    output.heading(3, "Test Set Quality Review")
    await evalTestCollection(files, options)
    output.detailsFenced(`test ratings (md)`, files.rateTests, "md")
    output.detailsFenced(`filtered tests (json)`, files.filteredTests, "json")
}
await checkConfirm("rateTests")

if (rateTests && options.filterTestCount > 0) {
    // Parse the JSON content
    output.heading(3, `Running ${options.filterTestCount} Filtered Tests`)
    const filteredTests: PromptPexTest[] = JSON.parse(
        files.filteredTests.content
    )
    await generateEvals(modelsUnderTest, files, filteredTests, options)
} else {
    await generateEvals(modelsUnderTest, files, files.promptPexTests, options)
}
await checkConfirm("evals")

if (createEvalRuns) {
    output.note(`Evals run created, skipping local evals...`)
} else if (evals && !modelsUnderTest?.length && !storeCompletions) {
    output.warn(
        `No modelsUnderTest and storeCompletions is not enabled. Skipping test run.`
    )

    if (options.evalModel?.length && options.loadContext) {
        output.note(`Evaluating saved test results using evalModel.`)
        const results = JSON.parse(files.testOutputs.content)
        // Evaluate metrics for all test results
        for (const testRes of results) {
            const newResult = await evaluateTestMetrics(testRes, files, options)
            testRes.metrics = newResult.metrics
        }
        files.testOutputs.content = JSON.stringify(results, null, 2)

        if (files.writeResults)
            await workspace.writeText(
                files.testOutputs.filename,
                JSON.stringify(results, null, 2)
            )
        output.detailsFenced(`results (json)`, results, "json")
    }
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

    output.itemValue(`evaluation models`, evalModel.join(", "))

    // only run tests if modelsUnderTest is defined
    let groundtruthResults: PromptPexTestResult[] = []
    if (groundtruthModel?.length) {
        output.heading(4, `Groundtruth Test Results`)
        groundtruthResults = await runTests(files, {
            runGroundtruth: true,
            ...options,
        })
    }

    // Copy groundtruth outputs into files.promptPexTests, save to disk
    if (groundtruthResults.length && Array.isArray(files.promptPexTests)) {
        for (let i = 0; i < files.promptPexTests.length; ++i) {
            if (
                groundtruthResults[i] &&
                typeof groundtruthResults[i].output === "string"
            ) {
                files.promptPexTests[i].groundtruth =
                    groundtruthResults[i].output
                files.promptPexTests[i].groundtruthModel = groundtruthModel
                dbg(
                    `Set groundtruth for test ${i} to ${groundtruthResults[i].output}`
                )
                dbg(`test[${i}]:`, files.promptPexTests[i])
            }
        }
        dbg(`saving ${files.promptPexTests.length} tests with groundtruth`)
        const resc = JSON.stringify(files.promptPexTests, null, 2)
        files.tests.content = resc
        if (files.writeResults) await workspace.writeFiles(files.tests)
    }

    // groundtruth,only run tests if modelsUnderTest is defined
    let results = []
    if (modelsUnderTest?.length) {
        output.heading(4, `Test Results`)
        results = await runTests(files, { runGroundtruth: false, ...options })
    }

    // only measure metrics if eval is true
    if (evals) {
        let newResult: PromptPexTestResult
        // Evaluate metrics for all test results
        for (const testRes of results) {
            newResult = await evaluateTestMetrics(testRes, files, options)
            testRes.metrics = newResult.metrics
        }
        files.testOutputs.content = JSON.stringify(results, null, 2)

        if (files.writeResults)
            await workspace.writeText(
                files.testOutputs.filename,
                JSON.stringify(results, null, 2)
            )
        output.detailsFenced(`results (json)`, results, "json")
    }

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
                model,
                scenario,
                input,
                output,
                ...Object.fromEntries(
                    Object.entries(
                        metrics && typeof metrics === "object" ? metrics : {}
                    ).map(([k, v]) => [
                        k,
                        v && typeof v === "object" && "content" in v
                            ? renderEvaluation(v as any)
                            : "",
                    ])
                ),
                compliance: renderEvaluationOutcome(testCompliance),
                rule,
                inverse: inverse ? "🔄" : "",
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

if (files.writeResults) {
    saveContextState(files, path.join(files.dir, PROMPTPEX_CONTEXT))
    output.appendContent(
        `saving PromptPexContext to ${path.join(files.dir, PROMPTPEX_CONTEXT)}`
    )
}

reportPerf()
