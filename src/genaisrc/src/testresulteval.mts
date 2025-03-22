import { PROMPT_EVAL_TEST_RESULT } from "./constants.mts"
import { modelOptions, checkLLMResponse } from "./parsers.mts"
import { measure } from "./perf.mts"
import {
    PromptPexContext,
    PromptPexTestResult,
    PromptPexOptions,
} from "./types.mts"
const { generator } = env

export async function evaluateTestResult(
    files: PromptPexContext,
    testResult: PromptPexTestResult,
    options: PromptPexOptions
): Promise<string> {
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
                choices: ["OK", "ERR"],
                label: `${files.name}> evaluate test result ${testResult.model} ${testResult.input.slice(0, 42)}...`,
            }
        )
    )
    const evaluation = checkLLMResponse(res)
    return evaluation
}
