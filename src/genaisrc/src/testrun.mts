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
        force?: boolean
        q?: PromiseQueue
    }
): Promise<string> {
    console.debug("[runTests] Starting with options:", JSON.stringify(options, null, 2))
    const {
        force,
        modelsUnderTest,
        maxTestsToRun,
        runsPerTest = 1,
    } = options || {}
    if (!modelsUnderTest?.length) throw new Error("No models to run tests on")

    console.debug("[runTests] Parsing tests...")
    const rulesTests = parseRulesTests(files.tests.content)
    console.debug("[runTests] Found rules tests:", rulesTests.length)
    const baselineTests = options?.baselineTests === false
        ? []
        : parseBaselineTests(files)
    console.debug("[runTests] Found baseline tests:", baselineTests.length)
    const tests = [...rulesTests, ...baselineTests].slice(0, maxTestsToRun)
    if (!tests?.length) throw new Error("No tests found to run")

    console.log(
        `running ${tests.length} tests (x ${runsPerTest}) with ${modelsUnderTest.length} models`
    )

    const testResults: PromptPexTestResult[] = []
    const runPromises: Promise<PromptPexTestResult>[] = []
    const evalPromises: Promise<void>[] = []

    // Function to run a single test
    const runTestOnly = async (modelUnderTest: string, test: PromptPexTest, testIndex: number, runIndex: number) => {
        const testId = `${modelUnderTest}-${testIndex}-${runIndex}`
        console.debug(`[runTests] [${testId}] Starting test run`)
        console.log(
            `${files.name}> ${modelUnderTest}: run test ${testIndex + 1}/${tests.length}x${runsPerTest} ${test.testinput.slice(0, 42)}...`
        )

        const testRes = await runTest(files, test, {
            ...options,
            model: modelUnderTest,
            force,
        })
        console.debug(`[runTests] [${testId}] Test run completed`)
        assert(testRes.model)
        testResults.push(testRes)
        return testRes
    }

    // Function to evaluate a single test result
    const evalTestOnly = async (testRes: PromptPexTestResult) => {
        const testId = `${testRes.model}-${testRes.id}`
        console.debug(`[runTests] [${testId}] Starting evaluation`)
        if (options?.compliance || options?.customTestEvalTemplate) {
            if (options.compliance) {
                testRes.complianceText = await evaluateTestResult(
                    files,
                    testRes,
                    options
                )
                updateTestResultCompliant(testRes)
                console.debug(`[runTests] [${testId}] Compliance evaluation completed`)
            }

            if (options.customTestEvalTemplate) {
                testRes.customEvalText = await evaluateCustomTestResult(
                    files,
                    testRes,
                    options
                )
                console.debug(`[runTests] [${testId}] Custom evaluation completed`)
            }
        }
        console.debug(`[runTests] [${testId}] All evaluations completed`)
    }

    // Start all test runs in sequence
    for (const modelUnderTest of modelsUnderTest) {
        console.debug("[runTests] Starting tests for model:", modelUnderTest)
        for (let testi = 0; testi < tests.length; ++testi) {
            const test = tests[testi]
            for (let ri = 0; ri < runsPerTest; ++ri) {
                console.debug("[runTests] Run iteration:", ri + 1, "of", runsPerTest)
                // Start the test run
                const testPromise = runTestOnly(modelUnderTest, test, testi, ri)
                runPromises.push(testPromise)

                // When test completes, start its evaluation
                testPromise.then(testRes => {
                    console.debug(`[runTests] Test ${testRes.id} completed, starting evaluation`)
                    const evalPromise = evalTestOnly(testRes)
                    evalPromises.push(evalPromise)
                })
            }
        }
    }

    // Wait for all runs to complete
    console.debug("[runTests] Waiting for all runs to complete...")
    await Promise.all(runPromises)
    console.debug("[runTests] All runs completed")

    // Wait for all evaluations to complete
    console.debug("[runTests] Waiting for all evaluations to complete...")
    await Promise.all(evalPromises)
    console.debug("[runTests] All evaluations completed")

    return JSON.stringify(testResults, null, 2)
}

function updateTestResultCompliant(testRes: PromptPexTestResult) {
    console.debug("[updateTestResultCompliant] Updating compliance for result:", JSON.stringify(testRes, null, 2))
    console.debug("[updateTestResultCompliant] complianceText:", testRes.complianceText)
    if (testRes.complianceText) {
        testRes.compliance = parseOKERR(testRes.complianceText)
        console.debug("[updateTestResultCompliant] Updated compliance:", testRes.compliance)
    }
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
    console.debug("[runTest] Starting with test:", JSON.stringify(test, null, 2))
    console.debug("[runTest] Options:", JSON.stringify(options, null, 2))
    
    const { model, force, compliance, customTestEvalTemplate, evalCache } =
        options || {}
    if (!model) throw new Error("No model provided for test")

    console.debug("[runTest] Getting model options for:", model)
    const moptions = modelOptions(model, options)
    console.debug("[runTest] Model options:", JSON.stringify(moptions, null, 2))

    console.debug("[runTest] Resolving test path...")
    const { id, promptid, file } = await resolveTestPath(files, test, {
        model,
        evalCache,
    })
    console.debug("[runTest] Resolved path:", { id, promptid, file: file?.filename })

    if (file?.content && !force) {
        console.debug("[runTest] Found cached result, checking if valid...")
        const res = parsers.JSON5(file) as PromptPexTestResult
        if (res && !res.error && res.complianceText) {
            console.debug("[runTest] Using cached result")
            if (!res.model)
                output.warn(
                    `invalid test result ${file.filename}, missing model field`
                )
            updateTestResultCompliant(res)
            res.baseline = test.baseline
            return res
        }
    }

    console.debug("[runTest] Resolving prompt args...")
    const { inputs, args, testInput } = resolvePromptArgs(files, test)
    console.debug("[runTests] Resolved args:", JSON.stringify({ inputs, args, testInput }, null, 2))

    console.debug("[runTest] Parsing rules...")
    const allRules = parseAllRules(files)
    const rule = resolveRule(allRules, test)
    console.debug("[runTest] Resolved rule:", JSON.stringify(rule, null, 2))

    if (!args) {
        console.debug("[runTest] No valid args found, returning error result")
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
    }

    console.debug("[runTest] Running prompt...")
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
    console.debug("[runTest] Prompt result:", JSON.stringify(res, null, 2))

    if (res.error) {
        console.debug("[runTest] Error in prompt result:", res.error)
        console.debug(res.finishReason)
        console.debug(JSON.stringify(res.error, null, 2))
        throw new Error(res.error.message)
    }

    const actualOutput = res.text
    console.debug("[runTest] Actual output:", actualOutput)
    output.detailsFenced(
        `test result: ${testInput.slice(0, 42)}}...`,
        testInput + "\n\n---\n\n" + actualOutput
    )

    console.debug("[runTest] Creating test result object...")
    const testRes: PromptPexTestResult = {
        id,
        promptid,
        ...rule,
        baseline: test.baseline,
        model: res.model,
        error: res.error?.message,
        input: testInput,
        output: actualOutput,
        compliance: undefined,
        complianceText: undefined,
        customEvalText: undefined
    } satisfies PromptPexTestResult
    console.debug("[runTest] Created test result:", JSON.stringify(testRes, null, 2))

    // Write file if needed
    if (file) {
        console.debug("[runTest] Writing result to file:", file.filename)
        await workspace.writeText(
            file.filename,
            JSON.stringify(testRes, null, 2)
        )
    }

    console.debug("[runTest] Returning test result")
    return testRes
}
