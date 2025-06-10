import { TEMPLATE_VARIABLE_RX } from "./constants.mts"
import type {
    PromptPexContext,
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
    const { inputs } = files
    const {
        testinput,
        expectedoutput,
        scenario,
        groundtruth,
        groundtruthModel,
    } = test

    const inputKeys = Object.keys(inputs)
    const unresolved = new Set(inputKeys)
    dbg(`unresolved inputs: %s`, inputKeys)
    const args: Record<string, any> = {}

    // apply scenario values
    if (scenario) {
        const scenarios = resolveScenarios(files)
        const scenarioInstance = scenarios.find((s) => s.name === scenario)
        if (!scenarioInstance) throw new Error(`Scenario ${scenario} not found`)
        for (const [iname, ivalue] of Object.entries(
            scenarioInstance.parameters || {}
        )) {
            if (unresolved.has(iname) && ivalue !== undefined) {
                dbg(`input %s scenario: %s`, iname, ivalue)
                args[iname] = ivalue
                unresolved.delete(iname)
            }
        }
    }

    // apply defaults
    for (const [iname, ivalue] of Object.entries(inputs)) {
        if (unresolved.has(iname) && ivalue?.default !== undefined) {
            dbg(`input %s default: %s`, iname, ivalue.default)
            args[iname] = ivalue.default
            unresolved.delete(iname)
        }
    }

    // fill last whole with generated input
    dbg(`remaining unresolved inputs: %s`, Array.from(unresolved))
    const parsedInputs = parsers.JSON5(testinput)
    if (unresolved.size === 1) {
        const key = Array.from(unresolved)[0]
        const val = parsedInputs?.[key] ?? testinput
        dbg(`input %s <- %s`, key, val)
        args[key] = val
    } else if (unresolved.size > 1) {
        dbg(`parsed inputs: %O`, parsedInputs)
        if (typeof parsedInputs !== "object") {
            dbg(`invalid test input format: %o`, testinput)
            throw new Error(
                `Invalid test input format, expected JSON object: ${testinput}`
            )
        }
        Object.assign(args, parsedInputs)
    } else if (unresolved.size === 0 && inputKeys.length > 0) {
        dbg(
            `all inputs prefilled, replacing first (%s) with test input`,
            inputKeys[0]
        )
        args[inputKeys[0]] = testinput
    }
    return {
        inputs,
        args,
        testInput: testinput,
        expectedOutput: expectedoutput,
        groundtruth,
        groundtruthModel,
    }
}

export async function resolveRuleHash(files: PromptPexContext, rule: string) {
    const content = MD.content(files.prompt.content)
    const ruleId = await parsers.hash(content + rule, {
        length: 7,
    })
    return ruleId
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

export function fillTemplateVariables(
    content: string,
    options: {
        variables: Record<string, string>
        idResolver: (id: string) => string
    }
) {
    return content.replace(TEMPLATE_VARIABLE_RX, (_, id) => {
        const variable = options.variables?.[id]
        if (variable) {
            dbg(`inline ${id}`)
            return variable
        }
        return options.idResolver?.(id) ?? _
    })
}
