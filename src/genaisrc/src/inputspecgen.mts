import { DIAGRAM_GENERATE_INPUT_SPEC, PROMPT_GENERATE_INPUT_SPEC } from "./constants.mts"
import { outputWorkflowDiagram, outputPrompty } from "./output.mts"
import { modelOptions, checkLLMResponse, tidyRules } from "./parsers.mts"
import { measure } from "./perf.mts"
import type { PromptPexContext, PromptPexOptions } from "./types.mts"
const { generator } = env

export async function generateInputSpec(
    files: PromptPexContext,
    options?: PromptPexOptions
) {
    const instructions = options?.instructions?.inputSpec || ""
    outputWorkflowDiagram(DIAGRAM_GENERATE_INPUT_SPEC, options)

    const { rulesModel = "rules" } = options || {}
    const context = MD.content(files.prompt.content)
    const pn = PROMPT_GENERATE_INPUT_SPEC
    await outputPrompty(pn, options)
    const res = await measure("gen.inputspec", () =>
        generator.runPrompt(
            (ctx) => {
                ctx.importTemplate(pn, {
                    context,
                    instructions,
                })
            },
            {
                ...modelOptions(rulesModel, options),
                //      logprobs: true,
                label: `${files.name}> generate input spec`,
            }
        )
    )
    return tidyRules(checkLLMResponse(res))
}
