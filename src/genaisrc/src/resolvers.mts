import type { PromptPexContext, PromptPexTest } from "./types.mts"
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

export function resolvePromptArgs(
    files: PromptPexContext,
    test: PromptPexTest
) {
    const inputs = files.inputs
    const inputKeys = Object.keys(inputs)
    const unresolved = new Set(inputKeys)
    const expectedOutput = test["expectedoutput"]
    const testInput = test["testinput"]
    const args: Record<string, any> = {}

    // apply defaults
    for (const [iname, ivalue] of Object.entries(inputs)) {
        if (unresolved.has(iname) && ivalue?.default) {
            dbg(`input %s has default value: %s`, iname, ivalue.default)
            args[iname] = ivalue.default
            unresolved.delete(iname)
        }
    }

    if (unresolved.size === 1) {
        dbg(`last unresolved input: ${unresolved[0]}`)
        args[unresolved[0]] = testInput
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
