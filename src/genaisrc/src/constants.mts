import { fileURLToPath } from "node:url"
import { dirname, join, resolve } from "node:path"
import type { PromptPexOptions } from "./types.mts"

const genaisrcSrcDir = dirname(fileURLToPath(import.meta.url))
export const PARAMETER_INPUT_TEXT = "input_text"
export const PROMPT_DIR = resolve(genaisrcSrcDir, "..", "..", "prompts")

export const PROMPT_GENERATE_INPUT_SPEC = join(
    PROMPT_DIR,
    "generate_input_spec.prompty"
)
export const PROMPT_GENERATE_INTENT = join(
    PROMPT_DIR,
    "generate_intent.prompty"
)
export const PROMPT_RATE_TESTS = join(
    PROMPT_DIR, "evals",
    "eval_test_collection.prompty"
)
export const PROMPT_FILTER_TESTS = join(
    PROMPT_DIR, "evals",
    "filter_test_collection.prompty"
)
export const PROMPT_GENERATE_OUTPUT_RULES = join(
    PROMPT_DIR,
    "generate_output_rules.prompty"
)
export const PROMPT_GENERATE_BASELINE_TESTS = join(
    PROMPT_DIR,
    "generation",
    "generate_baseline_tests.prompty"
)
export const PROMPT_GENERATE_INVERSE_RULES = join(
    PROMPT_DIR,
    "generate_inverse_rules.prompty"
)
export const PROMPT_GENERATE_TESTS = join(PROMPT_DIR, "generate_tests.prompty")
export const PROMPT_EVAL_RULE_GROUNDED = join(
    PROMPT_DIR,
    "evals",
    "eval_rule_grounded.prompty"
)
export const PROMPT_EVAL_TEST_VALIDITY = join(
    PROMPT_DIR,
    "evals",
    "eval_test_validity.prompty"
)
export const PROMPT_EVAL_OUTPUT_RULE_AGREEMENT = join(
    PROMPT_DIR,
    "evals",
    "eval_output_rule_agreement.prompty"
)
export const PROMPT_EVAL_TEST_RESULT = join(
    PROMPT_DIR,
    "evals",
    "eval_test_result.prompty"
)
export const PROMPTPEX_CONTEXT = "promptpex_context.json"

export const PROMPT_EXPAND_TEST = join(
    PROMPT_DIR,
    "generation",
    "expand_test.prompty"
)

export const PROMPT_ALL = [
    PROMPT_GENERATE_INPUT_SPEC,
    PROMPT_GENERATE_INTENT,
    PROMPT_GENERATE_OUTPUT_RULES,
    PROMPT_GENERATE_BASELINE_TESTS,
    PROMPT_GENERATE_INVERSE_RULES,
    PROMPT_GENERATE_TESTS,
    PROMPT_EVAL_RULE_GROUNDED,
    PROMPT_EVAL_TEST_VALIDITY,
    PROMPT_EVAL_OUTPUT_RULE_AGREEMENT,
    PROMPT_EVAL_TEST_RESULT,
    PROMPT_EXPAND_TEST,

    PROMPT_FILTER_TESTS,
    PROMPT_RATE_TESTS,
]

export const INTENT_RETRY = 2
export const RATE_TESTS_RETRY = 2
export const INPUT_SPEC_RETRY = 2
export const CONCURRENCY = 2
export const RULES_NUM = 0
export const TESTS_NUM = 3

export const GROUNDTRUTH_THRESHOLD = 80
export const GROUNDTRUTH_RETRIES = 3
export const GROUNDTRUTH_FAIL_SCORE = -1

export const TEST_EVALUATION_DIR = "test_evals"
export const RULE_EVALUATION_DIR = "rule_evals"
export const DOCS_TEST_GENERATION_DIAGRAM = `
graph TD
    PUT(["Prompt Under Test (PUT)"])
    IS["Input Specification (IS)"]
    OR["Output Rules (OR)"]
    IOR["Inverse Output Rules (IOR)"]
    PPT["PromptPex Tests (PPT)"]
    TO["Test Output (TO) for MUT"]

    PUT --> IS

    PUT --> OR
    OR --> IOR

    PUT --> PPT
    IS --> PPT
    OR --> PPT
    IOR --> PPT

    PPT --> TO
    PUT --> TO
`

export const DIAGRAM_GENERATE_TESTS = `PUT(["Prompt Under Test (PUT)"])
IS["Input Specification (IS)"]
OR["Output Rules (OR)"]
IOR["Inverse Output Rules (IOR)"]
PPT["PromptPex Tests (PPT)"]

PUT --> IS

PUT --> OR
OR --> IOR

PUT --> PPT
IS --> PPT
OR --> PPT
IOR --> PPT        
`
export const DIAGRAM_GENERATE_INPUT_SPEC = `PUT(["Prompt Under Test (PUT)"])
IS["Input Specification (IS)"]
PUT --> IS`
export const DIAGRAM_GENERATE_OUTPUT_RULES = `PUT(["Prompt Under Test (PUT)"])
OR["Output Rules (OR)"]

PUT --> OR        
`

