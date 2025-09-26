import {
    TESTS_NUM,
    PROMPT_GENERATE_TESTS,
    DIAGRAM_GENERATE_TESTS,
    GENERATION_SYMBOL,
    SCENARIO_SYMBOL,
    RULE_SYMBOL,
    MODEL_ALIAS_RULES,
} from "./constants.mts"

// Fraction of tests that should be generated from inverse rules
const FRACTION_INVERSE = 0.5
import { outputWorkflowDiagram, outputPrompty } from "./output.mts"
import {
    parseAllRules,
    modelOptions,
    isUnassistedResponse,
} from "./parsers.mts"
import { measure } from "./perf.mts"
import { resolveScenarios } from "./resolvers.mts"
import { convertToTestData } from "./testdata.mts"
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
): Promise<void> {
    const {
        testsPerRule: num = TESTS_NUM,
        rulesModel = MODEL_ALIAS_RULES,
        testGenerations = 1,
    } = options || {}

    if (!files.rules.content) throw new Error("No rules found")
    if (!files.inputSpec.content) throw new Error("No input spec found")
    if (files.tests.content) {
        dbg(`tests already exist for %s, skipping generation`, files.name)
        return
    }

    const allRules = parseAllRules(files, options)
    dbg(`rules: ${allRules.length}`)
    if (!allRules) throw new Error("No rules found")

    outputWorkflowDiagram(DIAGRAM_GENERATE_TESTS, options)

    const scenarios = resolveScenarios(files)
    dbg(`scenarios: %d`, scenarios.length)
    const context = MD.content(files.prompt.content)
    const pn = PROMPT_GENERATE_TESTS
    // TODO: parameterize how many and which test samples to use
    const testSamples = files.testSamples
    const test_samples = testSamples?.length ? YAML.stringify(testSamples) : ""
    dbg(`test samples: %d`, test_samples)

    await outputPrompty(pn, options)

    const rulesGroups = splitRules(allRules, options)
    const tests: PromptPexTest[] = []

    const checkpoint = async () => {
        dbg(`saving ${tests.length} tests`)
        const resc = JSON.stringify(tests, null, 2)
        files.promptPexTests = tests
        files.tests.content = resc
        if (files.writeResults) await workspace.writeFiles(files.tests)
        await convertToTestData(files, tests)
    }

    dbg(`rule groups: ${rulesGroups.length}`)
    const inverseGroups = rulesGroups.filter(g => g.length > 0 && g[0].inverse).length
    const regularGroups = rulesGroups.length - inverseGroups
    const totalRulesInGroups = rulesGroups.reduce((sum, g) => sum + g.length, 0)
    const regularRulesInGroups = rulesGroups.filter(g => g.length > 0 && !g[0].inverse).reduce((sum, g) => sum + g.length, 0)
    const inverseRulesInGroups = totalRulesInGroups - regularRulesInGroups
    
    dbg(`rule group distribution: ${regularGroups} regular groups (${regularRulesInGroups} rules), ${inverseGroups} inverse groups (${inverseRulesInGroups} rules)`)
    dbg(`expected test distribution: ~${Math.round((regularRulesInGroups / totalRulesInGroups) * 100)}% regular, ~${Math.round((inverseRulesInGroups / totalRulesInGroups) * 100)}% inverse (target: ${Math.round((1-FRACTION_INVERSE) * 100)}% regular, ${Math.round(FRACTION_INVERSE * 100)}% inverse)`)
    for (let si = 0; si < scenarios.length; si++) {
        const scenario = scenarios[si]
        const { instructions, parameters = {} } = scenario

        dbg(`scenario: ${scenario.name}`)
        let rulesCount = 0
        for (let ri = 0; ri < rulesGroups.length; ri++) {
            const rulesGroup = rulesGroups[ri]
            let testGeneration = 0
            let repaired = false
            // Check if this group contains inverse rules
            const isInverseGroup = rulesGroup.length > 0 && rulesGroup[0].inverse
            const rule = rulesGroup
                .map((r, index) => `${rulesCount + index + 1}. ${r.rule}`)
                .join("\n")
            dbg(`rule group ${ri + 1}/${rulesGroups.length}: ${rulesGroup.length} rules, inverse: ${isInverseGroup}`)
            dbg(`rules: ${rule}`)
            const scenarioInstructions = [
                instructions,
                ...Object.entries(parameters).map(
                    ([k, v]) => `'{{${k}}}' = ${v}`
                ),
            ]
                .filter((l) => !!l)
                .map((l) => `- ${l}`)
                .join("\n")

            const args = Object.fromEntries(
                Object.entries(files.inputs).filter(([k]) => !parameters[k])
            )
            dbg(`open args: %O`, args)

            const argNames = Object.keys(args)
            const testinput_names = argNames.join(", ")
            const testinput_descriptions = Object.entries(args)
                .map(
                    ([k, v]) =>
                        `- "${k}": ${v.type} = ${v.description || `Detailed input '${k}' provided to the software.`}`
                )
                .join("\n")
            const testinput_example_1 = argNames
                .map((name) => `input '${name}' for rule 1 scenario 1`)
                .join(",")
            const testinput_example_2 = argNames
                .map((name) => `input '${name}' for rule 1 scenario 2`)
                .join(",")
            const testinput_count = argNames.length

            dbg(`testinput: %O`, {
                testinput_names,
                testinput_descriptions,
                testinput_example_1,
                testinput_example_2,
                testinput_count,
            })

            dbg(`generating ${num} tests for ${rulesGroup.length} rules (${num * testGenerations} total per group across ${testGenerations} generations)`)

            await measure("gen.tests", () =>
                generator.runPrompt(
                    (ctx) => {
                        ctx.importTemplate(pn, {
                            input_spec: files.inputSpec.content,
                            context,
                            num,
                            scenario: scenarioInstructions,
                            rule,
                            num_rules: rulesGroup.length,
                            testinput_descriptions,
                            testinput_names,
                            testinput_example_1,
                            testinput_example_2,
                            testinput_count,
                            test_samples,
                        })
                        ctx.defChatParticipant((p, c) => {
                            const last: string = c.at(-1)?.content as string
                            dbg(`last message: %s`, last)
                            if (typeof last !== "string")
                                throw new Error("Invalid last message")
                            const csv = parseCsvTests(last, Object.keys(args))
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
                                    tests.push(
                                        ...csv.map((t) => ({
                                            ...t,
                                            scenario: scenario.name,
                                            generation: testGeneration,
                                            baseline: false,
                                            inverse: isInverseGroup,
                                        }))
                                    )
                                }
                                testGeneration++
                                if (testGeneration < testGenerations) {
                                    dbg(
                                        `next test generation ${testGeneration}`
                                    )
                                    repaired = false
                                    p.$`Generate ${num} more tests for the same rules. Do not duplicate the previous tests.`
                                }
                            }
                        })
                    },
                    {
                        ...modelOptions(rulesModel, options),
                        label: `${files.name}> generate tests (${SCENARIO_SYMBOL} ${scenario.name} ${si + 1}/${scenarios.length}, ${RULE_SYMBOL} ${ri + 1}/${rulesGroups.length}, ${GENERATION_SYMBOL} ${testGeneration + 1}/${testGenerations})`,
                    }
                )
            )
            await checkpoint()
            // TODO retry
            rulesCount += rulesGroup.length
        }
    }

    await checkpoint()
    
    // Final summary of test distribution
    const totalTests = tests.length
    const inverseTests = tests.filter(t => t.inverse).length
    const regularTests = totalTests - inverseTests
    const actualInverseFraction = totalTests > 0 ? inverseTests / totalTests : 0
    
    dbg(`Final test distribution: ${regularTests} regular, ${inverseTests} inverse (${Math.round(actualInverseFraction * 100)}% inverse, target: ${Math.round(FRACTION_INVERSE * 100)}%)`)
}

