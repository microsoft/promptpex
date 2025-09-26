import { checkConfirm } from "./confirm.mts"
import { openaiEvalsListEvals, openaiEvalsGenerate } from "./openaievals.mts"
import { diagnostics } from "./flags.mts"
import { generateInputSpec } from "./inputspecgen.mts"
import { generateIntent } from "./intentgen.mts"
import { generateInverseOutputRules } from "./inverserulesgen.mts"
import { outputFile, outputLines, outputTable } from "./output.mts"
import { metricName, parseTestResults } from "./parsers.mts"
import { reportPerf } from "./perf.mts"
import { expandTests } from "./testexpand.mts"
import { generateBaselineTests } from "./baselinetestgen.mts"
import { evaluateTestsQuality } from "./testquality.mts"

import {
    computeOverview,
    computeSeparateOverviews,
    generateReports,
    renderTestResults,
} from "./reports.mts"
import { generateOutputRules } from "./rulesgen.mts"
import { generateTests } from "./testgen.mts"
import { runTests } from "./testrun.mts"
import { evaluateTestMetrics } from "./testevalmetric.mts"
import type { PromptPexContext, PromptPexTestResult } from "./types.mts"
import {
    MODEL_ALIAS_RULES,
    MODEL_ALIAS_STORE,
    PROMPTPEX_CONTEXT,
} from "./constants.mts"
import { evalTestCollection } from "./testcollectioneval.mts"
import { githubModelsEvalsGenerate } from "./githubmodels.mts"
import { resolve } from "node:path"
import { saveContextState } from "./loaders.mts"

const { output } = env
const dbg = host.logger("promptpex")