export const SCENARIO_SYMBOL = "scene"
export const RULE_SYMBOL = "rule"
export const GENERATION_SYMBOL = "gen"
export const METRIC_SEPARATOR = " with "
export const METRIC_SUMMARY = "average"

export const DOCS_GLOSSARY = `
- Prompt Under Test (PUT) - like Program Under Test; the prompt
- Model Under Test (MUT) - Model which we are testing against with specific temperature, etc example: gpt-4o-mini
- Model Used by PromptPex (MPP) - gpt-4o/llama3.3

- Intent (I) - 
- Input Specification (IS) - Extracting input constraints of PUT using MPP
- Output Rules ${RULE_SYMBOL} (OR) - Extracting output constraints of PUT using MPP
- Output Rules Groundedness (ORG) - Checks if OR is grounded in PUT using MPP

- Prompt Under Test Intent (PUTI) - Extracting the exact task from PUT using MMP

- PromptPex Tests (PPT) - Test cases generated for PUT with MPP using IS and OR
- Baseline Tests (BT) - Zero shot test cases generated for PUT with MPP

- Test Input Compliance (TIC) - Checking if PPT and BT meets the constraints in IS using MPP
- Test Coverage (TC) - Result generated for PPT and BT on PUTI + OR with MPP

- Test Output (TO) - Result generated for PPT and BT on PUT with each MUT
- Test Output Compliance (TOC) - Checking if TO meets the constraints in PUT using MPP

- Test Generation Scenario ${SCENARIO_SYMBOL} (TS) - A scenario used to generate tests
- Test Generation Iteration ${GENERATION_SYMBOL} (TGI) - A scenario used to generate tests
`

export const OK_ERR_CHOICES = ["OK", "ERR"]
export const OK_CHOICE = OK_ERR_CHOICES[0]
export const TEST_DATA_LENGTH = 64

export const TEST_SAMPLES_COUNT_DEFAULT = 5

export const MODEL_ALIAS_EVAL = "eval"
export const MODEL_ALIAS_GROUNDTRUTH_EVAL = "groundtruth_eval"
export const MODEL_ALIAS_STORE = "store"
export const MODEL_ALIAS_RULES = "rules"
export const MODEL_ALIAS_GROUNDTRUTH = "groundtruth"
// export const MODEL_ALIAS_MODELS_UNDER_TEST = ["model_under_test_small", "model_under_test_tiny"]
export const MODEL_ALIAS_MODELS_UNDER_TEST = []

export const TEST_TRAINING_DATASET_RATIO = 0.75

export const EFFORTS: Record<string, Partial<PromptPexOptions>> = {
    min: {
        splitRules: true,
        testGenerations: 1,
        testsPerRule: 1,
        runsPerTest: 1,
        testExpansions: 0,
        maxRules: 10,
        maxRulesPerTestGeneration: 100,
        maxTestsToRun: 80,
        compliance: true,
    },
    low: {
        testExpansions: 0,
        testGenerations: 1,
        maxRules: 3,
        maxRulesPerTestGeneration: 100,
        maxTestsToRun: 80,
    },
    medium: {
        testExpansions: 0,
        maxRules: 20,
        testsPerRule: 3,
        runsPerTest: 1,
        maxRulesPerTestGeneration: 5,
        splitRules: true,
        testGenerations: 1,
    },
    high: {
        testExpansions: 1,
        maxRules: 50,
        maxRulesPerTestGeneration: 2,
        splitRules: true,
        testGenerations: 2,
    },
}

export const scoringOutputFormat = `
### Evaluation
Ensure your response is valid JSON using the following JSON schema:

{
    "type": "object",
    "properties": {
        "explanation": {
            "type": "string",
            "description": "Explain reasoning behind generating the score based on the criteria outlined in the instruction. Only keep a minimum draft with 5 words at most."
        },
        "score": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100,
            "description": "Provide a score from 0 to 100 based on the criteria of the chatbot output as defined above"
        }
    },
    "required": ["explanation", "score"],
}

`

export const okErrorOutputFormat = `
## Output
**Binary Decision on Evaluation**: You are required to make a binary decision based on your evaluation:
- Return 'OK' if <OUTPUT> is compliant with <CRITERIA>.
- Return 'ERR' if <OUTPUT> is **not** compliant with <CRITERIA> or if you are unable to confidently answer.
`

export const githubModelsOutputFormat = `
## Output
Rate the answer on a scale from 1-5 where:
1 = Poor (completely wrong or irrelevant)
2 = Below Average (partially correct but missing key information)
3 = Average (mostly correct with minor gaps)
4 = Good (accurate and complete with clear explanation)
5 = Excellent (exceptionally accurate, complete, and well-explained)
You must respond with ONLY the number rating (1, 2, 3, 4, or 5).
`

export const GITHUB_MODELS_RX = /\.prompt\.yml$/
export const TEMPLATE_VARIABLE_RX = /\{\{\s*(?<id>\w+)\s*\}\}/g

export const OUTPUT_TABLE_MAX_ROWS = 100
