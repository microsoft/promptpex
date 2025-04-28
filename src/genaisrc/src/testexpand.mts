import { PROMPT_EXPAND_TEST } from "./constants.mts"
import { modelOptions, parseAllRules } from "./parsers.mts"
import { measure } from "./perf.mts"
import { resolvePromptArgs, resolveRule } from "./resolvers.mts"
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
    options: PromptPexOptions
) {
    const { testExpansions } = options
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
        const { args } = resolvePromptArgs(files, test)
        const testInputs = Object.keys(args)
        const responseSchema = testInputs.length
            ? {
                  type: "object",
                  properties: Object.fromEntries(
                      testInputs.map((k) => [k, { type: "string" }])
                  ),
                  required: testInputs.slice(0),
              }
            : undefined
        test.testinputOriginal = test.testinput
        for (let ti = 0; ti < testExpansions; ti++) {
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
                        responseSchema,
                        responseType: responseSchema ? "json_schema" : "text",
                        cache: "promptpex",
                        label: `expanding test case ${i + 1}/${ruleTests.length} #${ti}`,
                    }
                )
            )

            if (res.error) {
                dbg(`expansion error: %s`, res.error)
                continue
            }
            if (!res.json) {
                dbg(`expansion response is not json: %s`, res.text)
                continue
            }
            dbg(`expansion:\n%s\n->\n%s`, test.testinput, res.text)
            test.testinput = res.text
            // recompute?
            // delete test.expectedoutput
            await checkpoint()
        }
    }
    await checkpoint()
}
