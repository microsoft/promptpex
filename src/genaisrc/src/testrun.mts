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
const dbg = host.logger("promptpex:eval:run")

const { generator, output } = env

export async function runTests(
    files: PromptPexContext,
    options?: PromptPexOptions
): Promise<string> {
    const { modelsUnderTest, maxTestsToRun, runsPerTest = 1 } = options || {}
    if (!modelsUnderTest?.length) throw new Error("No models to run tests on")

    const rulesTests = parseRulesTests(files.tests.content)
    dbg(`found ${rulesTests.length} tests`)
    const baselineTests = options?.baselineTests

        ? parseBaselineTests(files)
        : []

    dbg(`found ${baselineTests.length} tests`)      
const tests = [...rulesTests, ...baselineTests].slice(0, maxTestsToRun)

    dbg(
        `running ${tests.length} tests (x ${runsPerTest}) with ${modelsUnderTest.length} models`
    )
    if (!tests?.length) throw new Error("No tests found to run")

    console.log(
        `running ${tests.length} tests (x ${runsPerTest}) with ${modelsUnderTest.length} models`
    )
    const testResults: PromptPexTestResult[] = []
    for (const modelUnderTest of modelsUnderTest) {
        for (let testi = 0; testi < tests.length; ++testi) {
            const test = tests[testi]
            console.log(
                `${files.name}> ${modelUnderTest}: run test ${testi + 1}/${tests.length}x${runsPerTest} ${test.testinput.slice(0, 42)}...`
            )
            for (let ri = 0; ri < runsPerTest; ++ri) {
                const testRes = await runTest(files, test, {
                    ...options,
                    model: modelUnderTest,
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
    }
): Promise<PromptPexTestResult> {
    const { model, compliance, customTestEvalTemplate, evalCache } =
        options || {}
    if (!model) throw new Error("No model provided for test")

    const { cache, testRunCache, ...optionsNoCache } = options || {}
    const moptions = modelOptions(model, {
        ...optionsNoCache,
        cache: testRunCache,
    })

    const { id, promptid, file } = await resolveTestPath(files, test, {
        model,
        evalCache,
    })
    /* if (file?.content && !force) {
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
    }*/
    const { inputs, args, testInput } = resolvePromptArgs(files, test)
    const allRules = parseAllRules(files, options)
    const rule = resolveRule(allRules, test)
    if (!args) {
        dbg(`invalid test input %O`, { test, inputs, testInput })
        return {
            id,
            promptid,
            ...rule,
            scenario: test.scenario,
            baseline: test.baseline,
            model: "",
            error: "invalid test input",
            input: testInput,
            output: "invalid test input",
        } satisfies PromptPexTestResult
    }

    const res = await measure("test.run", () =>
        generator.runPrompt(
            (ctx) => {
                ctx.importTemplate(files.prompt, args, {
                    allowExtraArguments: true,
                })
                if (!Object.keys(inputs || {}).length) ctx.writeText(testInput)
            },
            {
                ...moptions,
                label: `${files.name}> ${moptions.model}: run test ${testInput.slice(0, 42)}...`,
            }
        )
    )
    if (res.error) {
        dbg(`test run error ${res.finishReason}, ${res.error.message}`, {
            test,
            inputs,
            args,
            testInput,
        })
        throw new Error(res.error.message)
    }
    const actualOutput = res.text
    output.startDetails(`test result: ${testInput.slice(0, 42)}}...`)
    output.itemValue("model", model)
    output.fence(testInput)
    output.fence(actualOutput)
    output.endDetails()

    const testRes: PromptPexTestResult = {
        id,
        promptid,
        ...rule,
        scenario: test.scenario,
        baseline: test.baseline,
        model: res.model,
        error: res.error?.message,
        input: testInput,
        output: actualOutput,
    } satisfies PromptPexTestResult

    if (compliance) {
        testRes.compliance = undefined
        const compliance = await evaluateTestResult(files, testRes, options)
        testRes.complianceText = compliance.content
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
