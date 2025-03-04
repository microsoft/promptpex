import { modelOptions, parseOKERR, parseBaselineTests } from "./parsers.mts"
import type { PromptPexContext, PromptPexOptions } from "./types.mts"

const { generator } = env

export async function evaluateBaselineTests(
    files: PromptPexContext,
    options?: PromptPexOptions & { model?: ModelType; force?: boolean }
) {
    const { model } = options || {}
    const moptions = {
        ...modelOptions(model, options),
    }
    const inputSpec = files.inputSpec.content
    const baselineTests = parseBaselineTests(files)

    const results = []
    for (const baselineTest of baselineTests) {
        const { testinput, ...rest } = baselineTest
        const resValidity = await generator.runPrompt(
            (ctx) => {
                ctx.importTemplate(
                    "src/prompts/check_violation_with_input_spec.prompty",
                    {
                        input_spec: inputSpec,
                        test: testinput,
                    }
                )
            },
            {
                ...moptions,
                choices: ["OK", "ERR"],
                label: `${files.name}> evaluate validity of baseline test ${baselineTest.testinput.slice(0, 42)}...`,
            }
        )
        const valid = parseOKERR(resValidity.text)
        results.push({
            input: testinput,
            validity: valid,
            validityText: resValidity.text,
            ...rest,
        })
    }
    return JSON.stringify(results, null, 2)
}
