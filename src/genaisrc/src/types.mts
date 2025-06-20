export type PromptPexModelAliases = OptionsOrString<
    "rules" | "eval" | "large" | "baseline" | "groundtruth"
>

export interface PromptPexPrompts {
    /**
     * Input specifications, overrides input spec generation
     */
    inputSpec?: string
    /**
     * Output rules, overrides output rules generation
     */
    outputRules?: string
    /**
     * Inverse output rules, overrides inverse output rules generation
     */
    inverseOutputRules?: string
    /**
     * Prompt intent, overrides intent generation
     */
    intent?: string
    /**
     * Test expansion prompt
    ) */
    testExpansion?: string
}

interface PromptPexCliExtraOptions {
    evalModel?: ModelType
    effort?: "min" | "low" | "medium" | "high"
    customMetric?: string
    prompt?: string
    inputSpecInstructions?: string
    outputRulesInstructions?: string
    inverseOutputRulesInstructions?: string
    testExpansionInstructions?: string
}

export interface PromptPexBaseOptions extends PromptPexLoaderOptions {
    /**
     * Generate temperature for requests
     */
    temperature?: number

    /**
     * Add PromptPex prompts to the output
     */
    outputPrompts?: boolean

    /**
     * Emit diagrams in output
     */
    workflowDiagram?: boolean

    /**
     * Additional instructions
     */
    instructions?: PromptPexPrompts
    /**
     * Custom model aliases
     */
    modelAliases?: Partial<Record<PromptPexModelAliases, string>>

    /**
     * Caches results in the file system
     */
    evalCache?: boolean

    /**
     * Evaluate the test results
     */
    evals?: boolean

    /**
     * Cache runTest results
     */
    testRunCache?: boolean

    /**
     * Model used to generate rules
     */
    rulesModel?: string

    /**
     * Model used to run tests for distillation/evaluation
     */
    storeModel?: ModelType

    /**
     * Compute groundtruth for the tests.
     */
    groundtruth?: boolean

    /**
     * Model used to generate ground truth
     */
    groundtruthModel?: ModelType

    /**
     * Model used to generate baseline tests
     */
    baselineModel?: ModelType

    /**
     * Number of tests to generate per rule
     */
    testsPerRule?: number

    /**
     * Number of run to execute per test
     */
    runsPerTest?: number

    /**
     * Evaluate test result coverage and validity
     */
    compliance?: boolean

    /**
     * Generate and evaluate baseline tests
     */
    baselineTests?: boolean

    /**
     * Maximum number of tests to run
     */
    maxTestsToRun?: number

    /**
     * Maximum number of output rules (and inverse rules) to use
     */
    maxRules?: number

    /**
     * Cache applied to all prompts, expect run test.
     */
    cache?: boolean | string

    /**
     * Run tests with 'store' model and store completions for fine tuning or evaluation
     */
    storeCompletions?: boolean

    /**
     * List of models to run the prompt against
     */
    modelsUnderTest?: ModelType[]

    /**
     * Split rules/inverse rules in separate prompts
     */
    splitRules?: boolean

    /**
     * Maximum number of rules to use per test generation
     */
    maxRulesPerTestGeneration?: number

    /**
     * Number of times to amplify the test generation, default is 1
     */
    testGenerations?: number

    /**
     * Creates a new eval run in OpenAI. Requires OpenAI API key.
     */
    createEvalRuns?: boolean

    /**
     * Applying expansion phase to generate tests.
     */
    testExpansions?: number

    /**
     * Evaluate the test collection
     */
    rateTests?: boolean

    /**
     * Evaluate the test collection
     */
    filterTestCount?: number
}

export interface PromptPexCliOptions
    extends PromptPexBaseOptions,
        PromptPexCliExtraOptions {}

export interface PromptPexOptions extends PromptPexBaseOptions {
    evalModels?: ModelType[]
    evalModelsGroundtruth?: ModelType[]
}

/**
 * In memory cache of various files involved with promptpex test generation.
 *
 * - Model Used by PromptPex (MPP) - gpt-4o
 * - Model Under Test (MUT) - Model which we are testing against with specific temperature, etc example: gpt-4o-mini
 */
export interface PromptPexContext {
    /**
     * Unique identifier for the run
     */
    runId: string

    /** Should write results to files */
    writeResults?: boolean
    /**
     * Prompt folder location if any
     */
    dir?: string
    /**
     * Prompt name
     */
    name: string
    /**
     * Prompt parsed frontmatter section
     */
    frontmatter: PromptPexPromptyFrontmatter

    /**
     * The list of messages used in the prompt
     */
    messages: ChatMessage[]

    /**
     * Inputs extracted from the prompt frontmatter
     */
    inputs: Record<string, JSONSchemaSimpleType>
    /**
     * Prompt Under Test
     */
    prompt: WorkspaceFile

    /**
     * For converted prompts, the original source of the prompt
     */
    originalPrompt?: WorkspaceFile

    /**
 0  * Prompt Under Test Intent (PUTI)
   */
    intent: WorkspaceFile
    /**
     * Output Rules (OR) - Extracted output constraints of PUT using MPP
     */
    rules: WorkspaceFile
    /**
     * Inverse output rules (IOR) - Negated OR rules
     */
    inverseRules: WorkspaceFile
    /**
     * Input specification (IS): Extracted input constraints of PUT using MPP
     */
    inputSpec: WorkspaceFile

