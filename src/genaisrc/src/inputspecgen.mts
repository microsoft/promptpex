import {
    DIAGRAM_GENERATE_INPUT_SPEC,
    PROMPT_GENERATE_INPUT_SPEC,
} from "./constants.mts"
import { outputWorkflowDiagram, outputPrompty } from "./output.mts"
import { modelOptions, checkLLMResponse, tidyRules } from "./parsers.mts"
import { measure } from "./perf.mts"
import type { PromptPexContext, PromptPexOptions } from "./types.mts"
const { generator } = env

export async function generateInputSpec(
    files: PromptPexContext,
    options?: PromptPexOptions
): Promise<void> {
    const instructions =
        options?.instructions?.inputSpec ||
        files.frontmatter?.instructions?.inputSpec ||
        ""
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
                label: `${files.name}> input spec`,
            }
        )
    )
    files.inputSpec.content = tidyRules(checkLLMResponse(res))
    if (files.writeResults) await workspace.writeFiles([files.inputSpec])
}
