import { OK_ERR_CHOICES, PROMPT_EVAL_TEST_VALIDITY } from "./constants.mts"
import { modelOptions, parseOKERR, parseBaselineTests } from "./parsers.mts"
import { measure } from "./perf.mts"
import type { PromptPexContext, PromptPexOptions } from "./types.mts"
const { generator } = env
const dbg = host.logger("promptpex:eval:baseline")

export async function evaluateBaselineTests(
    files: PromptPexContext,
    options?: PromptPexOptions & { force?: boolean }
) {
    const { evalModel = "eval" } = options || {}
    const moptions = modelOptions(evalModel, options)
    const inputSpec = files.inputSpec.content
    const baselineTests = parseBaselineTests(files)

    dbg(`eval ${baselineTests.length} baseline tests`)
    const results = []
    for (const baselineTest of baselineTests) {
        const { testinput, ...rest } = baselineTest
        const resValidity = await measure("eval.baseline", () =>
            generator.runPrompt(
                (ctx) => {
                    ctx.importTemplate(PROMPT_EVAL_TEST_VALIDITY, {
                        input_spec: inputSpec,
                        test: testinput,
                    })
                },
                {
                    ...moptions,
                    choices: OK_ERR_CHOICES,
                    label: `${files.name}> evaluate validity of baseline test ${baselineTest.testinput.slice(0, 42)}...`,
                }
            )
        )
        const valid = parseOKERR(resValidity.text)
        results.push({
            input: testinput,
            validity: valid,
            validityText: resValidity.text,
            ...rest,
        })
    }
    return JSON.stringify(results, null, 2)
}
