import { PROMPT_EXPAND_TEST } from "./constants.mts"
import {
    modelOptions,
    parseAllRules,
    parseRules,
    parseRulesTests,
} from "./parsers.mts"
import { measure } from "./perf.mts"
import { resolveRule } from "./resolvers.mts"
import { convertToTestData } from "./testdata.mts"
import type {
    PromptPexContext,
    PromptPexOptions,
    PromptPexTest,
} from "./types.mts"

const { generator } = env
const dbg = host.logger("promptpex:gen:expand")

export async function expandTests(
    files: PromptPexContext,
    ruleTests: PromptPexTest[],
    options?: PromptPexOptions
) {
    const allRules = parseAllRules(files)
    const testSamples = files.testSamples
    const examples = testSamples?.length ? YAML.stringify(testSamples) : ""

    const checkpoint = async () => {
        dbg(`saving ${ruleTests.length} tests`)
        const resc = JSON.stringify(ruleTests, null, 2)
        files.tests.content = resc
        if (files.writeResults) await workspace.writeFiles(files.tests)
        await convertToTestData(files, ruleTests)
    }

    for (let i = 0; i < ruleTests.length; i++) {
        const test = ruleTests[i]
        const targetRule = resolveRule(allRules, test)
        if (!targetRule) {
            dbg(`no target rule for test %O`, test)
            continue
        }
        const res = await measure("expand.test", () =>
            generator.runPrompt(
                (ctx) => {
                    ctx.importTemplate(PROMPT_EXPAND_TEST, {
                        intent: files.intent.content,
                        rules: files.rules.content,
                        targetRule: targetRule?.rule,
                        examples,
                        test: test.testinput,
                    })
                },
                {
                    ...modelOptions("rules", options),
                    cache: "promptpex",
                    label: `expanding test case ${i + 1}/${ruleTests.length}`,
                }
            )
        )

        if (!res.error) {
            dbg(`expansion:\n%s\n->\n%s`, test.testinput, res.text)
            test.testinputOriginal = test.testinput
            test.testinput = res.text
            // recompute?
            // delete test.expectedoutput
            await checkpoint()
        }
    }
    await checkpoint()
}
