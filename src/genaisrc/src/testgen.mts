import { TESTS_NUM, PROMPT_GENERATE_TESTS } from "./constants.mts"
import { outputWorkflowDiagram, outputPrompty } from "./output.mts"
import {
    parseAllRules,
    parseRulesTests,
    modelOptions,
    checkLLMResponse,
} from "./parsers.mts"
import { measure } from "./perf.mts"
import { PromptPexContext, PromptPexOptions } from "./types.mts"
const { generator, output } = env

export async function generateTests(
    files: PromptPexContext,
    options?: PromptPexOptions
) {
    const { testsPerRule: num = TESTS_NUM, rulesModel = "rules" } =
        options || {}

    if (!files.rules.content) throw new Error("No rules found")
    if (!files.inputSpec.content) throw new Error("No input spec found")
    const allRules = parseAllRules(files)
    if (!allRules) throw new Error("No rules found")

    outputWorkflowDiagram(
        `PUT(["Prompt Under Test (PUT)"])
IS["Input Specification (IS)"]
OR["Output Rules (OR)"]
IOR["Inverse Output Rules (IOR)"]
PPT["PromptPex Tests (PPT)"]

PUT --> IS

PUT --> OR
OR --> IOR

PUT --> PPT
IS --> PPT
OR --> PPT
IOR --> PPT        
`,
        options
    )

    const context = MD.content(files.prompt.content)
    let repaired = false
    const pn = PROMPT_GENERATE_TESTS
    await outputPrompty(pn, options)
    const res = await measure("llm.gen.tests", () =>
        generator.runPrompt(
            (ctx) => {
                ctx.importTemplate(pn, {
                    input_spec: files.inputSpec.content,
                    context,
                    num,
                    rule: allRules
                        .map((r, index) => `${index + 1}. ${r.rule}`)
                        .join("\n"),
                    num_rules: allRules.length,
                })
                ctx.defChatParticipant((p, c) => {
                    const last: string = c.at(-1)?.content
                    const csv = parseRulesTests(last)
                    if (!csv.length) {
                        if (!repaired) {
                            console.warn(
                                "Invalid generated test format or no test generated, trying to repair"
                            )
                            repaired = true
                            p.$`The generated tests are not valid CSV. Please fix formatting issues and try again.`
                        } else {
                            output.warn(
                                "Invalid generated test format, skipping repair."
                            )
                            output.fence(last, "txt")
                        }
                    }
                })
            },
            {
                ...modelOptions(rulesModel, options),
                //      logprobs: true,
                label: `${files.name}> generate tests`,
            }
        )
    )
    const text = checkLLMResponse(res)
    const csv = parsers.unfence(text, "csv")
    return csv
}
