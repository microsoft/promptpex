import { PROMPT_GENERATE_INTENT } from "./constants.mts"
import { outputPrompty } from "./output.mts"
import { modelOptions, checkLLMResponse } from "./parsers.mts"
import { measure } from "./perf.mts"
import { PromptPexContext, PromptPexOptions } from "./types.mts"
const { generator } = env

export async function generateIntent(
    files: PromptPexContext,
    options?: PromptPexOptions
): Promise<string> {
    const { rulesModel = "rules" } = options || {}
    const context = MD.content(files.prompt.content)
    const instructions = options?.instructions?.intent || ""
    const pn = PROMPT_GENERATE_INTENT
    await outputPrompty(pn, options)
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
                //      logprobs: true,
                label: `${files.name}> generate intent`,
            }
        )
    )
    return checkLLMResponse(res)
}
