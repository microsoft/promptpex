import { generateBaselineTests } from "./src/baselinetestgen.mts"
import { evaluateBaselineTests } from "./src/baselinetestseval.mts"
import { generateInputSpec } from "./src/inputspecgen.mts"
import { generateIntent } from "./src/intentgen.mts"
import { outputFile } from "./src/output.mts"
import { loadPromptContext } from "./src/loaders.mts"
import { computeOverview, generateReports } from "./src/reports.mts"
import { generateOutputRules } from "./src/rulesgen.mts"
import { evaluateRulesGrounded } from "./src/rulesgroundeness.mts"
import { evaluateRulesSpecAgreement } from "./src/rulesspecagreement.mts"
import { generateTests } from "./src/testgen.mts"
import { evaluateTestsQuality } from "./src/testquality.mts"
import { runTests } from "./src/testrun.mts"
import { PromptPexContext, PromptPexOptions } from "./src/types.mts"
import { parseTestResults } from "./src/parsers.mts"
import { diagnostics } from "./src/flags.mts"
import { generateInverseOutputRules } from "./src/inverserulesgen.mts"

type PaperOptions = PromptPexOptions & {
    force?: boolean
    evals?: boolean
}

script({
    title: "PromptPex Paper Evaluation",
    description:
        "Evaluate the performance of PromptPex and generate results for the paper.",
    files: ["samples/speech-tag/speech-tag.prompty"],
    accept: ".prompty",
    unlisted: true,
    parameters: {
        disableSafety: {
            type: "boolean",
            description:
                "Do not include safety system prompts and do not run safety content service",
            default: false,
        },
        force: {
            type: "boolean",
            description: "Force overwrite of existing files",
            default: false,
        },
        evals: {
            type: "boolean",
            description: "Evaluate quality of generated tests",
            default: true,
        },
        testsPerRule: {
            type: "integer",
            description: "Number of tests to generate per rule",
            minimum: 1,
            maximum: 10,
            default: 3,
        },
        runsPerTest: {
            type: "integer",
            description: "Number of runs to execute per test",
            minimum: 1,
            maximum: 100,
            default: 1,
        },
        maxTestsToRun: {
            type: "integer",
            description: "Maximum number of tests to runs",
        },
        models: { type: "string", description: "List of models to evaluate" },
        out: { type: "string", description: "Output directory", default: "" },
    },
})

const { vars, files, output } = env
const { disableSafety, force, out, evals, testsPerRule, runsPerTest } =
    vars as PromptPexOptions & {
        force?: boolean
        out?: string
        evals?: boolean
    }
let maxTestsToRun = diagnostics ? 2 : vars.maxTestsToRun

const prompts = await loadPromptContext(files, { disableSafety, out })
const modelsUnderTest = env.vars.models
    ?.split(/[;\n ,]/g)
    .map((model) => model.trim())
if (!modelsUnderTest?.length)
    throw new Error(`no modelsUnderTest provided for evaluation`)

if (diagnostics) {
    for (const files of prompts) {
        parseTestResults(files) // parse early for warnings
        await generateReports(files)
    }
}

const res = []
const options = Object.freeze({
    disableSafety,
    force,
    modelsUnderTest,
    evals,
    evalCache: true,
    testsPerRule,
    runsPerTest,
    maxTestsToRun,
    compliance: true,
    baselineTests: true,
} satisfies PaperOptions)

output.heading(3, `Configuration`)
output.fence(YAML.stringify(options), "yaml")

for (const files of prompts) {
    try {
        const ctx = await generate(files, options)
        const { testEvals, rules, ruleEvals, overview } = computeOverview(ctx, {
            percent: false,
        })
        res.push({
            prompt: files.name,
            rules: rules.filter((r) => !r.inverse).length,
            ["rules grounded"]: ruleEvals.filter((g) => g.grounded === "ok")
                .length,
            tests: testEvals.length,
            ...Object.fromEntries(
                overview.map((o) => [o.model, o["tests compliant"]])
            ),
        })
    } catch (e) {
        console.error(e)
        console.debug(e.stack)
    }
}

res.sort((a, b) => a.prompt.localeCompare(b.prompt))
await workspace.writeText(
    path.join(out, "evals/README.md"),
    `# Eval summary
  
## Test Results

- % represent compliance rate

${CSV.markdownify(res)}

`
)

