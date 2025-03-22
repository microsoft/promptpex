import { PROMPT_EVAL_OUTPUT_RULE_AGREEMENT } from "./constants.mts"
import { modelOptions, parsBaselineTestEvals } from "./parsers.mts"
import { measure } from "./perf.mts"
import type {
    PromptPexContext,
    PromptPexOptions,
    PromptPexTestEval,
} from "./types.mts"
const { generator } = env

export async function evaluateRulesSpecAgreement(
    files: PromptPexContext,
    options?: PromptPexOptions & { model?: ModelType; force?: boolean }
) {
    const { model } = options || {}
    const moptions = modelOptions(model, options)

    const baselineTests = parsBaselineTestEvals(files)
    const validBaselineTests = baselineTests.filter((t) => t.validity === "ok")

    const intent = files.intent.content
    const rules = files.rules.content

    const results: PromptPexTestEval[] = []
    for (const baselineTest of validBaselineTests) {
        const res = await measure("eval.rules.agreement", () =>
            generator.runPrompt(
                (ctx) => {
                    ctx.importTemplate(PROMPT_EVAL_OUTPUT_RULE_AGREEMENT, {
                        intent,
                        rules,
                        testInput: baselineTest.input,
                    })
                },
                {
                    ...moptions,
                    cache: "promptpex",
                    label: `evaluate rules spec agreement for ${model}...`,
                }
            )
        )
        results.push({
            ...baselineTest,
            // TODO: review
            coverage: res.text as any,
            //coverageText: res.text,
            //coverage: parseOKERR(res.text),
        })
    }
    files.ruleCoverages.content = JSON.stringify(results, null, 2)
    await workspace.writeText(
        files.ruleCoverages.filename,
        files.ruleCoverages.content
    )
    return results
}
