import { INTENT_RETRY, PROMPT_GENERATE_INTENT } from "./constants.mts"
import { outputPrompty } from "./output.mts"
import { modelOptions, checkLLMResponse } from "./parsers.mts"
import { measure } from "./perf.mts"
import type { PromptPexContext, PromptPexOptions } from "./types.mts"
const { generator } = env
const dbg = host.logger("promptpex:intent")

export async function generateIntent(
    files: PromptPexContext,
    options?: PromptPexOptions
): Promise<void> {
    const { rulesModel = "rules" } = options || {}
    const context = MD.content(files.prompt.content)
    const instructions =
        options?.instructions?.intent ||
        files.frontmatter?.instructions?.intent ||
        ""
    const pn = PROMPT_GENERATE_INTENT
    await outputPrompty(pn, options)

    for (let i = 0; i < INTENT_RETRY; i++) {
        dbg(`attempt ${i + 1} of ${INTENT_RETRY}`)
        const res = await measure("gen.intent", () =>
            generator.runPrompt(
                (ctx) => {
                    ctx.importTemplate(pn, {
                        prompt: context,
                        instructions,
                    })
                },
                {
                    ...modelOptions(rulesModel, options),
                    label: `${files.name}> intent`,
                }
            )
        )
        files.intent.content = checkLLMResponse(res)
        if (files.writeResults) await workspace.writeFiles([files.intent])
        if (files.intent.content) break

        dbg(`failed, try again`)
    }
    if (!files.intent.content) throw new Error("failed to generate intent")
}
