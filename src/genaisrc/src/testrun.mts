import {
    GROUNDTRUTH_FAIL_SCORE,
    GROUNDTRUTH_RETRIES,
    GROUNDTRUTH_THRESHOLD,
    MODEL_ALIAS_EVAL,
    MODEL_ALIAS_STORE,
    TEST_TRAINING_DATASET_RATIO,
} from "./constants.mts"
import { resolveTestPath } from "./filecache.mts"
import {
    modelOptions,
    parseAllRules,
    parseBaselineTests,
    parseOKERR,
    metricName,
} from "./parsers.mts"
import { measure } from "./perf.mts"
import { resolvePromptArgs, resolveRule } from "./resolvers.mts"
import { evaluateTestResult } from "./testresulteval.mts"
import { evaluateTestMetrics, createMetricKey } from "./testevalmetric.mts"
import type {
    PromptPexContext,
    PromptPexOptions,
    PromptPexTest,
    PromptPexTestResult,
} from "./types.mts"
import assert from "node:assert/strict"
const dbg = host.logger("promptpex:eval:run")

const { generator, output } = env

async function computeGroundtruthScore(
    testRes: PromptPexTestResult,
    files: PromptPexContext,
    options?: PromptPexOptions & { runGroundtruth?: boolean }
): Promise<number | undefined> {
    const gtMetrics = await evaluateTestMetrics(testRes, files, options)
    // dbg(`groundtruth metrics: %O`, gtMetrics)
    // assumptions: at least 1 evalModelsGroundtruth is provided
    // at most 1 metric is provided
    // Combine the scores of the metrics for the groundtruth
    const keys = options?.evalModelsGroundtruth.map((eModel) =>
        createMetricKey(metricName(files.groundtruthMetrics[0]), eModel)
    )
    const metricResults = keys
        .map((k) => gtMetrics.metrics[k])
        .filter((m) => !isNaN(m?.score))
    if (metricResults.length > 0 && options?.evalModelsGroundtruth.length > 0) {
        const avg =
            metricResults.reduce((sum, m) => sum + m.score, 0) /
            metricResults.length
        return avg
    }
    return undefined
}

