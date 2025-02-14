export type PromptPexModelAliases = OptionsOrString<"rules" | "eval" | "large">;

export interface PromptPexPrompts {
    /**
     * Input specifications, overrides input spec generation
     */
    inputSpec?: string;
    /**
     * Output rules, overrides output rules generation
     */
    outputRules?: string;
    /**
     * Inverse output rules, overrides inverse output rules generation
     */
    inverseOutputRules?: string;
    /**
     * Prompt intent, overrides intent generation
     */
    intent?: string;
}

export interface PromptPexOptions {
    /**
     * Do not include Responsible AI safety prompts and validation
     */
    disableSafety?: boolean;
    /**
     * Generate temperature for requests
     */
    temperature?: number;

    /**
     * Add PromptPex prompts to the output
     */
    outputPrompts?: boolean;

    /**
     * Emit diagrams in output
     */
    workflowDiagram?: boolean;
    /**
     * Aditional instructions
     */
    instructions?: PromptPexPrompts;
    /**
     * Custom model aliases
     */
    modelAliases?: Partial<Record<PromptPexModelAliases, string>>;

    /**
     * Caches resuls in the file system
     */
    evalCache?: boolean;
}

/**
 * In memory cache of various files involved with promptpex test generation.
 *
 * - Model Used by PromptPex (MPP) - gpt-4o
 * - Model Under Test (MUT) - Model which we are testing against with specific temperature, etc example: gpt-4o-mini
 */
export interface PromptPexContext {
    /**
     * Prompt folder location if any
     */
    dir?: string;
    /**
     * Prompt name
     */
    name: string;
    /**
     * Prompt parsed frontmatter section
     */
    frontmatter: any;
    /**
     * Inputs extracted from the prompt frontmatter
     */
    inputs: Record<string, any>;
    /**
     * Metadata extract from the prompt frontmatter
     */
    meta: PromptPexPrompts;

    /**
     * Prompt Under Test
     */
    prompt: WorkspaceFile;
    /**
 0  * Prompt Under Test Intent (PUTI)
   */
    intent: WorkspaceFile;
    /**
     * Output Rules (OR) - Extracted output constraints of PUT using MPP
     */
    rules: WorkspaceFile;
    /**
     * Inverse output rules (IOR) - Negated OR rules
     */
    inverseRules: WorkspaceFile;
    /**
     * Input specification (IS): Extracted input constraints of PUT using MPP
     */
    inputSpec: WorkspaceFile;

    /**
     * Baseline Tests (BT) - Zero shot test cases generated for PUT with MPP
     */
    baselineTests: WorkspaceFile;

    /**
     * PromptPex Tests (PPT) - Test cases generated for PUT with MPP using IS and OR (test)
     */
    tests: WorkspaceFile;

    /**
     * Test Output (TO) - Result generated for PPT and BT on PUT with each MUT (the template is PUT)
     */
    testOutputs: WorkspaceFile;

    /**
     * Coverage and validate test evals
     */
    testEvals: WorkspaceFile;

    /**
     * Groundedness
     */
    ruleEvals: WorkspaceFile;

    /**
     * Coverage of rules
     */
    ruleCoverages: WorkspaceFile;
    /**
     * Baseline tests validaty
     */
    baselineTestEvals: WorkspaceFile;
}

export interface PromptPexTest {
    /**
     * Index of the rule in the OR+IOR rules. undefined for baseline tests.
     */
    ruleid?: number;
    /**
     * Index of the generated test for the given rule. undefined for baseline tests
     */
    testid?: number;
    /**
     * Generated by the baseline prompt
     */
    baseline?: boolean;
    /**
     * Prompt test input text
     */
    testinput: string;
    /**
     * Expected output generated by the PromptPex Test generator
     */
    expectedoutput?: string;
    /**
     * Explanation of the test generation process
     */
    reasoning?: string;
}

export interface PromptPexTestResult {
    id: string;
    promptid: string;
    ruleid: number;
    rule: string;
    inverse?: boolean;
    baseline?: boolean;
    model: string;
    input: string;
    output: string;
    error?: string;

    compliance?: "ok" | "err";
    complianceText?: string;
}

export interface PromptPexTestEval {
    id: string;
    promptid: string;
    model?: string;
    rule: string;
    inverse?: boolean;
    input: string;
    coverage?: "ok" | "err";
    coverageEvalText?: string;
    coverageText?: string;
    validity?: "ok" | "err";
    validityText?: string;
    error?: string;
}

export interface PromptPexRuleEval {
    id: string;
    promptid: string;
    ruleid: number;
    rule: string;
    groundedText?: string;
    grounded?: "ok" | "err";
    error?: string;
}
