import {
    RULES_NUM,
    PROMPT_GENERATE_OUTPUT_RULES,
    DIAGRAM_GENERATE_OUTPUT_RULES,
    MODEL_ALIAS_RULES,
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
): Promise<void> {
    const { numRules = RULES_NUM, rulesModel = MODEL_ALIAS_RULES } =
        options || {}

    dbg(`generating %d output rules`, numRules)
    const instructions =
        options?.instructions?.outputRules ||
        files.frontmatter?.instructions?.outputRules ||
        ""

    outputWorkflowDiagram(DIAGRAM_GENERATE_OUTPUT_RULES, options)
    const pn = PROMPT_GENERATE_OUTPUT_RULES
    await outputPrompty(pn, options)

    if (files.rules.content) {
        dbg(`rules already exist for %s, skipping generation`, files.name)
        return
    }

    // generate rules
    const input_data = MD.content(files.prompt.content)
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
    files.rules.content = rules
    if (files.writeResults) await workspace.writeFiles(files.rules)
}
