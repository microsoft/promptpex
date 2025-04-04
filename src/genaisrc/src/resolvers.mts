import type {
    PromptPexContext,
    PromptPexPromptyFrontmatter,
    PromptPexTest,
    PromptPexTestGenerationScenario,
} from "./types.mts"
const dbg = host.logger("promptpex:resolvers")

export async function resolveTestId(
    files: PromptPexContext,
    test: PromptPexTest
) {
    const content = MD.content(files.prompt.content)
    const testid = await parsers.hash(
        content + test.testinput + (test.baseline ? ";baseline" : ""),
        {
            length: 7,
        }
    )
    return testid
}

export function resolveScenarios(
    files: PromptPexContext
): PromptPexTestGenerationScenario[] {
    return (
        files.frontmatter?.scenarios || [
            {
                name: "",
                instructions: "",
                parameters: {},
            } satisfies PromptPexTestGenerationScenario,
        ]
    )
}

export function resolvePromptArgs(
    files: PromptPexContext,
    test: PromptPexTest
) {
    const inputs = files.inputs
    const inputKeys = Object.keys(inputs)
    const unresolved = new Set(inputKeys)
    dbg(`unresolved inputs: %s`, inputKeys)
    const expectedOutput = test["expectedoutput"]
    const testInput = test["testinput"]
    const args: Record<string, any> = {}

    // apply defaults
    for (const [iname, ivalue] of Object.entries(inputs)) {
        if (unresolved.has(iname) && ivalue?.default) {
            dbg(`input %s default: %s`, iname, ivalue.default)
            args[iname] = ivalue.default
            unresolved.delete(iname)
        }
    }

    // apply scenario values
    if (test.scenario) {
        const scenarios = resolveScenarios(files)
        const scenario = scenarios.find((s) => s.name === test.scenario)
        if (!scenario) throw new Error(`Scenario ${test.scenario} not found`)
        for (const [iname, ivalue] of Object.entries(
            scenario.parameters || {}
        )) {
            if (unresolved.has(iname) && ivalue !== undefined) {
                dbg(`input %s scenario: %s`, iname, ivalue)
                args[iname] = ivalue
                unresolved.delete(iname)
            }
        }
    }

    // fill last whole with generated input
    dbg(`remaining unresolved inputs: %s`, unresolved)
    if (unresolved.size === 1) {
        const key = Array.from(unresolved)[0]
        dbg(`input %s <- %s`, key, testInput)
        args[key] = testInput
    } else if (unresolved.size > 1) {
        // not supported yet
        dbg(`multiple unspecified inputs not supported: %O`, {
            inputKeys,
            unresolved,
            testInput,
        })
        throw new Error("multiple unspecified inputs not supported yet")
    } else if (unresolved.size === 0 && inputKeys.length > 0) {
        dbg(
            `all inputs prefilled, replacing first (%s) with test input`,
            inputKeys[0]
        )
        args[inputKeys[0]] = testInput
    }
    return { inputs, args, testInput, expectedOutput }
}

export async function resolveRuleHash(files: PromptPexContext, rule: string) {
    const content = MD.content(files.prompt.content)
    const ruleid = await parsers.hash(content + rule, {
        length: 7,
    })
    return ruleid
}

export function resolveRule(
    rules: { rule: string; inverse?: boolean }[],
    test: PromptPexTest
) {
    const index = test.ruleid - 1
    const rule = rules[index]
    return { ruleid: index + 1, ...rule }
}

export async function resolvePromptId(files: PromptPexContext) {
    const content = MD.content(files.prompt.content)
    return parsers.hash(content, { length: 7 })
}
