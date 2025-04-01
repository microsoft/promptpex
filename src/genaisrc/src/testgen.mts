import { TESTS_NUM, PROMPT_GENERATE_TESTS } from "./constants.mts"
import { outputWorkflowDiagram, outputPrompty } from "./output.mts"
import {
    parseAllRules,
    parseRulesTests,
    modelOptions,
    checkLLMResponse,
    isUnassistedResponse,
} from "./parsers.mts"
import { measure } from "./perf.mts"
import type {
    PromptPexContext,
    PromptPexOptions,
    PromptPexRule,
    PromptPexTest,
} from "./types.mts"
const dbg = host.logger("promptpex:gen:test")
const { generator, output } = env

export async function generateTests(
    files: PromptPexContext,
    options?: PromptPexOptions
): Promise<string> {
    const {
        testsPerRule: num = TESTS_NUM,
        rulesModel = "rules",
        testGenerations = 1,
    } = options || {}

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
    const pn = PROMPT_GENERATE_TESTS
    await outputPrompty(pn, options)

    const rulesGroups = splitRules(allRules, options)
    const tests: PromptPexTest[] = []
    let rulesCount = 0

    dbg(`${allRules.length} rules, ${rulesGroups.length} groups`)
    for (const rulesGroup of rulesGroups) {
        let testGeneration = 0
        let repaired = false
        await measure("gen.tests", () =>
            generator.runPrompt(
                (ctx) => {
                    ctx.importTemplate(pn, {
                        input_spec: files.inputSpec.content,
                        context,
                        num,
                        rule: rulesGroup
                            .map(
                                (r, index) =>
                                    `${rulesCount + index + 1}. ${r.rule}`
                            )
                            .join("\n"),
                        num_rules: rulesGroup.length,
                    })
                    ctx.defChatParticipant((p, c) => {
                        const last: string = c.at(-1)?.content
                        const csv = parseCsvTests(last)
                        if (!csv.length) {
                            if (!repaired) {
                                dbg(`no tests found, trying to repair`)
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
                        } else {
                            if (csv?.length) {
                                dbg(`adding ${csv.length} tests`)
                                tests.push(...csv)
                            }
                            if (testGeneration < testGenerations) {
                                testGeneration++
                                dbg(`test generation ${testGeneration + 1}`)
                                repaired = false
                                p.$`Generate ${num} more tests for the same rules. Do not duplicate the previous tests.`
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
        // TODO retry
        rulesCount += rulesGroup.length
    }
    const resc = JSON.stringify(tests, null, 2)
    return resc
}

function splitRules(rules: PromptPexRule[], options?: PromptPexOptions) {
    const { splitRules, maxRulesPerTestGeneration } = options || {}
    let res = splitRules
        ? [rules.filter((r) => !r.inverse), rules.filter((r) => r.inverse)]
        : [rules.slice(0)]
    if (maxRulesPerTestGeneration > 0)
        res = res.flatMap((r) => chunkArray(r, maxRulesPerTestGeneration))
    return res
}

function chunkArray<T>(array: T[], n: number): T[][] {
    const result: T[][] = []
    for (let i = 0; i < array.length; i += n) {
        result.push(array.slice(i, i + n))
    }
    return result
}

function parseCsvTests(text: string): PromptPexTest[] {
    if (!text) return []
    if (isUnassistedResponse(text)) return []
    const content = text.trim().replace(/\\"/g, '""')
    const rulesTests = content
        ? (CSV.parse(content, {
              delimiter: ",",
              repair: true,
          }) as PromptPexTest[])
        : []
    return rulesTests.map((r) => ({ ...r, testinput: r.testinput || "" }))
}
