import { RATE_TESTS_RETRY, PROMPT_RATE_TESTS } from "./constants.mts"
import { outputPrompty } from "./output.mts"
import { modelOptions, checkLLMResponse } from "./parsers.mts"
import { measure } from "./perf.mts"
import type { PromptPexContext, PromptPexOptions } from "./types.mts"
const { generator } = env
const dbg = host.logger("promptpex:gen:ratetests")

export async function eval_test_collection (
    files: PromptPexContext,
    options?: PromptPexOptions
): Promise<void> {
    const { rulesModel = "rules" } = options || {}
    const context = MD.content(files.prompt.content)

    const pn = PROMPT_RATE_TESTS
    await outputPrompty(pn, options)

    for (let i = 0; i < RATE_TESTS_RETRY; i++) {
        dbg(`attempt ${i + 1} of ${RATE_TESTS_RETRY}`)
        const res = await measure("gen.ratetests", () =>
            generator.runPrompt(
                (ctx) => {
                    ctx.importTemplate(pn, {
                        prompt: context,
                        tests: files.testData.content
                    })
                },
                {
                    ...modelOptions(rulesModel, options),
                    label: `${files.name}> ratetests`,
                }
            )
        )
        if (!files.rateTests) files.rateTests = { filename: files.name + ".rateTests.md", content: "" };
        files.rateTests.content = checkLLMResponse(res)
        if (files.writeResults) await workspace.writeFiles([files.rateTests])
        if (files.rateTests.content) break

        dbg(`failed, try again`)
        dbg(res.text)
    }
    if (!files.rateTests.content) throw new Error("failed to generate intent")
}
