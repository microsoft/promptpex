import {
    parseAllRules,
    parseBaselineTests,
    parseRuleEvals,
    parseRules,
    parseRulesTests,
    parseTestEvals,
    parseTestResults,
} from "./parsers.mts"
import { groupBy } from "genaiscript/runtime"
import { resolveRule } from "./resolvers.mts"
import type { PromptPexContext, PromptPexOptions } from "./types.mts"
const dbg = host.logger("promptpex:reports")
const dbgtests = host.logger("promptpex:reports:tests")

export function computeOverview(
    files: PromptPexContext,
    options?: PromptPexOptions & { percent?: boolean }
) {
    const { percent } = options || {}
    const testResults = parseTestResults(files)
    dbg(`testResults: %d`, testResults.length)
    const testEvals = parseTestEvals(files)
    dbg(`testEvals: %d`, testEvals.length)
    const rules = parseAllRules(files, options)
    dbg(`rules: %d`, rules.length)
    const ruleEvals = parseRuleEvals(files)
    dbg(`ruleEvals: %d`, ruleEvals.length)

    const defaultScenario = testResults.find((tr) => tr.scenario)?.scenario
    const testResultsPerModelsAndScenario = groupBy(
        testResults.filter((tr) => tr.scenario),
        (result) => `${result.model}:${result.scenario || defaultScenario}`
    )
    const overview = Object.entries(testResultsPerModelsAndScenario).map(
        ([key, results]) => {
            const { model, scenario, error } = results[0]
            const tests = results.filter((tr) => !tr.error && tr.rule)
            const errors =
                (error ? 1 : 0) + results.filter((tr) => tr.error).length
            const baseline = results.filter((tr) => !tr.error && !tr.rule)
            dbg(
                `${key}: ${tests.length} tests, ${baseline.length} baseline, ${errors} errors`
            )
            dbgtests("%O", tests)
            const norm = (v: number) =>
                tests.length === 0
                    ? "--"
                    : percent
                      ? Math.round((v / tests.length) * 100) + "%"
                      : v
            const bnorm = (v: number) =>
                baseline.length === 0
                    ? "--"
                    : percent
                      ? Math.round((v / baseline.length) * 100) + "%"
                      : v
            return {
                model,
                scenario,
                errors,
                tests: tests.length,
                ["tests compliant"]: norm(
                    tests.filter((tr) => tr.compliance === "ok").length
                ),
                ["tests compliance unknown"]: norm(
                    tests.filter(
                        (tr) =>
                            tr.compliance !== "ok" && tr.compliance !== "err"
                    ).length
                ),
                ["baseline compliant"]: bnorm(
                    baseline.filter((tr) => tr.compliance === "ok").length
                ),
                ["tests positive"]: tests.filter((tr) => !tr.inverse).length,
                ["tests positive compliant"]: tests.filter(
                    (tr) => tr.compliance === "ok"
                ).length,
                ["tests negative"]: tests.filter((tr) => tr.inverse).length,
                ["tests negative compliant"]: tests.filter(
                    (tr) => tr.compliance === "ok"
                ).length,
                baseline: baseline.length,
                ["tests valid"]: tests.filter(
                    (tr) =>
                        testEvals.find((te) => te.id === tr.id)?.validity ===
                        "ok"
                ).length,
                ["tests valid compliant"]: tests.filter(
                    (tr) =>
                        tr.compliance === "ok" &&
                        testEvals.find((te) => te.id === tr.id)?.validity ===
                            "ok"
                ).length,
            }
        }
    )
    return {
        testResults,
        testEvals,
        rules,
        ruleEvals,
        overview,
    }
}