function splitRules(rules: PromptPexRule[], options?: PromptPexOptions) {
    const { splitRules, maxRulesPerTestGeneration = 5 } = options || {}
    
    if (!splitRules) {
        // If not splitting rules, still need to respect the fraction
        // Create a mixed group with proper distribution
        const regularRules = rules.filter((r) => !r.inverse)
        const inverseRules = rules.filter((r) => r.inverse)
        
        const totalRules = regularRules.length + inverseRules.length
        const targetInverseCount = Math.round(totalRules * FRACTION_INVERSE)
        const targetRegularCount = totalRules - targetInverseCount
        
        const selectedRules: PromptPexRule[] = []
        
        // Add rules to achieve the target distribution
        for (let i = 0; i < Math.min(targetRegularCount, regularRules.length); i++) {
            selectedRules.push(regularRules[i])
        }
        for (let i = 0; i < Math.min(targetInverseCount, inverseRules.length); i++) {
            selectedRules.push(inverseRules[i])
        }
        
        let res = [selectedRules]
        if (maxRulesPerTestGeneration > 0 && selectedRules.length > maxRulesPerTestGeneration)
            res = chunkArray(selectedRules, maxRulesPerTestGeneration)
        return res
    }
    
    // Split rules based on inverse property and desired fraction
    const regularRules = rules.filter((r) => !r.inverse)
    const inverseRules = rules.filter((r) => r.inverse)
    
    dbg(`splitRules: regular=${regularRules.length}, inverse=${inverseRules.length}, maxPerGroup=${maxRulesPerTestGeneration}`)
    
    let res: PromptPexRule[][] = []
    
    // Create efficient groups that respect both maxRulesPerTestGeneration and fraction balance
    if (maxRulesPerTestGeneration > 0) {
        // Calculate target number of groups for each type based on rules and group size
        const regularGroups = Math.ceil(regularRules.length / maxRulesPerTestGeneration)
        const inverseGroups = Math.ceil(inverseRules.length / maxRulesPerTestGeneration)
        const totalGroups = regularGroups + inverseGroups
        
        // Calculate how many groups should be inverse to achieve target fraction
        const targetInverseGroupRatio = totalGroups > 0 ? FRACTION_INVERSE : 0
        const targetInverseGroups = Math.round(totalGroups * targetInverseGroupRatio)
        const targetRegularGroups = totalGroups - targetInverseGroups
        
        dbg(`target group distribution: ${targetRegularGroups} regular groups, ${targetInverseGroups} inverse groups`)
        
        // Create regular rule groups
        const actualRegularGroups = Math.min(targetRegularGroups, regularGroups)
        const regularChunks = chunkArray(regularRules, maxRulesPerTestGeneration)
        for (let i = 0; i < actualRegularGroups && i < regularChunks.length; i++) {
            res.push(regularChunks[i])
        }
        
        // Create inverse rule groups
        const actualInverseGroups = Math.min(targetInverseGroups, inverseGroups)
        const inverseChunks = chunkArray(inverseRules, maxRulesPerTestGeneration)
        for (let i = 0; i < actualInverseGroups && i < inverseChunks.length; i++) {
            res.push(inverseChunks[i])
        }
        
        // If we have remaining slots and available rules, fill them
        const remainingRegularChunks = regularChunks.slice(actualRegularGroups)
        const remainingInverseChunks = inverseChunks.slice(actualInverseGroups)
        
        // Add remaining chunks alternating between types to maintain balance
        let regularIndex = 0
        let inverseIndex = 0
        while (regularIndex < remainingRegularChunks.length || inverseIndex < remainingInverseChunks.length) {
            if (regularIndex < remainingRegularChunks.length) {
                res.push(remainingRegularChunks[regularIndex++])
            }
            if (inverseIndex < remainingInverseChunks.length) {
                res.push(remainingInverseChunks[inverseIndex++])
            }
        }
    } else {
        // If maxRulesPerTestGeneration is not set, create two large groups
        if (regularRules.length > 0) res.push(regularRules)
        if (inverseRules.length > 0) res.push(inverseRules)
    }
    
    const actualRegularGroups = res.filter(g => g.length > 0 && !g[0].inverse).length
    const actualInverseGroups = res.filter(g => g.length > 0 && g[0].inverse).length
    dbg(`created ${actualRegularGroups} regular groups, ${actualInverseGroups} inverse groups`)
    
    return res
}

function chunkArray<T>(array: T[], n: number): T[][] {
    const result: T[][] = []
    for (let i = 0; i < array.length; i += n) {
        result.push(array.slice(i, i + n))
    }
    return result
}

function parseCsvTests(
    text: string,
    testInputNames: string[]
): PromptPexTest[] {
    if (!text) return []

    const content = parsers.unfence(text.trim().replace(/\\"/g, '""'), "csv")
    const rulesTests = content
        ? (parsers.CSV(content, {
              delimiter: ",",
              repair: true,
          }) as PromptPexTest[])
        : []
    const res = rulesTests
        .map((r) => {
            const testinput: Record<string, string> = {}
            for (const testInputName of testInputNames) {
                const v = r[testInputName]
                if (v === undefined) {
                    dbg(`testinput %s not found`, testInputName)
                    return undefined // skip test if not found?
                }
                testinput[testInputName] = v
            }
            return {
                ...r,
                testinput:
                    testInputNames.length > 1
                        ? JSON.stringify(testinput)
                        : testinput[testInputNames[0]],
            }
        })
        .filter((t) => !!t)
    if (!res.length)
        output.detailsFenced(`tests - unable to parse`, text, "text")
    return res
}
