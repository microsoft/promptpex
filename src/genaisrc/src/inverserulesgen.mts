import { PROMPT_GENERATE_INVERSE_RULES } from "./constants.mts"
import { outputWorkflowDiagram, outputPrompty } from "./output.mts"
import {
    modelOptions,
    checkLLMResponse,
    tidyRules,
    parseRules,
} from "./parsers.mts"
import { measure } from "./perf.mts"
import type { PromptPexContext, PromptPexOptions } from "./types.mts"
const { generator } = env

export async function generateInverseOutputRules(
    files: PromptPexContext,
    options?: PromptPexOptions
) {
    const { rulesModel = "rules" } = options || {}
    const instructions =
        options?.instructions?.inverseOutputRules ||
        files.frontmatter?.instructions?.inverseOutputRules ||
        ""
    outputWorkflowDiagram(
        `OR["Output Rules (OR)"]
IOR["Inverse Output Rules (IOR)"]
OR --> IOR    
`,
        options
    )

    const rule = MD.content(files.rules.content)
    const prules = parseRules(rule)
    const pn = PROMPT_GENERATE_INVERSE_RULES
    await outputPrompty(pn, options)

    let irules: string
    let pirules: string[]
    let retry = 3
    do {
        const res = await measure("gen.inverseoutputrules", () =>
            generator.runPrompt(
                (ctx) => {
                    ctx.importTemplate(pn, {
                        rule,
                        instructions,
                    })
                },
                {
                    ...modelOptions(rulesModel, options),
                    //      logprobs: true,
                    label: `${files.name}> inverse rules`,
                }
            )
        )
        irules = tidyRules(checkLLMResponse(res))
        pirules = parseRules(irules)
    } while (retry-- > 0 && pirules.length !== prules.length)

    if (pirules.length !== prules.length) {
        console.warn(
            `inverse rules length mismatch: generated ${pirules.length}, expected ${prules.length}`
        )
    }

    return irules
}
