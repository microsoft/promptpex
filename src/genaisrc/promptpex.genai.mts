import { initPerf } from "./src/perf.mts"
import type { PromptPexCliOptions, PromptPexOptions } from "./src/types.mts"
import {
    EFFORTS,
    MODEL_ALIAS_EVAL,
    MODEL_ALIAS_GROUNDTRUTH,
    MODEL_ALIAS_GROUNDTRUTH_EVAL,
    MODEL_ALIAS_MODELS_UNDER_TEST,
} from "./src/constants.mts"
import { promptpexGenerate } from "./src/promptpex.mts"
import { loadPromptContexts } from "./src/loaders.mts"
import { deleteFalsyValues } from "./src/cleaners.mts"
import { parseStrings } from "./src/parsers.mts"

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
    modelAliases: {
        rules: "large",
        eval: "large",
        baseline: "large",
        groundtruth: "large",
        groundtruth_eval: "large",
        model_under_test_small: "small",
        model_under_test_tiny: "tiny",
    },
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
            default: true,
        },
        testRunCache: {
            type: "boolean",
            description: "Cache test run results in files.",
            uiGroup: "Cache",
            default: true,
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
            default: true,
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
        evalModelGroundtruth: {
            type: "string",
            description:
                "List of models to use for ground truth evaluation; semi-colon separated",
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
        groundtruth: {
            type: "boolean",
            description:
                "Generate groundtruth for the tests. This will generate a groundtruth output for each test run.",
            default: true,
            uiGroup: "Groundtruth",
        },
        groundtruthModel: {
            type: "string",
            description: "Model used to generate groundtruth",
            uiSuggestions: ["openai:gpt-4.1", "azure:gpt-4.1"],
            uiGroup: "Groundtruth",
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
            uiGroup: "Evaluation",
        },
    },
})

const dbg = host.logger("promptpex:main")
const { output, vars, files } = env

initPerf({})

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
    groundtruth,
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
} = vars as PromptPexCliOptions

const workflowDiagram = false
const efforts = EFFORTS[effort || ""] || EFFORTS["low"]
if (effort && !efforts) throw new Error(`unknown effort level ${effort}`)
const modelsUnderTest: string[] = parseStrings(vars.modelsUnderTest)
if (!modelsUnderTest.length)
    modelsUnderTest.push(...MODEL_ALIAS_MODELS_UNDER_TEST)
dbg(`modelsUnderTest: %o`, modelsUnderTest)
const evalModels: string[] = parseStrings(vars.evalModel)
if (!evalModels.length) evalModels.push(MODEL_ALIAS_EVAL)
dbg(`evalModels: %o`, evalModels)
const evalModelsGroundtruth: string[] = parseStrings(vars.evalModelGroundtruth)
if (!evalModelsGroundtruth.length)
    evalModelsGroundtruth.push(MODEL_ALIAS_GROUNDTRUTH_EVAL)
dbg(`evalModelsGroundTruth: %o`, evalModelsGroundtruth)
const groundtruthModel = vars.groundtruthModel || MODEL_ALIAS_GROUNDTRUTH
dbg(`groundtruthModel: %s`, groundtruthModel)

if (groundtruth && evalModelsGroundtruth.includes(groundtruthModel))
    output.note(
        `Groundtruth model is the same as groundtruth eval model: ${groundtruthModel}`
    )
if (groundtruth && evalModelsGroundtruth.some((m) => evalModels.includes(m)))
    output.note(
        `Some eval models and groundtruth models are the same: ${evalModelsGroundtruth.filter((m) => evalModels.includes(m)).join(", ")}`
    )

const options: PromptPexOptions = Object.freeze(
    deleteFalsyValues({
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
        workflowDiagram,
        baselineModel,
        rulesModel,
        storeCompletions,
        storeModel,
        groundtruth,
        groundtruthModel,
        testsPerRule,
        maxTestsToRun,
        runsPerTest,
        customMetric,
        compliance,
        baselineTests: false,
        modelsUnderTest,
        evalModels,
        evalModelsGroundtruth,
        splitRules,
        maxRulesPerTestGeneration,
        testGenerations,
        createEvalRuns,
        testSamplesCount,
        testSamplesShuffle,
        testExpansions,
        rateTests,
        filterTestCount,
        out,
        ...efforts,
    } satisfies PromptPexOptions)
)

