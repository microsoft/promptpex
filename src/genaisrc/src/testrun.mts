import { evaluateCustomTestResult } from "./customtestresulteval.mts"
import { resolveTestPath } from "./filecache.mts"
import {
    modelOptions,
    parseAllRules,
    parseBaselineTests,
    parseOKERR,
    parseRulesTests,
} from "./parsers.mts"
import { measure } from "./perf.mts"
import { resolvePromptArgs, resolveRule } from "./resolvers.mts"
import { evaluateTestResult } from "./testresulteval.mts"
import type {
    PromptPexContext,
    PromptPexOptions,
    PromptPexTest,
    PromptPexTestResult,
} from "./types.mts"
import assert from "node:assert/strict"

const { generator, output } = env

export async function runTests(
    files: PromptPexContext,
    options?: PromptPexOptions & {
        models?: ModelType[]
        force?: boolean
        compliance?: boolean
        q?: PromiseQueue
        maxTests?: number
        ignoreBaseline?: boolean
    }
): Promise<string> {
    const {
        force,
        models = [],
        compliance,
        maxTests,
        ignoreBaseline,
        runsPerTest = 1,
    } = options || {}
    console.debug({ models })
    assert(models.every((m) => !!m))
    const rulesTests = parseRulesTests(files.tests.content)
    const baselineTests = ignoreBaseline ? [] : parseBaselineTests(files)
    const tests = [...rulesTests, ...baselineTests].slice(0, maxTests)
    if (!tests?.length) throw new Error("No tests found to run")

    console.log(
        `running ${tests.length} tests (x ${runsPerTest}) with ${models.length} models`
    )
    const testResults: PromptPexTestResult[] = []
    for (const model of models) {
        for (let testi = 0; testi < tests.length; ++testi) {
            const test = tests[testi]
            console.log(
                `${files.name}> ${model}: run test ${testi + 1}/${tests.length}x${runsPerTest} ${test.testinput.slice(0, 42)}...`
            )
            for (let ri = 0; ri < runsPerTest; ++ri) {
                const testRes = await runTest(files, test, {
                    ...options,
                    model,
                    force,
                    compliance,
                })
                assert(testRes.model)
                if (testRes) testResults.push(testRes)
            }
        }
    }

    return JSON.stringify(testResults, null, 2)
}

function updateTestResultCompliant(testRes: PromptPexTestResult) {
    testRes.compliance = parseOKERR(testRes.complianceText)
}

export async function runTest(
    files: PromptPexContext,
    test: PromptPexTest,
    options?: PromptPexOptions & {
        model?: ModelType
        compliance?: boolean
        force?: boolean
    }
): Promise<PromptPexTestResult> {
    const {
        model,
        force,
        compliance,
        customTestEvalModel,
        customTestEvalTemplate,
        evalCache,
    } = options || {}
    const moptions = {
        ...modelOptions(model, options),
    }
    const { id, promptid, file } = await resolveTestPath(files, test, {
        model,
        evalCache,
    })
    if (file?.content && !force) {
        const res = parsers.JSON5(file) as PromptPexTestResult
        if (res && !res.error && res.complianceText) {
            if (!res.model)
                output.warn(
                    `invalid test result ${file.filename}, missing model field`
                )
            updateTestResultCompliant(res)
            res.baseline = test.baseline
            return res
        }
    }
    const { inputs, args, testInput } = resolvePromptArgs(files, test)
    const allRules = parseAllRules(files)
    const rule = resolveRule(allRules, test)
    if (!args)
        return {
            id,
            promptid,
            ...rule,
            baseline: test.baseline,
            model: "",
            error: "invalid test input",
            input: testInput,
            output: "invalid test input",
        } satisfies PromptPexTestResult

    const res = await measure("llm.test.run", () =>
        generator.runPrompt(
            (ctx) => {
                ctx.importTemplate(files.prompt, args, {
                    allowExtraArguments: true,
                })
                if (!Object.keys(inputs || {}).length) ctx.writeText(testInput)
            },
            {
                ...moptions,
                label: `${files.name}> run test ${testInput.slice(0, 42)}...`,
            }
        )
    )
    if (res.error) {
        console.debug(res.finishReason)
        console.debug(JSON.stringify(res.error, null, 2))
        throw new Error(res.error.message)
    }
    const actualOutput = res.text
    output.detailsFenced(
        `test result: ${testInput.slice(0, 42)}}...`,
        testInput + "\n\n---\n\n" + actualOutput
    )

    const testRes: PromptPexTestResult = {
        id,
        promptid,
        ...rule,
        baseline: test.baseline,
        model: res.model,
        error: res.error?.message,
        input: testInput,
        output: actualOutput,
    } satisfies PromptPexTestResult

    if (compliance) {
        testRes.compliance = undefined
        testRes.complianceText = await evaluateTestResult(
            files,
            testRes,
            options
        )
        updateTestResultCompliant(testRes)
    }

    if (customTestEvalTemplate) {
        const customTestEval = await evaluateCustomTestResult(
            files,
            testRes,
            options
        )
        testRes.customEvalText = customTestEval
    }

    if (file)
        await workspace.writeText(
            file.filename,
            JSON.stringify(testRes, null, 2)
        )
    return testRes
}
