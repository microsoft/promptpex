import { generateBaselineTests } from "./src/baselinetestgen.mts"
import { generateInputSpec } from "./src/inputspecgen.mts"
import { generateIntent } from "./src/intentgen.mts"
import { generateInverseOutputRules } from "./src/inverserulesgen.mts"
import { loadPromptFiles } from "./src/loaders.mts"
import {
    parseBaselineTests,
    parseRules,
    parseRulesTests,
    parseTestResults,
} from "./src/parsers.mts"
import { initPerf, reportPerf } from "./src/perf.mts"
import { generateOutputRules } from "./src/rulesgen.mts"
import { generateTests } from "./src/testgen.mts"
import { runTests } from "./src/testrun.mts"
import type { PromptPexOptions } from "./src/types.mts"

script({
    accept: ".prompty",
    title: "test suite assuming very limited access to models",
    files: "samples/demo/demo.prompty",
    unlisted: true,
})

const { output } = env
const modelsUnderTest = process.env.PROMPTPEX_MODELS?.split(";").filter(
    (s) => !!s
)
if (!modelsUnderTest?.length)
    throw new Error("No models found in PROMPTPEX_MODELS")
const options: PromptPexOptions = {
    disableSafety: true,
    workflowDiagram: false,
    testsPerRule: 1,
    runsPerTest: 1,
    maxTestsToRun: 1,
    compliance: true,
    baselineTests: true,
    cache: true,
    modelsUnderTest,
    splitRules: false,
    maxRules: 2,
    maxRulesPerTestGeneration: 100,
    testGenerations: 1,
}

initPerf({ output })
const promptFile = env.files.find((f) => f.filename.endsWith(".prompty"))
const files = await loadPromptFiles(promptFile)

// generate intent
output.heading(3, "Intent")
await generateIntent(files, options)
output.fence(files.intent.content, "text")

output.heading(3, "Input Specification")
await generateInputSpec(files, options)
output.fence(files.inputSpec.content, "text")

output.heading(3, "Output Rules")
await generateOutputRules(files, options)
output.fence(files.rules.content, "text")
const rules = parseRules(files.rules.content)
if (!rules?.length) throw new Error("No rules found")

output.heading(3, "Inverse Output Rules")
await generateInverseOutputRules(files, options)
output.fence(files.inverseRules.content, "text")
const inverseRules = parseRules(files.inverseRules.content)
if (!inverseRules?.length) throw new Error("No inverse rules found")

output.heading(3, "Tests")
await generateTests(files, options)
output.fence(files.tests.content, "text")
const tests = parseRulesTests(files.tests.content).map(
    ({ scenario, testinput, expectedoutput }) => ({
        scenario,
        testinput,
        expectedoutput,
    })
)
if (!tests?.length) throw new Error("No tests found")
output.table(tests)

output.heading(3, "Baseline tests")
await generateBaselineTests(files, options)
output.fence(files.baselineTests.content, "text")
const baselineTests = parseBaselineTests(files)
if (!baselineTests?.length) throw new Error("No baseline tests found")
output.table(baselineTests)

output.heading(3, "Test results")
const testResultsParsed = await runTests(files, options)
if (!testResultsParsed) throw new Error("No test results found")

reportPerf()
