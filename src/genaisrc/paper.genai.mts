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
import type { PromptPexContext, PromptPexOptions } from "./src/types.mts"
import { diagnostics } from "./src/flags.mts"
import { generateInverseOutputRules } from "./src/inverserulesgen.mts"
import { checkConfirm } from "./src/confirm.mts"
const dbg = host.logger("promptpex:paper")

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
        cache: {
            type: "boolean",
            description: "Cache all LLM calls",
        },
        testRunCache: {
            type: "boolean",
            description: "Cache test run results",
        },
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
        baselineTests: {
            type: "boolean",
            description: "Generate baseline tests",
            default: true,
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
            minimum: 0,
        },
        maxRules: {
            type: "integer",
            description: "Maximum number of output rules to use",
            minimum: 1,
        },
        splitRules: {
            type: "boolean",
            description:
                "Split rules and inverse rules in separate prompts for generation",
            default: false,
        },
        maxRulesPerTestGeneration: {
            type: "integer",
            description: "Maximum number of rules to use per test generation",
        },
        testGenerations: {
            type: "integer",
            description: "Number of times to amplify the test generation",
            minimum: 1,
            maximum: 10,
        },
        modelsUnderTest: {
            type: "string",
            description: "List of models to evaluate",
        },
        out: { type: "string", description: "Output directory", default: "" },
    },
})

const { vars, files, output } = env
const {
    cache,
    testRunCache,
    disableSafety,
    force,
    out,
    evals,
    testsPerRule,
    runsPerTest,
    splitRules,
    maxRulesPerTestGeneration,
    testGenerations,
    baselineTests,
    maxTestsToRun,
} = vars as PromptPexOptions & {
    force?: boolean
    out?: string
    evals?: boolean
}

const prompts = await loadPromptContext(files, { disableSafety, out })
dbg(`loaded ${prompts.length} prompts`)

if (diagnostics) {
    dbg(`generating reports`)
    for (const files of prompts) {
        const res = await generateReports(files)
        console.log(res)
    }
    cancel("Diagnostics complete")
}

const modelsUnderTest: ModelType[] = env.vars.modelsUnderTest
    ?.split(/[;\n ,]/g)
    .map((model) => model.trim())
    .filter((m) => !!m)
if (!modelsUnderTest?.length)
    throw new Error(`no modelsUnderTest provided for evaluation`)
dbg(`modelsUnderTest: %o`, modelsUnderTest)

const res = []
const options = Object.freeze({
    cache,
    testRunCache,
    evalCache: true,
    disableSafety,
    force,
    modelsUnderTest,
    evals,
    testsPerRule,
    runsPerTest,
    maxTestsToRun,
    splitRules,
    maxRulesPerTestGeneration,
    testGenerations,
    compliance: true,
    baselineTests,
} satisfies PaperOptions)

output.heading(3, `Configuration`)
output.fence(YAML.stringify(options), "yaml")
await checkConfirm("config")

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

        dbg(`results for ${files.name}: %o`, res.at(-1))
        await checkConfirm("run")
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
        evals?: boolean
    }
) {
    const {
        disableSafety = false,
        force = false,
        modelsUnderTest,
        evals,
        baselineTests,
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
        await generateIntent(files, options)
    }

    outputFile(files.intent)
    await checkConfirm("intent")

    // generate input spec
    if (!files.inputSpec.content || force) {
        await generateInputSpec(files, options)
        files.tests.content = undefined
        files.testOutputs.content = undefined
    }

    outputFile(files.inputSpec)
    await checkConfirm("inputspec")

    // generate rules
    if (!files.rules.content || force) {
        await generateOutputRules(files, options)
        files.inverseRules.content = undefined
        files.tests.content = undefined
        files.testOutputs.content = undefined
        files.testEvals.content = undefined
        files.ruleEvals.content = undefined
    }

    outputFile(files.rules)
    await checkConfirm("rules")

    // generate inverse rules
    if (!files.inverseRules.content || force) {
        await generateInverseOutputRules(files, options)
        files.tests.content = undefined
        files.testOutputs.content = undefined
        files.testEvals.content = undefined
    }

    outputFile(files.inverseRules)
    await checkConfirm("inverse")

    // generate tests
    if (!files.tests.content || force) {
        await generateTests(files, options)
        files.testEvals.content = undefined
        files.testOutputs.content = undefined
    }

    outputFile(files.tests)
    await checkConfirm("tests")

    // generate baseline tests
    if (baselineTests) {
        if (!files.baselineTests.content || force) {
            await generateBaselineTests(files, options)
            files.testEvals.content = undefined
            files.testOutputs.content = undefined
        }
        outputFile(files.baselineTests)
        await checkConfirm("baseline")
    }

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
        await checkConfirm("evalbaseline")
    }

    await evaluateRulesGrounded(files, options)
    await generateReports(files)
    await checkConfirm("evalgrounded")

    if (modelsUnderTest?.length) {
        await evaluateRulesSpecAgreement(files, {
            ...options,
            model: modelsUnderTest[0],
        })
        await generateReports(files)
        await checkConfirm("evalrulespec")
    }

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
    await checkConfirm("evaltests")

    await runTests(files, options)
    await workspace.writeText(
        files.testOutputs.filename,
        files.testOutputs.content
    )
    outputFile(files.testOutputs)
    await checkConfirm("runtests")

    // final report
    const report = await generateReports(files)
    console.log(`  report: ${report}`)

    return files
}
