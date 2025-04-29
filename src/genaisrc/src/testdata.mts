import { TEST_DATA_LENGTH } from "./constants.mts"
import { resolvePromptArgs } from "./resolvers.mts"
import type { PromptPexContext, PromptPexTest } from "./types.mts"

function splitArray<T>(array: T[], n: number): [T[], T[]] {
    if (n <= 0 || array.length === 0) {
        return [[], array.slice(0)]
    }
    const shuffled = array.slice(0).sort(() => Math.random() - 0.5)
    const nm = Math.min(n, array.length)
    const test = shuffled.slice(0, nm)
    return [test, shuffled.slice(test.length)]
}

export async function convertToTestData(
    files: PromptPexContext,
    tests: PromptPexTest[]
) {
    const inputSpec = files.inputSpec.content
    const rules = files.rules.content
    const intent = files.intent.content

    const testData = tests.map((testResult) => ({
        input: {
            parameters: JSON.stringify({
                ...resolvePromptArgs(files, testResult).args,
                rules,
                inputSpec,
                intent,
            }),
        },
        output: [],
    }))
    const testDataRaw = tests.map(
        (testResult) => resolvePromptArgs(files, testResult).args
    )
    const testDataDataRaw = { data: testDataRaw }
    files.testData.content = JSON.stringify(testData, null, 2)
    if (files.writeResults) {
        await workspace.writeFiles(files.testData)
        const [head, tail] = splitArray(testData, TEST_DATA_LENGTH)
        await workspace.writeText(
            path.changeext(files.testData.filename, ".head.json"),
            JSON.stringify(head, null, 2)
        )
        await workspace.writeText(
            path.changeext(files.testData.filename, ".tail.json"),
            JSON.stringify(tail, null, 2)
        )
        await workspace.writeText(
            path.changeext(files.testData.filename, ".raw.json"),
            JSON.stringify(testDataRaw, null, 2)
        )
        await workspace.writeText(
            path.changeext(files.testData.filename, ".training.json"),
            JSON.stringify(testDataDataRaw, null, 2)
        )
    }
}