const promptFiles: WorkspaceFile[] = []
if (promptText)
    promptFiles.push({ filename: "input.prompty", content: promptText })
for (const file of files) promptFiles.push(file)
const runs = await loadPromptContexts(promptFiles, options)
if (!runs.length) {
    if (files.length)
        console.error(
            `No prompts found in the input files. Please provide a valid prompt file.`
        )
    console.log(
        `PromptPex - Test Generation For Prompts
USAGE:
    promptpex <prompt-file> [options]

OPTIONS:
    --vars prompt=TEXT                     Prompt template to analyze. You can either copy the prompty source here or upload a file prompt.
    --vars effort=[min|low|medium|high]    Effort level for the test generation. This will influence the number of tests generated and the complexity of the tests.
    --vars out=DIR                         Output folder for the generated files. This flag is mostly used when running promptpex from the CLI.
    --vars cache=true                           Cache all LLM calls. This accelerates experimentation but you may miss issues due to LLM flakiness.
    --vars testRunCache=true                     Cache test run results in files.
    --vars evals=true                           Evaluate the test results (default: false)
    --vars evalCache=true                       Cache eval evaluation results in files.
    --vars evalModel=MODELS                    List of models to use for test evaluation; semi-colon separated
    --vars testsPerRule=INT                    Number of tests to generate per rule. By default, we generate 3 tests to cover each output rule. (default: 3)
    --vars splitRules=true                      Split rules and inverse rules in separate prompts for test generation. (default: true)
    --vars maxRulesPerTestGeneration=INT       Maximum number of rules to use per test generation. (default: 3)
    --vars testGenerations=INT                 Number of times to amplify the test generation. (default: 2)
    --vars runsPerTest=INT                     Number of runs to execute per test. (default: 2)
    --vars disableSafety=true                   Do not include safety system prompts and do not run safety content service. (default: false)
    --vars rateTests=true                       Generate a report rating the quality of the test set. (default: false)
    --vars rulesModel=MODEL                          Model used to generate rules (e.g. openai:gpt-4o, azure:gpt-4o)
    --vars baselineModel=MODEL                       Model used to generate baseline tests
    --vars modelsUnderTest=MODELS                    List of models to run the prompt again; semi-colon separated
    --vars compliance=true                                Evaluate Test Result compliance (default: false)
    --vars maxTestsToRun=INT                         Maximum number of tests to run
    --vars inputSpecInstructions=TEXT                Instructions added to the input specification generation prompt
    --vars outputRulesInstructions=TEXT              Instructions added to the output rules generation prompt
    --vars inverseOutputRulesInstructions=TEXT       Instructions added to the inverse output rules generation prompt
    --vars testExpansionInstructions=TEXT            Instructions added to the test expansion generation prompt
    --vars storeCompletions=true                          Store chat completions using stored completions
    --vars storeModel=MODEL                          Model used to create stored completions
    --vars groundtruth=true                          Generate groundtruth for the tests (default: true)
    --vars groundtruthModel=MODEL                     Model used to generate groundtruth
    --vars customMetric=TEXT                          Custom Test Evaluation Template
    --vars createEvalRuns=true                             Create an Evals run in OpenAI Evals
    --vars testExpansions=INT                         Number of test expansion phase to generate tests (default: 0)
    --vars testSamplesCount=INT                       Number of test samples to include for the rules and test generation
    --vars testSamplesShuffle=true                         Shuffle the test samples before generating tests for the prompt
    --vars filterTestCount=INT                        Number of tests to include in the filtered output of evalTestCollection

For more details, see https://microsoft.github.io/promptpex/cli/`
    )
    process.exit(1)
}

output.heading(1, "PromptPex Test Generation")
output.detailsFenced(`options`, options, "yaml")
for (const run of runs) {
    dbg(`file: %s`, run.name)
    dbg(`writeResults: %s`, run.writeResults)
    await promptpexGenerate(run)
}
output.appendContent("\n")
