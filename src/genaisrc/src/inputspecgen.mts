import { PROMPT_GENERATE_INPUT_SPEC, PROMPT_EXTRACT_INPUT_ENTITIES } from "./constants.mts"
import { outputWorkflowDiagram, outputPrompty } from "./output.mts"
import { modelOptions, checkLLMResponse, tidyRules } from "./parsers.mts"
import { measure } from "./perf.mts"
import type { PromptPexContext, PromptPexOptions } from "./types.mts"
const { generator } = env

export async function generateInputEntities(
    files: PromptPexContext,
    options?: PromptPexOptions
) {
    const { rulesModel = "rules" } = options || {}
    const context = MD.content(files.prompt.content)
    
    outputWorkflowDiagram(
        `PUT(["Prompt Under Test (PUT)"])
IE["Input Entities (IE)"]
PUT --> IE`,
        options
    )

    const pn = PROMPT_EXTRACT_INPUT_ENTITIES
    await outputPrompty(pn, options)
    const res = await measure("gen.entities", () =>
        generator.runPrompt(
            (ctx) => {
                ctx.importTemplate(pn, {
                    context,
                })
            },
            {
                ...modelOptions(rulesModel, options),
                label: `${files.name}> generate input entities`,
            }
        )
    )
    return checkLLMResponse(res).split("\n").filter(line => line.trim()).join("\n")
}

export async function generateInputSpec(
    files: PromptPexContext,
    options?: PromptPexOptions
) {
    const instructions = options?.instructions?.inputSpec || ""
    outputWorkflowDiagram(
        `PUT(["Prompt Under Test (PUT)"])
IS["Input Specification (IS)"]
PUT --> IS`,
        options
    )

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
                    input_entities: files.inputEntities.content,
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