async function generate(
    files: PromptPexContext,
    options?: PromptPexOptions & {
        force?: boolean
        models?: ModelType[]
        evals?: boolean
    }
) {
    const {
        disableSafety = false,
        force = false,
        models,
        evals,
    } = options || {}
    const { output } = env

    output.heading(3, `generating tests for ${files.name}`)
    output.detailsFenced(`prompt under test`, files.prompt)
    output.itemValue(`dir`, files.dir)

    if (!disableSafety) {
        const contentSafety = await host.contentSafety()
        if (!contentSafety) {
            output.warn(`content safety not configured, skipping`)
        } else {
            if (
                (await contentSafety.detectHarmfulContent?.(files.prompt))
                    ?.harmfulContentDetected
            )
                throw new Error(`Harmful content detected in prompt`)
            if (
                (await contentSafety.detectPromptInjection?.(files.prompt))
                    ?.attackDetected
            )
                throw new Error(`Harmful content detected in rules`)
        }
    }

    // generate intent
    if (!files.intent.content || force) {
        files.intent.content = await generateIntent(files, options)
        await workspace.writeText(files.intent.filename, files.intent.content)
    }

    outputFile(files.intent)

    // generate input spec
    if (!files.inputSpec.content || force) {
        files.inputSpec.content = await generateInputSpec(files, options)
        await workspace.writeText(
            files.inputSpec.filename,
            files.inputSpec.content
        )
        files.tests.content = undefined
        files.testOutputs.content = undefined
    }

    outputFile(files.inputSpec)

    // generate rules
    if (!files.rules.content || force) {
        files.rules.content = await generateOutputRules(files, options)
        await workspace.writeText(files.rules.filename, files.rules.content)
        files.inverseRules.content = undefined
        files.tests.content = undefined
        files.testOutputs.content = undefined
        files.testEvals.content = undefined
        files.ruleEvals.content = undefined
    }

    outputFile(files.rules)

    // generate inverse rules
    if (!files.inverseRules.content || force) {
        files.inverseRules.content = await generateInverseOutputRules(
            files,
            options
        )
        await workspace.writeText(
            files.inverseRules.filename,
            files.inverseRules.content
        )
        files.tests.content = undefined
        files.testOutputs.content = undefined
        files.testEvals.content = undefined
    }

    outputFile(files.inverseRules)

    // generate tests
    if (!files.tests.content || force) {
        files.tests.content = await generateTests(files, options)
        await workspace.writeText(files.tests.filename, files.tests.content)
        files.testEvals.content = undefined
        files.testOutputs.content = undefined
    }

    outputFile(files.tests)

    // generate baseline tests
    if (!files.baselineTests.content || force) {
        files.baselineTests.content = await generateBaselineTests(
            files,
            options
        )
        await workspace.writeText(
            files.baselineTests.filename,
            files.baselineTests.content
        )
        files.testEvals.content = undefined
        files.testOutputs.content = undefined
    }

    outputFile(files.baselineTests)

    await generateReports(files)

    if (!evals) return files

    if (!files.baselineTestEvals.content || force) {
        files.baselineTestEvals.content = await evaluateBaselineTests(files, {
            force: force,
        })
        await workspace.writeText(
            files.baselineTestEvals.filename,
            files.baselineTestEvals.content
        )
    }

    await evaluateRulesGrounded(files, options)
    await generateReports(files)

    await evaluateRulesSpecAgreement(files, { ...options, model: models[0] })
    await generateReports(files)

    // test exhaustiveness
    const tc = await evaluateTestsQuality(files, {
        ...(options || {}),
        force,
    })
    if (tc !== files.testEvals.content) {
        files.testEvals.content = tc
        await workspace.writeText(
            files.testEvals.filename,
            files.testEvals.content
        )
        await generateReports(files)
    }

    outputFile(files.testEvals)

    files.testOutputs.content = await runTests(files, {
        ...options,
        force,
    })
    await workspace.writeText(
        files.testOutputs.filename,
        files.testOutputs.content
    )
    outputFile(files.testOutputs)

    // final report
    const report = await generateReports(files)
    console.log(`  report: ${report}`)

    return files
}
