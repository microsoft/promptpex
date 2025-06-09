import { checkConfirm } from "./confirm.mts"
import {
    openaiEvalsListEvals,
    openaiEvalsGenerate,
} from "./openaievals.mts"
import { diagnostics } from "./flags.mts"
import { generateInputSpec } from "./inputspecgen.mts"
import { generateIntent } from "./intentgen.mts"
import { generateInverseOutputRules } from "./inverserulesgen.mts"
import { loadPromptFiles, updateOutput } from "./loaders.mts"
import { outputFile, outputLines } from "./output.mts"
import { metricName } from "./parsers.mts"
import { initPerf, reportPerf } from "./perf.mts"
import { expandTests } from "./testexpand.mts"
import {
    computeOverview,
    generateReports,
    renderEvaluation,
    renderEvaluationOutcome,
} from "./reports.mts"
import { generateOutputRules } from "./rulesgen.mts"
import { generateTests } from "./testgen.mts"
import { runTests } from "./testrun.mts"
import { evaluateTestMetrics } from "./testevalmetric.mts"
import type {
    PromptPexContext,
    PromptPexOptions,
    PromptPexTest,
    PromptPexTestResult,
} from "./types.mts"
import {
    MODEL_ALIAS_STORE,
    PROMPTPEX_CONTEXT,
} from "./constants.mts"
import { evalTestCollection } from "./testcollectioneval.mts"
import { saveContextState, restoreContextState } from "./context.mts"
import { githubModelsEvalsGenerate } from "./githubmodels.mts"

const { output } = env
const dbg = host.logger("promptpex")