async function generateMarkdownReport(files: PromptPexContext) {
    const tests = [
        ...parseRulesTests(files.tests.content),
        ...parseBaselineTests(files),
    ]
    const rules = parseRules(files.rules.content)
    const ruleEvals = parseRuleEvals(files)
    const groundedRuleEvals = ruleEvals.filter((r) => r.grounded === "ok")
    const inverseRules = parseRules(files.inverseRules.content)
    const testResults = parseTestResults(files)
    const ts = testResults.length
    const oks = testResults.filter((t) => t.compliance === "ok").length
    const errs = testResults.filter((t) => t.compliance === "err").length
    const unknowns = testResults.filter(
        (t) => t.compliance !== "ok" && t.compliance !== "err"
    ).length
    const rp = (n: number, t: number) =>
        `${n}/${t} (${Math.floor((n / t) * 100)}%)`

    const res: string[] = [
        `## ${files.name} ([json](./${files.dir}/report.json))`,
        ``,
        `- ${rules?.length ?? 0} rules, ${rp(groundedRuleEvals.length, ruleEvals.length)} grounded`,
        `- ${inverseRules?.length ?? 0} inverse rules`,
        `- ${tests.length ?? 0} tests, ${tests.filter((t) => t.baseline).length} baseline tests`,
        testResults?.length
            ? `- ${testResults?.length ?? 0} test results, ${rp(oks, ts)} oks, ${rp(errs, ts)} errs, ${rp(unknowns, ts)} unknowns`
            : undefined,
        ``,
    ].filter((l) => l !== undefined)

    res.push("### Overview", "")

    const { overview } = computeOverview(files, { percent: true })
    await workspace.writeText(
        path.join(files.dir, "overview.csv"),
        CSV.stringify(overview, { header: true })
    )
    res.push(
        "",
        `### [${path.basename(files.testOutputs.filename)}](./${path.basename(files.testOutputs.filename)})`,
        "",
        // Three more same columns with the same data but only for valid tests
        CSV.markdownify(overview)
    )

    const fence = "`````"
    const appendFile = (file: WorkspaceFile) => {
        const ext = path.extname(file.filename).slice(1)
        const headers =
            file === files.testOutputs
                ? ["model", "scenario", "rule", "input", "output", "compliance"]
                : file === files.tests
                  ? ["scenario", "testinput", "expectedoutput", "reasoning"]
                  : file === files.baselineTests
                    ? ["testinput"]
                    : file === files.testEvals
                      ? [
                            "scenario",
                            "rule",
                            "model",
                            "input",
                            "coverage",
                            "coverageUncertainty",
                            "validity",
                            "validityUncertainty",
                        ]
                      : file === files.ruleEvals
                        ? ["ruleid", "rule", "grounded"]
                        : file === files.baselineTestEvals
                          ? ["input", "validity"]
                          : undefined
        const lang =
            {
                prompty: "md",
            }[ext] || ext
        res.push(
            "",
            `### [${path.basename(file.filename)}](./${path.basename(file.filename)})`,
            ""
        )

        if (lang === "csv")
            res.push(CSV.markdownify(CSV.parse(file.content), { headers }))
        else if (lang === "json") {
            const data = parsers.JSON5(file.content)
            if (Array.isArray(data) && typeof data[0] === "object")
                res.push(CSV.markdownify(data, { headers }))
            else res.push("```json", file.content, "```")
        } else {
            let content = file.content
            if (file === files.rules) content = addLineNumbers(content, 1)
            else if (file === files.inverseRules)
                content = addLineNumbers(content, 1 + inverseRules.length)
            res.push(`${fence}${lang}`, content || "", `${fence}`, ``)
        }
    }

    for (const file of Object.values(files))
        if (typeof file === "object" && file.filename && file.content)
            appendFile(file as WorkspaceFile)

    return res.filter((l) => l !== undefined).join("\n")
}

function addLineNumbers(text: string, start: number) {
    return text
        .split(/\r?\n/gi)
        .map((l, i) => `${start + i}: ${l}`)
        .join("\n")
}

export async function generateJSONReport(files: PromptPexContext) {
    const prompt = files.prompt.content
    const inputSpec = files.inputSpec.content
    const errors: string[] = []
    const rules = parseRules(files.rules.content)
    const inverseRules = parseRules(files.inverseRules.content)
    const allRules = parseAllRules(files)
    const rulesTests = parseRulesTests(files.tests.content)
    const baseLineTests = parseBaselineTests(files)
    const testEvals = parseTestEvals(files)
    const ruleEvals = parseRuleEvals(files)
    const testResults = parseTestResults(files)
    if (files.tests.content && !rulesTests.length) {
        console.warn(`failed to parse tests in ${files.tests.filename}`)
        errors.push(`failed to parse tests in ${files.tests.filename}`)
    }

    const tests = [...rulesTests, ...baseLineTests].map((test) => {
        const rule = resolveRule(allRules, test)
        if (!rule && !test.baseline)
            errors.push(
                `test '${test.ruleid}' references non-existent rule in ${files.tests.filename}`
            )
        const res: any = {
            ...rule,
            ...test,
        }
        return res
    })

    return {
        prompt,
        inputSpec,
        rules,
        inverseRules,
        ruleEvals,
        tests,
        testEvals,
        testResults,
        errors: errors.length ? errors : undefined,
    }
}

export async function generateReports(files: PromptPexContext) {
    const jsonreport = await generateJSONReport(files)
    const fnjson = path.join(files.dir, "report.json")
    dbg(`report (json): ${fnjson}`)
    await workspace.writeText(fnjson, JSON.stringify(jsonreport, null, 2))

    const mdreport = await generateMarkdownReport(files)
    const fn = path.join(files.dir, "README.md")
    dbg(`report (markdown): ${fn}`)
    await workspace.writeText(fn, mdreport)
    return fn
}
