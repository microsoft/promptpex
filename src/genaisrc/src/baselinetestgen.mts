import { PROMPT_GENERATE_BASELINE_TESTS } from "./constants.mts"
import { outputPrompty } from "./output.mts"
import {
    parseRulesTests,
    modelOptions,
    isUnassistedResponse,
    checkLLMResponse,
    cleanBaselineTests,
} from "./parsers.mts"
import { measure } from "./perf.mts"
import type { PromptPexContext, PromptPexOptions } from "./types.mts"
const { generator } = env
const dbg = host.logger("promptpex:gen:baseline")

export async function generateBaselineTests(
    files: PromptPexContext,
    options?: PromptPexOptions & { num?: number }
): Promise<void> {
    const { baselineModel = "baseline" } = options || {}
    const tests = parseRulesTests(files.tests.content)
    if (!tests?.length)
        throw new Error("No tests found to generate baseline tests")
    const { num = tests.length } = options || {}
    if (!num) throw new Error("Number of baseline tests must be positive")
    const context = MD.content(files.prompt.content)
    const pn = PROMPT_GENERATE_BASELINE_TESTS
    await outputPrompty(pn, options)
    const res = await measure("gen.baseline", () =>
        generator.runPrompt(
            (ctx) => {
                ctx.importTemplate(pn, {
                    num,
                    prompt: context,
                })
            },
            {
                ...modelOptions(baselineModel, options),
                //      logprobs: true,
                label: `${files.name}> generate baseline tests`,
            }
        )
    )

    if (isUnassistedResponse(res.text)) {
        dbg(`unassisted response: ${res.text}`)
        return
    }
    checkLLMResponse(res)
    
    // Parse baseline tests from the text response
    const cleanedBaselineInputs = cleanBaselineTests(res.text)
    dbg(`cleaned baseline tests: %O`, cleanedBaselineInputs)
    
    // Convert to the same JSON format as regular tests
    const baselineTests = cleanedBaselineInputs.map((testinput, index) => ({
        ruleid: undefined, // baseline tests don't have rules
        testid: undefined, // baseline tests don't have testid
        expectedoutput: undefined, // baseline tests don't have expected outputs
        reasoning: undefined, // baseline tests don't have reasoning
        testinput: testinput,
        scenario: "",
        generation: 0,
        testuid: `baseline-test-${Math.random().toString(36).substr(2, 9)}`,
        baseline: true
    }))
    
    // Merge with existing tests
    const existingTests = files.promptPexTests || []
    // Ensure existing tests have baseline: false if they don't have a baseline field
    const regularTests = existingTests.map(test => ({
        ...test,
        baseline: test.baseline !== undefined ? test.baseline : false
    }))
    const allTests = [...regularTests, ...baselineTests]
    
    // Update the files with merged tests
    files.promptPexTests = allTests
    files.tests.content = JSON.stringify(allTests, null, 2)
    
    // Keep the old baseline_tests.txt format for compatibility, but also write to regular tests.json
    const txt = cleanedBaselineInputs.join("\n===\n")
    files.baselineTests.content = txt
    
    if (files.writeResults) {
        await workspace.writeFiles(files.tests) // Write to tests.json
        await workspace.writeFiles(files.baselineTests) // Keep baseline_tests.txt for compatibility
    }
}