export async function promptpexGenerate(files: PromptPexContext, modelsUnderTest?: string[]) {
    const { name, prompt, options } = files
    const {
        evals,
        evalModels,
        createEvalRuns,
        storeCompletions,
        storeModel,
        testExpansions,
        rateTests,
        testValidity,
        compliance,
        groundtruth,
        groundtruthModel,
        // modelsUnderTest,
        evalModelsGroundtruth,
        baselineModel,
        baselineTests,
    } = options

    dbg(`modelsUnderTest: %O`, modelsUnderTest)

    dbg("writeResults: %s", files.writeResults)

    output.heading(2, name)
    output.itemValue(`prompt file`, prompt.filename)
    const rulesModel = await host.resolveLanguageModel(MODEL_ALIAS_RULES)
    dbg(`rules model: %O`, rulesModel)
    //   if (!rulesModel.model) throw new Error(`Model ${MODEL_ALIAS_RULES} not found`)
    output.itemValue(
        `rules model`,
        `${rulesModel.provider}:${rulesModel.model}`
    )

    if (groundtruth) {
        const resolved = await host.resolveLanguageModel(groundtruthModel)
        //    if (!resolved.model)
        //        throw new Error(`Model ${groundtruthModel} not found`)
        output.itemValue(
            `groundtruth model`,
            `${resolved.provider}:${resolved.model}`
        )
    }

    if (modelsUnderTest?.length) {
        for (const modelUnderTest of modelsUnderTest) {
            const resolved = await host.resolveLanguageModel(modelUnderTest)
            //            if (!resolved.model)
            //              throw new Error(`Model ${modelUnderTest} not found`)
            output.itemValue(
                `model under test`,
                `${resolved.provider}:${resolved.model}`
            )
        }
    }




    if (evals)
        if (evalModels?.length) {
            for (const eModel of evalModels) {
                const resolved = await host.resolveLanguageModel(eModel)
                if (!resolved) throw new Error(`Model ${eModel} not found`)
                output.itemValue(
                    `eval model`,
                    `${resolved.provider}:${resolved.model}`
                )
            }
        } else {
            cancel("No evaluation model defined.")
        }

    // use context state if available
    if (diagnostics) {
        output.heading(2, `PromptPex Diagnostics`)
        await generateReports(files)
        if (createEvalRuns) {
            const openAIEvals = await openaiEvalsListEvals()
            if (!openAIEvals.ok)
                throw new Error("evals configuration not found")
        }
        await checkConfirm("diag")
    }
    // prompt info
    output.heading(3, `Prompt Under Test`)
    if (files.originalPrompt) {
        output.itemValue(`filename`, files.originalPrompt.filename)
        output.fence(files.originalPrompt.content, "md")
        output.detailsFenced(files.prompt.filename, files.prompt.content, "md")
    } else {
        output.itemValue(`filename`, files.prompt.filename)
        output.fence(files.prompt.content, "md")
    }

    if (files.testSamples?.length) {
        output.startDetails("test samples")
        outputTable(files.testSamples)
        output.endDetails()
    }

    // generate intent
    output.heading(3, "Intent")
    await generateIntent(files, options)
    outputFile(files.intent)
    await checkConfirm("intent")

    // generate input spec
    output.heading(3, "Input Specification")
    await generateInputSpec(files, options)
    outputLines(files.inputSpec, "rules")
    await checkConfirm("inputspec")

    // generate rules
    output.heading(3, "Output Rules")
    await generateOutputRules(files, options)
    outputLines(files.rules, "rules")
    await checkConfirm("rule")

    // generate inverse rules
    output.heading(3, "Inverse Output Rules")
    await generateInverseOutputRules(files, options)
    outputLines(files.inverseRules, "inverse rules")
    await checkConfirm("inverse")

    // generate tests
    output.heading(3, "Tests")
    await generateTests(files, options)


    // generate baseline tests
    if (baselineTests) {
        if (baselineModel?.length) {
            const resolved = await host.resolveLanguageModel(baselineModel)
            if (!resolved) throw new Error(`Model ${baselineModel} not found`)
            output.itemValue(
                `baseline model`,
                `${resolved.provider}:${resolved.model}`
            )
        } else {
            cancel("No baseline model defined.")
        }
        if (!files.baselineTests.content) {
            await generateBaselineTests(files, options)
            files.testEvals.content = undefined
            files.testOutputs.content = undefined
        }
        outputFile(files.baselineTests)
        await checkConfirm("baseline")
    }

    outputTable(
        files.promptPexTests.map(({ scenario, testinput, reasoning }) => ({
            scenario,
            testinput,
            reasoning,
        }))
    )
    output.detailsFenced(`tests (json)`, files.promptPexTests, "json")
    output.detailsFenced(`test data (json)`, files.testData.content, "json")
    await checkConfirm("test")

    if (testExpansions > 0) {
        output.heading(3, "Expanded Tests")
        await expandTests(files, files.promptPexTests, options)
        outputTable(
            files.promptPexTests.map(
                ({
                    scenario,
                    testinput: expanded,
                    testinputOriginal: original,
                    reasoning,
                }) => ({
                    scenario,
                    expanded,
                    original,
                    reasoning,
                })
            )
        )
        output.detailsFenced(`tests (json)`, files.promptPexTests, "json")
        output.detailsFenced(`test data (json)`, files.testData.content, "json")
        await checkConfirm("expansion")
    }

    // label tests with unique IDs
    output.heading(3, "Label Tests with Unique IDs")
    if (files.promptPexTests?.length) {
        for (const [index, test] of files.promptPexTests.entries()) {
            if (!test.testuid) {
                const id = Math.random().toString().slice(-8)
                files.promptPexTests[index].testuid = `test-${id}`
            }
        }
    }


    dbg(`modelsUnderTest: %O`, modelsUnderTest)

    // test validity and quality evaluation
    if (testValidity) {
        output.heading(3, "Test Validity and Quality")
        const tc = await evaluateTestsQuality(files, {
            ...(options || {}),
        })
        if (tc !== files.testEvals.content) {
            files.testEvals.content = tc
            if (files.writeResults) {
                await workspace.writeText(
                    files.testEvals.filename,
                    files.testEvals.content
                )
            }
        }
        outputFile(files.testEvals)
        output.detailsFenced(`test evaluations (json)`, tc, "json")
        await checkConfirm("testValidity")
    }

    // After test expansion, before evals
    if (rateTests) {
        output.heading(3, "Test Set Quality Review")
        await evalTestCollection(files, options)
        output.detailsFenced(`test ratings (md)`, files.rateTests, "md")
        await checkConfirm("rateTests")
    }

    // one of the tests does not have a groundtruth entry
    const needsGroundtruth = files.promptPexTests.some(
        (t) => !t.groundtruth || !t.groundtruthModel
    )
    if (groundtruth && needsGroundtruth) {
        output.heading(3, `Groundtruth`)
        const resolved = await host.resolveLanguageModel(groundtruthModel)
        output.itemValue(
            `groundtruth model`,
            `${resolved.provider}:${resolved.model}`
        )
        const results = await runTests(files, {
            ...options,
            runGroundtruth: true,
            runsPerTest: 1,
        })
        outputTable(
            files.promptPexTests.map(
                ({ scenario, testinput, groundtruth }) => ({
                    scenario,
                    testinput,
                    groundtruth,
                })
            )
        )
        output.detailsFenced(`tests (json)`, files.promptPexTests, "json")

        if (evalModelsGroundtruth?.length) {
            dbg(
                `evaluating groundtruth with eval models %O`,
                evalModelsGroundtruth
            )
            output.itemValue(
                `ground truth evaluation models`,
                evalModelsGroundtruth.join(", ")
            )
            // Evaluate metrics for groundtruth tests
            for (const testRes of results) {
                const newResult = await evaluateTestMetrics(testRes, files, {
                    ...options,
                    runGroundtruth: true,
                })
                testRes.metrics = newResult.metrics
            }
            if (results?.length) output.heading(3, `Groundtruth eval results`)
            outputTable(
                renderTestResults(results.filter((r) => r.isGroundtruth)),
                { maxRows: 12 }
            )
            files.groundtruthOutputs.content = JSON.stringify(results, null, 2)
            if (files.writeResults)
                await workspace.writeText(
                    files.groundtruthOutputs.filename,
                    JSON.stringify(results, null, 2)
                )
        } else {
            output.error(`No evaluation models provided for groundtruth tests`)
        }
        await checkConfirm("groundtruth")
    }

    await githubModelsEvalsGenerate(files, files.promptPexTests, options)
    if (modelsUnderTest?.length) {
        await openaiEvalsGenerate(files, files.promptPexTests, options)
        await checkConfirm("integration")
    }

    if (modelsUnderTest?.length) {
        // run tests against the model(s)
        output.heading(3, `Test Runs with Models Under Test`)
        if (storeCompletions)
            output.itemValue(
                `stored completion model`,
                (
                    await host.resolveLanguageModel(
                        storeModel || MODEL_ALIAS_STORE
                    )
                )?.model || "store"
            )
        output.itemValue(`models under test`, modelsUnderTest.join(", "))

        output.heading(4, `Metrics`)
        for (const metric of files.metrics)
            output.detailsFenced(metricName(metric), metric.content, "markdown")

        if (evalModels?.length)
            output.itemValue(`evaluation models`, evalModels.join(", "))

        output.heading(4, `Test Results`)
        const results = await runTests(files, options)
        files.testOutputs.content = JSON.stringify(results, null, 2)
        if (files.writeResults)
            await workspace.writeText(
                files.testOutputs.filename,
                JSON.stringify(results, null, 2)
            )
        output.detailsFenced(`results (json)`, results, "json")
    }

    // only measure metrics if eval is true
    if (evals) {
        output.heading(4, `Evaluating Test Results`)
        const originalResults = parseTestResults(files)
        // unclear you want to run more tests...
        // const results = await runTests(files, options)
        const results = []
        // Evaluate metrics for all test results
        for (const testRes of originalResults) {
            const newResult: PromptPexTestResult = await evaluateTestMetrics(
                testRes,
                files,
                {
                    ...options,
                    runGroundtruth: false,
                }
            )
            testRes.metrics = newResult.metrics
        }
        const allResults = [...results, ...originalResults]
        files.testOutputs.content = JSON.stringify(allResults, null, 2)
        if (files.writeResults)
            await workspace.writeText(
                files.testOutputs.filename,
                JSON.stringify(allResults, null, 2)
            )
        output.detailsFenced(`results (json)`, results, "json")
    }

    // final result table
    {
        const results = parseTestResults(files)
        if (results?.length) {
            outputTable(
                renderTestResults(results.filter((r) => !r.isGroundtruth)),
                { maxRows: 12 }
            )
        }
    }

    // Generate separate overviews for regular and baseline tests
    const { regularOverview, baselineOverview } = computeSeparateOverviews(files, { percent: true })
    
    if (regularOverview.length) {
        output.heading(3, `Results Overview (Regular Tests)`)
        outputTable(regularOverview)
        if (files.writeResults)
            await workspace.writeText(
                path.join(files.dir, "overview.csv"),
                CSV.stringify(regularOverview, { header: true })
            )
    }
    
    if (baselineOverview.length) {
        output.heading(3, `Results Overview (Baseline Tests)`)
        outputTable(baselineOverview)
        if (files.writeResults)
            await workspace.writeText(
                path.join(files.dir, "overview-baseline.csv"),
                CSV.stringify(baselineOverview, { header: true })
            )
    }

    if (files.writeResults)
        output.itemValue(`output directory`, resolve(files.dir))
    output.appendContent("\n\n---\n\n")

    dbg("writeResults: %s", files.writeResults)
    if (files.writeResults) dbg("writing context to", files.dir)
    await saveContextState(files, path.join(files.dir, PROMPTPEX_CONTEXT))
    reportPerf()
}