export async function runTests(
    files: PromptPexContext,
    options?: PromptPexOptions & {
        runGroundtruth?: boolean
    }
): Promise<PromptPexTestResult[]> {
    const {
        groundtruthModel,
        modelsUnderTest,
        maxTestsToRun,
        storeCompletions,
        storeModel = MODEL_ALIAS_STORE,
        runsPerTest = 1,
        runGroundtruth,
    } = options || {}
    if (!groundtruthModel && !modelsUnderTest?.length && !storeCompletions)
        throw new Error("No models to run tests on")
    if (runGroundtruth && !groundtruthModel)
        throw new Error("No groundtruth model provided for running tests")

    const rulesTests = files.promptPexTests
    dbg(`found ${rulesTests.length} tests`)
    const baselineTests = options?.baselineTests
        ? parseBaselineTests(files)
        : []

    dbg(`found ${baselineTests.length} tests`)
    // run all the tests when generating groundtruth
    const tests = [...rulesTests, ...baselineTests].slice(
        0,
        runGroundtruth ? undefined : maxTestsToRun
    )

    if (!tests?.length) {
        dbg(`rules tests:\n%s`, files.tests.content)
        dbg(`baseline tests:\n%s`, files.baselineTests.content)
        throw new Error("No tests found to run")
    }

    const checkpoint = async () => {
        files.testOutputs.content = JSON.stringify(testResults, null, 2)
        if (files.writeResults) await workspace.writeFiles(files.testOutputs)
    }
    const checkpointTests = async () => {
        files.tests.content = JSON.stringify(rulesTests, null, 2)
        if (files.writeResults) await workspace.writeFiles(files.tests)
    }

    const modelsToRun: {
        model: ModelType
        metadata: Record<string, string>
    }[] = runGroundtruth
        ? [
              {
                  model: groundtruthModel,
                  metadata: { prompt: files.name, ...files.versions },
              },
          ]
        : [
              storeCompletions
                  ? {
                        model: storeModel,
                        metadata: {
                            prompt: files.name,
                            ...files.versions,
                        },
                    }
                  : undefined,
              ...modelsUnderTest.map((model) => ({
                  model,
                  metadata: undefined,
              })),
          ].filter(Boolean)
    dbg(
        `running ${tests.length} tests (x ${runsPerTest}) with ${modelsToRun.length} models`
    )
    output.startDetails(`running ${tests.length} tests (x ${runsPerTest})`, {
        expanded: false,
    })

    const ntraining = tests.length * TEST_TRAINING_DATASET_RATIO
    const testResults: PromptPexTestResult[] = []
    for (const modelToRun of modelsToRun) {
        const { model: modelUnderTest, metadata } = modelToRun
        for (let testi = 0; testi < tests.length; ++testi) {
            const test = tests[testi]
            console.log(
                `${files.name}> ${modelUnderTest}: run test ${testi + 1}/${tests.length}x${runsPerTest} ${test.testinput.slice(0, 42)}...`
            )
            const testMetadata: Record<string, string> = metadata
                ? {
                      ...metadata,
                      run: files.runId,
                      scenario: test.scenario,
                      testid: !isNaN(test.testid)
                          ? String(test.testid)
                          : undefined,
                      ruleid: !isNaN(test.ruleid)
                          ? String(test.ruleid)
                          : undefined,
                      baseline: test.baseline ? "true" : undefined,
                      generation: !isNaN(test.generation)
                          ? String(test.generation)
                          : undefined,
                      dataset: testi < ntraining ? "training" : "test",
                  }
                : undefined
            for (let ri = 0; ri < runsPerTest; ++ri) {
                let testRes: PromptPexTestResult | undefined
                let retryCount = 0
                let shouldRetry = false
                do {
                    testRes = await runTest(files, test, {
                        ...options,
                        model: modelUnderTest,
                        metadata: testMetadata,
                    })
                    assert(testRes.model)
                    shouldRetry = false
                    if (testRes) {
                        // store groundtruth
                        if (runGroundtruth) {
                            const gtScore: number =
                                await computeGroundtruthScore(
                                    testRes,
                                    files,
                                    options
                                )
                            test.groundtruthScore = gtScore
                            dbg(`groundtruth score: %O`, test.groundtruthScore)
                            test.groundtruthModel = testRes.model
                            test.groundtruth = testRes.output
                            testRes.isGroundtruth = true
                            await checkpointTests()
                            // Retry logic for low groundtruthScore
                            if (
                                test.groundtruthScore < GROUNDTRUTH_THRESHOLD &&
                                retryCount < GROUNDTRUTH_RETRIES
                            ) {
                                dbg(
                                    `groundtruthScore < GROUNDTRUTH_THRESHOLD (${test.groundtruthScore}), retrying (${retryCount + 1}/${GROUNDTRUTH_RETRIES})`
                                )
                                retryCount++
                                shouldRetry = true
                            }
                        }
                        if (!shouldRetry) {
                            testResults.push(testRes)
                            await checkpoint()
                        }
                    }
                } while (shouldRetry)
                // If after retries groundtruthScore is still < 50, set to -1
                if (
                    runGroundtruth &&
                    test.groundtruthScore < 50 &&
                    retryCount >= 3
                ) {
                    dbg(
                        `groundtruthScore < ${GROUNDTRUTH_THRESHOLD} after ${retryCount} retries, setting to ${GROUNDTRUTH_FAIL_SCORE}`
                    )
                    test.groundtruthScore = -1
                }
            }
        }
    }

    await checkpoint()
    output.endDetails()
    return testResults
}

function updateTestResultCompliant(testRes: PromptPexTestResult) {
    testRes.compliance = parseOKERR(testRes.complianceText)
}

async function runTest(
    files: PromptPexContext,
    test: PromptPexTest,
    options?: PromptPexOptions & {
        model?: ModelType
        compliance?: boolean
        metadata?: Record<string, string>
    }
): Promise<PromptPexTestResult> {
    const { model, compliance, evalCache, metadata, evalModels } = options || {}
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
            testinput: testInput,
            model: "",
            error: "invalid test input",
            input: testInput,
            output: "invalid test input",
            metrics: {},
        } satisfies PromptPexTestResult
    }

    dbg(`running test %o\n%O`, test.testid, args)
    const res = await measure("test.run", () =>
        generator.runPrompt(
            (ctx) => {
                ctx.importTemplate(files.prompt, args, {
                    allowExtraArguments: true,
                })
            },
            {
                ...moptions,
                metadata,
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
        testinput: testInput,
        model: res.model,
        error: res.error?.message,
        input: testInput,
        output: actualOutput,
        metrics: {},
    } satisfies PromptPexTestResult

    if (compliance) {
        const eModel = evalModels?.[0] || MODEL_ALIAS_EVAL
        testRes.compliance = undefined
        const compliance = await evaluateTestResult(
            files,
            eModel,
            testRes,
            options
        )
        testRes.complianceText = compliance.content
        updateTestResultCompliant(testRes)
    }

    if (file)
        await workspace.writeText(
            files.testOutputs.filename,
            JSON.stringify(testRes, null, 2)
        )
    return testRes
}
