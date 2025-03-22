import { modelOptions, checkLLMResponse } from "./parsers.mts"
import { measure } from "./perf.mts"
import {
    PromptPexContext,
    PromptPexTestResult,
    PromptPexOptions,
} from "./types.mts"
const { generator } = env

export async function evaluateCustomTestResult(
    files: PromptPexContext,
    testResult: PromptPexTestResult,
    options: PromptPexOptions
): Promise<string> {
    const { customTestEvalTemplate, customTestEvalModel = "usereval" } =
        options || {}
    if (!customTestEvalTemplate) throw new Error("No custom test eval template")
    const moptions = modelOptions(customTestEvalModel, options)

    const content = MD.content(files.prompt.content)
    const res = await measure("eval.user", () =>
        generator.runPrompt(
            (ctx) => {
                // removes frontmatter
                ctx.importTemplate(
                    {
                        filename: "custom.prompt",
                        content: customTestEvalTemplate,
                    },
                    {
                        prompt: content.replace(/^(system|user):/gm, ""),
                        input: testResult.input,
                        output: testResult.output,
                    },
                    { allowExtraArguments: true }
                )
            },
            {
                ...moptions,
                label: `${files.name}> evaluate custom test result ${testResult.model} ${testResult.input.slice(0, 42)}...`,
            }
        )
    )
    const evaluation = checkLLMResponse(res)
    return evaluation
}