export async function promptpexGenerate(file: WorkspaceFile, options: PromptPexOptions) {
    const {
        evals,
        evalModels,
        loadContext,
        loadContextFile,
        createEvalRuns,
        storeCompletions,
        storeModel,
        testExpansions,
        filterTestCount,
        out,
        rateTests,
        groundtruthModel,
        modelsUnderTest
    } = options

    output.heading(2, "PromptPex Test Generation")
    output.itemValue(`prompt file`, file.filename)
    output.detailsFenced(`options`, options, "yaml")

    if (modelsUnderTest?.length) {
        output.heading(3, `Models Under Test`)
        for (const modelUnderTest of modelsUnderTest) {
            const resolved = await host.resolveLanguageModel(modelUnderTest)
            if (!resolved) throw new Error(`Model ${modelUnderTest} not found`)
            output.item(`${resolved.provider}:${resolved.model}`)
        }
    }

    if (groundtruthModel?.length) {
        output.heading(3, `Groundtruth Model`)

        const resolved = await host.resolveLanguageModel(groundtruthModel)
        if (!resolved) throw new Error(`Model ${groundtruthModel} not found`)
        output.item(`${resolved.provider}:${resolved.model}`)
    }

    if (evals)
        if (evalModels?.length) {
            output.heading(2, `Evaluation Models`)
            for (const eModel of evalModels) {
                const resolved = await host.resolveLanguageModel(eModel)
                if (!resolved) throw new Error(`Model ${eModel} not found`)
                output.item(`${resolved.provider}:${resolved.model}`)
            }
        } else {
            cancel("No evaluation model defined.")
        }

    // process the prompt file (or read the context file)

    let files: PromptPexContext
    if (!loadContext) files = await loadPromptFiles(file, options)

    // use context state if available

    if (loadContext) {
        output.heading(3, `Loading context from file`)
        const newOut = out
        output.appendContent(
            `loading PromptPexContext from ${loadContextFile}`
        )
        files = await restoreContextState(loadContextFile)
        updateOutput(newOut, files)

        // Save the contents of the prompt file to the out directory with the original prompt file name
        if (
            files.prompt &&
            files.prompt.filename &&
            files.prompt.content &&
            out
        ) {
            const promptOutPath = path.join(
                out,
                path.basename(files.prompt.filename)
            )
            await workspace.writeText(promptOutPath, files.prompt.content)
            dbg(`Saved prompt file to ${promptOutPath}`)
        }
    } else {
        if (diagnostics) {
            output.heading(2, `PromptPex Diagnostics`)
            await generateReports(files)
            if (createEvalRuns) {
                const evals = await openaiEvalsListEvals()
                if (!evals.ok) throw new Error("evals configuration not found")
            }
            await checkConfirm("diag")
        }
        // prompt info
        output.heading(3, `Prompt Under Test`)
        output.itemValue(`filename`, files.prompt.filename)
        output.fence(files.prompt.content, "md")

        if (files.testSamples?.length) {
            output.startDetails("test samples")
            output.table(files.testSamples)
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
        outputFile(files.inputSpec)
        await checkConfirm("inputspec")

        // generate rules
        output.heading(3, "Output Rules")
        await generateOutputRules(files, options)
        outputLines(files.rules, "rule")
        await checkConfirm("rule")

        // generate inverse rules
        output.heading(3, "Inverse Output Rules")
        await generateInverseOutputRules(files, options)
        outputLines(files.inverseRules, "generate inverse output rule")
        await checkConfirm("inverse")

        // generate tests
        output.heading(3, "Tests")
        files.promptPexTests = await generateTests(files, options)

        output.table(
            files.promptPexTests.map(({ scenario, testinput, expectedoutput }) => ({
                scenario,
                testinput,
                expectedoutput,
            }))
        )
        output.detailsFenced(`tests (json)`, files.promptPexTests, "json")
        output.detailsFenced(`test data (json)`, files.testData.content, "json")
        await checkConfirm("test")
    }

    if (testExpansions > 0) {
        output.heading(3, "Expanded Tests")
        await expandTests(files, files.promptPexTests, options)
        output.table(
            files.promptPexTests.map(({ scenario, testinput, expectedoutput }) => ({
                scenario,
                testinput,
                expectedoutput,
            }))
        )
        await checkConfirm("expansion")
        output.detailsFenced(`tests (json)`, files.promptPexTests, "json")
        output.detailsFenced(`test data (json)`, files.testData.content, "json")
    }

    // After test expansion, before evals
    if (rateTests) {
        output.heading(3, "Test Set Quality Review")
        await evalTestCollection(files, options)
        output.detailsFenced(`test ratings (md)`, files.rateTests, "md")
        output.detailsFenced(`filtered tests (json)`, files.filteredTests, "json")
        await checkConfirm("rateTests")
    }

    if (modelsUnderTest?.length)
        await githubModelsEvalsGenerate(files, files.promptPexTests, options)

    if (modelsUnderTest?.length) {
        if (files.filteredTests.content?.length) {
            // Parse the JSON content
            output.heading(3, `Running ${filterTestCount} Filtered Tests`)
            const filteredTests: PromptPexTest[] = JSON.parse(
                files.filteredTests.content
            )
            await openaiEvalsGenerate(files, filteredTests, options)
        } else {
            await openaiEvalsGenerate(files, files.promptPexTests, options)
        }
        await checkConfirm("openaievals")
    }

    if (createEvalRuns) {
        output.note(`Evals run created, skipping local evals...`)
    } else if (evals && !modelsUnderTest?.length && !storeCompletions) {
        output.warn(
            `No modelsUnderTest and storeCompletions is not enabled. Skipping test run.`
        )

        if (evalModels?.length && loadContext) {
            output.note(`Evaluating saved test results using evalModel.`)
            const results = JSON.parse(files.testOutputs.content)
            // Evaluate metrics for all test results
            for (const testRes of results) {
                const newResult = await evaluateTestMetrics(testRes, files, options)
                testRes.metrics = newResult.metrics
            }
            files.testOutputs.content = JSON.stringify(results, null, 2)

            if (files.writeResults)
                await workspace.writeText(
                    files.testOutputs.filename,
                    JSON.stringify(results, null, 2)
                )
            output.detailsFenced(`results (json)`, results, "json")
        }
    } else {
        // run tests against the model(s)
        output.heading(3, `Test Runs with Models Under Test`)
        if (storeCompletions)
            output.itemValue(
                `stored completion model`,
                (await host.resolveLanguageModel(storeModel || MODEL_ALIAS_STORE))
                    ?.model || "store"
            )
        output.itemValue(`models under test`, modelsUnderTest.join(", "))

        output.heading(4, `Metrics`)
        for (const metric of files.metrics)
            output.detailsFenced(metricName(metric), metric.content, "markdown")

        if (evalModels?.length)
            output.itemValue(`evaluation models`, evalModels.join(", "))

        // only run tests if modelsUnderTest is defined
        let groundtruthResults: PromptPexTestResult[] = []
        if (groundtruthModel?.length) {
            output.heading(4, `Groundtruth Test Results`)
            groundtruthResults = await runTests(files, {
                runGroundtruth: true,
                ...options,
            })
        }

        // Copy groundtruth outputs into files.promptPexTests, save to disk
        if (groundtruthResults.length && Array.isArray(files.promptPexTests)) {
            for (let i = 0; i < files.promptPexTests.length; ++i) {
                if (
                    groundtruthResults[i] &&
                    typeof groundtruthResults[i].output === "string"
                ) {
                    files.promptPexTests[i].groundtruth =
                        groundtruthResults[i].output
                    files.promptPexTests[i].groundtruthModel = groundtruthModel
                    dbg(
                        `Set groundtruth for test ${i} to ${groundtruthResults[i].output}`
                    )
                    dbg(`test[${i}]:`, files.promptPexTests[i])
                }
            }
            dbg(`saving ${files.promptPexTests.length} tests with groundtruth`)
            const resc = JSON.stringify(files.promptPexTests, null, 2)
            files.tests.content = resc
            if (files.writeResults) await workspace.writeFiles(files.tests)
        }

        // groundtruth,only run tests if modelsUnderTest is defined
        let results = []
        if (modelsUnderTest?.length) {
            output.heading(4, `Test Results`)
            results = await runTests(files, { runGroundtruth: false, ...options })
        }

        // only measure metrics if eval is true
        if (evals) {
            let newResult: PromptPexTestResult
            // Evaluate metrics for all test results
            for (const testRes of results) {
                newResult = await evaluateTestMetrics(testRes, files, options)
                testRes.metrics = newResult.metrics
            }
            files.testOutputs.content = JSON.stringify(results, null, 2)

            if (files.writeResults)
                await workspace.writeText(
                    files.testOutputs.filename,
                    JSON.stringify(results, null, 2)
                )
            output.detailsFenced(`results (json)`, results, "json")
        }

        output.table(
            results.map(
                ({
                    scenario,
                    rule,
                    inverse,
                    model,
                    input,
                    output,
                    compliance: testCompliance,
                    metrics,
                }) => ({
                    model,
                    scenario,
                    input,
                    output,
                    ...Object.fromEntries(
                        Object.entries(
                            metrics && typeof metrics === "object" ? metrics : {}
                        ).map(([k, v]) => [
                            k,
                            v && typeof v === "object" && "content" in v
                                ? renderEvaluation(v as any)
                                : "",
                        ])
                    ),
                    compliance: renderEvaluationOutcome(testCompliance),
                    rule,
                    inverse: inverse ? "🔄" : "",
                })
            )
        )
    }

    output.heading(3, `Results Overview`)
    const { overview } = await computeOverview(files, { percent: true })
    output.table(overview)
    if (files.writeResults)
        await workspace.writeText(
            path.join(files.dir, "overview.csv"),
            CSV.stringify(overview, { header: true })
        )

    output.appendContent("\n\n---\n\n")

    if (files.writeResults) {
        saveContextState(files, path.join(files.dir, PROMPTPEX_CONTEXT))
        output.appendContent(
            `saving PromptPexContext to ${path.join(files.dir, PROMPTPEX_CONTEXT)}`
        )
    }

    reportPerf()
}