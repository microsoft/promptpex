import { PROMPT_GENERATE_BASELINE_TESTS } from "./constants.mts"
import { outputPrompty } from "./output.mts"
import {
    parseRulesTests,
    modelOptions,
    isUnassistedResponse,
    checkLLMResponse,
    cleanBaselineTests,
} from "./parsers.mts"
import { measure } from "./perf.mts"
import type { PromptPexContext, PromptPexOptions } from "./types.mts"
const { generator } = env
const dbg = host.logger("promptpex:gen:baseline")

export async function generateBaselineTests(
    files: PromptPexContext,
    options?: PromptPexOptions & { num?: number }
): Promise<string> {
    const { baselineModel = "baseline" } = options || {}
    const tests = parseRulesTests(files.tests.content)
    if (!tests?.length)
        throw new Error("No tests found to generate baseline tests")
    const { num = tests.length } = options || {}
    if (!num) throw new Error("Number of baseline tests must be positive")
    const context = MD.content(files.prompt.content)
    const pn = PROMPT_GENERATE_BASELINE_TESTS
    await outputPrompty(pn, options)
    const res = await measure("gen.baseline", () =>
        generator.runPrompt(
            (ctx) => {
                ctx.importTemplate(pn, {
                    num,
                    prompt: context,
                })
            },
            {
                ...modelOptions(baselineModel, options),
                //      logprobs: true,
                label: `${files.name}> generate baseline tests`,
            }
        )
    )

    if (isUnassistedResponse(res.text)) {
        dbg(`unassisted response: ${res.text}`)
        return ""
    }
    checkLLMResponse(res)
    const cleaned = cleanBaselineTests(res.text)
    dbg(`cleaned baseline tests: %O`, cleaned)
    const txt = cleaned.join("\n===\n")
    return txt
}