    /**
     * Baseline Tests (BT) - Zero shot test cases generated for PUT with MPP
     */
    baselineTests: WorkspaceFile

    /**
     * PromptPex Tests (PPT) - Test cases generated for PUT with MPP using IS and OR (test)
     */
    tests: WorkspaceFile

    /**
     * promptPexTests - Array of test cases generated for PUT
     */
    promptPexTests: PromptPexTest[]

    /**
     * PromptPex Test with resolved input parameters
     */
    testData: WorkspaceFile

    /**
     * PromptPex rateTests
     */
    rateTests: WorkspaceFile

    /**
     * Test Output (TO) - Result generated for PPT and BT on PUT with each MUT (the template is PUT)
     */
    testOutputs: WorkspaceFile

    /**
     * Groudtruth Output (TO) - Test results with metrics for groundtruth test outputs
     */
    groundtruthOutputs: WorkspaceFile

    /**
     * Coverage and validate test evals
     */
    testEvals: WorkspaceFile

    /**
     * Groundedness
     */
    ruleEvals: WorkspaceFile

    /**
     * Coverage of rules
     */
    ruleCoverages: WorkspaceFile
    /**
     * Baseline tests validity
     */
    baselineTestEvals: WorkspaceFile

    /**
     * Evaluation metrics prompt files
     */
    metrics: WorkspaceFile[]

    /**
     * Evaluation metrics for groundtruth prompt files
     */
    groundtruthMetrics: WorkspaceFile[]

    /**
     * Existing test data if any
     */
    testSamples?: Record<string, number | string | boolean>[]

    /**
     * Versions of tooling
     */
    versions: {
        promptpex: string
        node: string
    }

    /**
     * Reuse results
     */
    reuseResults?: boolean

    /**
     * Options when loading context
     */
    options: PromptPexOptions
}

export interface PromptPexTest {
    /**
     * Index of the rule in the OR+IOR rules. undefined for baseline tests.
     */
    ruleid?: number
    /**
     * Index of the generated test for the given rule. undefined for baseline tests
     */
    testid?: number
    /**
     * Unique identifier for the test
     */
    testuid?: string
    /**
     * Generated by the baseline prompt
     */
    baseline?: boolean
    /**
     * Model used to generate the groundtruth
     */
    groundtruthModel?: string
    /**
     * Groundtruth text, generated by the groundtruth model
     */
    groundtruth?: string
    /**
     * Groundtruth score generated by groundtruth metrics from evalModelsGroundtruth
     */
    groundtruthScore?: number

    /**
     * Prompt test input text
     */
    testinput: string
    /**
     * Original test input text, generated by the test generation prompt
     */
    testinputOriginal?: string
    /**
     * Expected output generated by the PromptPex Test generator
     */
    expectedoutput?: string
    /**
     * Explanation of the test generation process
     */
    reasoning?: string

    /**
     * Scenario name
     */
    scenario?: string

    /**
     * Test generation iteration index
     */
    generation?: number
}

export interface PromptPexTestResult {
    id: string
    promptid: string
    ruleid: number
    rule: string
    scenario: string
    testinput: string
    inverse?: boolean
    baseline?: boolean
    model: string
    input: string
    output: string
    error?: string
    testuid?: string
    isGroundtruth?: boolean

    compliance?: PromptPexEvalResultType
    complianceText?: string

    metrics: Record<string, PromptPexEvaluation>
}

export interface PromptPexTestEval {
    id: string
    promptid: string
    model?: string
    rule: string
    inverse?: boolean
    input: string
    coverage?: PromptPexEvalResultType
    coverageEvalText?: string
    coverageText?: string
    coverageUncertainty?: number
    validity?: PromptPexEvalResultType
    validityText?: string
    validityUncertainty?: number
    error?: string
}

export interface PromptPexRule {
    rule: string
    inverse?: boolean
}

export type PromptPexEvalResultType = "ok" | "err" | "unknown"

export interface PromptPexRuleEval {
    id: string
    promptid: string
    ruleid: number
    rule: string
    groundedText?: string
    grounded?: PromptPexEvalResultType
    error?: string
}

export interface PromptPexLoaderOptions {
    out?: string
    disableSafety?: boolean
    customMetric?: string

    /**
     * The number of test samples to use for input spec generation, test generation.
     */
    testSamplesCount?: number
    /**
     * Pick a random sample from the test samples for input spec generation, test generation.
     */
    testSamplesShuffle?: boolean
}

export interface PromptPexTestGenerationScenario {
    name: string
    instructions?: string
    parameters?: Record<string, number | string | boolean>
}

export interface PromptPexPromptyFrontmatter {
    name?: string
    model?: PromptyFrontmatter["model"]
    description?: string
    tags?: OptionsOrString<"scorer" | "unlisted" | "experimental">[]
    inputs?: PromptParametersSchema
    outputs?: JSONSchemaObject["properties"]
    instructions?: PromptPexPrompts
    scenarios?: PromptPexTestGenerationScenario[]
    /**
     * A list of samples or file containing samples.
     */
    testSamples?: (string | Record<string, number | string | boolean>)[]
    /**
     * Extra metadata
     */
    imported?: object
}

export interface PromptPexEvaluation {
    content: string
    uncertainty?: number
    perplexity?: number
    outcome?: PromptPexEvalResultType
    score?: number
}
