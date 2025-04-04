import {
    RULES_NUM,
    PROMPT_GENERATE_OUTPUT_RULES,
    DIAGRAM_GENERATE_OUTPUT_RULES,
} from "./constants.mts"
import { outputWorkflowDiagram, outputPrompty } from "./output.mts"
import { modelOptions, checkLLMResponse, tidyRules } from "./parsers.mts"
import { measure } from "./perf.mts"
import type { PromptPexContext, PromptPexOptions } from "./types.mts"
const dbg = host.logger("promptpex:gen:rules")
const { generator } = env

export async function generateOutputRules(
    files: PromptPexContext,
    options?: PromptPexOptions & { numRules?: number }
) {
    const { numRules = RULES_NUM, rulesModel = "rules" } = options || {}

    dbg(`generating ${numRules} output rules`)
    const instructions =
        options?.instructions?.outputRules ||
        files.frontmatter?.instructions?.outputRules ||
        ""

    outputWorkflowDiagram(DIAGRAM_GENERATE_OUTPUT_RULES, options)

    // generate rules
    const input_data = MD.content(files.prompt.content)
    const pn = PROMPT_GENERATE_OUTPUT_RULES
    await outputPrompty(pn, options)
    const res = await measure("gen.outputrules", () =>
        generator.runPrompt(
            (ctx) => {
                ctx.importTemplate(pn, {
                    num_rules: numRules,
                    input_data,
                    instructions,
                })
            },
            {
                ...modelOptions(rulesModel, options),
                //      logprobs: true,
                label: `${files.name}> generate rules`,
            }
        )
    )
    const rules = tidyRules(checkLLMResponse(res))
    return rules
}
