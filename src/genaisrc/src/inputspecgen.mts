import {
    DIAGRAM_GENERATE_INPUT_SPEC,
    INPUT_SPEC_RETRY,
    PROMPT_GENERATE_INPUT_SPEC,
} from "./constants.mts"
import { outputWorkflowDiagram, outputPrompty } from "./output.mts"
import { modelOptions, checkLLMResponse, tidyRules } from "./parsers.mts"
import { measure } from "./perf.mts"
import type { PromptPexContext, PromptPexOptions } from "./types.mts"
const { generator } = env
const dbg = host.logger("promptpex:gen:inputspec")

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
    const testSamples = files.testSamples
    const examples = testSamples?.length ? YAML.stringify(testSamples) : ""
    const pn = PROMPT_GENERATE_INPUT_SPEC
    await outputPrompty(pn, options)

    for (let i = 0; i < INPUT_SPEC_RETRY; ++i) {
        dbg(`attempt ${i + 1} of ${INPUT_SPEC_RETRY}`)
        const res = await measure("gen.inputspec", () =>
            generator.runPrompt(
                (ctx) => {
                    ctx.importTemplate(pn, {
                        context,
                        instructions,
                        examples,
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
        if (files.inputSpec.content) break
        dbg(`failed, try again`)
        dbg(res.text)
    }
    if (!files.inputSpec.content)
        throw new Error("Failed to generate input spec")
}
