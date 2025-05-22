import { RATE_TESTS_RETRY, PROMPT_RATE_TESTS, PROMPT_FILTER_TESTS } from "./constants.mts"
import { outputPrompty } from "./output.mts"
import { modelOptions, checkLLMResponse } from "./parsers.mts"
import { measure } from "./perf.mts"
import type { PromptPexContext, PromptPexOptions } from "./types.mts"
const { generator } = env
const dbg = host.logger("promptpex:gen:ratetests")

export async function evalTestCollection (
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
        files.rateTests.content = checkLLMResponse(res)
        if (files.writeResults) await workspace.writeFiles([files.rateTests])
        if (files.rateTests.content) break

        dbg(`failed, try again`)
        dbg(res.text)
    }
    if (!files.rateTests.content) throw new Error("failed evaluate test collection")

    const pnf = PROMPT_FILTER_TESTS
    await outputPrompty(pnf, options)

    for (let i = 0; i < RATE_TESTS_RETRY; i++) {
        dbg(`attempt ${i + 1} of ${RATE_TESTS_RETRY}`)
        const res = await measure("gen.filtertests", () =>
            generator.runPrompt(
                (ctx) => {
                    ctx.importTemplate(pnf, {
                        prompt: context,
                        tests: files.tests.content,
                        filter_critera: files.rateTests.content,
                        target_test_number: options?.filterTestCount
                    })
                },
                {
                    ...modelOptions(rulesModel, options),
                    responseType: "text",
                    label: `${files.name}> filtertests`,
                }
            )
        )
        files.filteredTests.content = checkLLMResponse(res)
        if (files.writeResults) await workspace.writeFiles([files.filteredTests])
        if (files.filteredTests.content) break

        dbg(`failed, try again`)
        dbg(res.text)
    }
    if (!files.rateTests.content) throw new Error("failed evaluate test collection")        
}
