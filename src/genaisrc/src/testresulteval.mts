import { OK_ERR_CHOICES, PROMPT_EVAL_TEST_RESULT } from "./constants.mts"
import { modelOptions, checkLLMEvaluation } from "./parsers.mts"
import { measure } from "./perf.mts"
import type {
    PromptPexContext,
    PromptPexTestResult,
    PromptPexOptions,
    PromptPexEvaluation,
} from "./types.mts"
const { generator } = env

export async function evaluateTestResult(
    files: PromptPexContext,
    testResult: PromptPexTestResult,
    options: PromptPexOptions
): Promise<PromptPexEvaluation> {
    const { evalModel = "eval" } = options || {}
    const moptions = modelOptions(evalModel, options)

    const content = MD.content(files.prompt.content)
    const res = await measure("eval.test", () =>
        generator.runPrompt(
            (ctx) => {
                // removes frontmatter
                ctx.importTemplate(PROMPT_EVAL_TEST_RESULT, {
                    system: content.replace(/^(system|user):/gm, ""),
                    result: testResult.output,
                })
            },
            {
                ...moptions,
                choices: OK_ERR_CHOICES,
                logprobs: true,
                label: `${files.name}> eval test result ${testResult.model} ${testResult.input.slice(0, 42)}...`,
            }
        )
    )
    const evaluation = checkLLMEvaluation(res, { allowUnassisted: true })
    return evaluation
}
