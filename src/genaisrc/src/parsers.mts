import { diagnostics } from "./flags.mts"
import type {
    PromptPexContext,
    PromptPexModelAliases,
    PromptPexOptions,
    PromptPexRuleEval,
    PromptPexTest,
    PromptPexTestEval,
    PromptPexTestResult,
} from "./types.mts"

const { output } = env

export function modelOptions(
    modelAlias: PromptPexModelAliases,
    options: PromptPexOptions
): PromptGeneratorOptions {
    const { temperature = 1, modelAliases } = options || {}
    return {
        model: modelAliases?.[modelAlias] || modelAlias,
        temperature,
        responseType: "text",
        // RAI must be checked by an external service
        system: [],
    }
}

export function parseInputs(file: WorkspaceFile) {
    const frontmatter = MD.frontmatter(file.content) || {}
    const inputs = frontmatter["inputs"] || {}
    // under specified inputs, try to find any missing inputs
    // using regex
    if (!Object.keys(inputs).length) {
        file.content.replace(/{{\s*([^}\s]+)\s*}}/g, (_, key) => {
            inputs[key] = { type: "string" }
            return ""
        })
    }

    return inputs
}

export function isUnassistedResponse(text: string) {
    return /i can't assist with that|i'm sorry/i.test(text)
}

export function checkLLMResponse(res: RunPromptResult) {
    if (res.error) throw new Error(res.error.message)
    if (isUnassistedResponse(res.text))
        throw new Error("LLM failed to generate response")
    return parsers.unfence(res.text, "")
}

export function tidyRules(text: string) {
    if (isUnassistedResponse(text)) return ""
    return parsers
        .unfence(text, "")
        .split(/\n/g)
        .map((line) => line.replace(/^(\d+\.|_|-|\*)\s+/i, "")) // unneded numbering
        .filter((s) => !!s)
        .filter((s) => !/^\s*Rules:\s*$/i.test(s))
        .join("\n")
}

export function tidyRulesFile(file: WorkspaceFile) {
    if (file?.content) file.content = tidyRules(file.content)
    return file
}

export function parseRules(rules: string) {
    return rules
        ? tidyRules(rules)
              .split(/\r?\n/g)
              .map((l) => l.trim())
              .filter((l) => !!l)
        : []
}

export function parseRulesTests(text: string): PromptPexTest[] {
    if (!text) return []
    if (isUnassistedResponse(text)) return []
    const content = text.trim().replace(/\\"/g, '""')
    const rulesTests = content
        ? (CSV.parse(content, {
              delimiter: ",",
              repair: true,
          }) as PromptPexTest[])
        : []
    return rulesTests.map((r) => ({ ...r, testinput: r.testinput || "" }))
}

export function parseTestResults(
    files: PromptPexContext
): PromptPexTestResult[] {
    const rules = parseRules(files.rules.content)
    const res = (parsers.JSON5(files.testOutputs.content) ||
        []) as PromptPexTestResult[]
    res.forEach((r) => {
        r.inverse =
            r.ruleid !== null && parseInt(r.ruleid as any) > rules.length
    })
    for (const r of res.filter((r) => !r.error && !r.model)) {
        output.warn(
            `missing 'model' for test result ${r.id} in ${files.testOutputs.filename}`
        )
        if (diagnostics)
            throw new Error(`missing 'model' for test result ${r.id}`)
    }
    for (const r of res) if (isNaN(r.ruleid)) r.ruleid = null
    return res
}

export function cleanBaselineTests(content: string) {
    const tests = parsers
        .unfence(content, "")
        .split(/\s*===\s*/g)
        .map((l) =>
            l
                .trim()
                .replace(/^(#+\s+)?(test case)( \d+)?:?$/gim, "")
                .trim()
        )
        .filter((l) => !!l)
    return tests
}

export function parseBaselineTests(files: PromptPexContext): PromptPexTest[] {
    const tests = cleanBaselineTests(files.baselineTests.content).map(
        (l) => ({ testinput: l, baseline: true }) satisfies PromptPexTest
    )
    return tests
}

export function parseTestEvals(files: PromptPexContext) {
    return parsers.JSON5(files.testEvals.content, {
        defaultValue: [],
    }) as PromptPexTestEval[]
}

export function parseRuleEvals(files: PromptPexContext) {
    return parsers.JSON5(files.ruleEvals.content, {
        defaultValue: [],
    }) as PromptPexRuleEval[]
}

export function parsBaselineTestEvals(files: PromptPexContext) {
    return parsers.JSON5(files.baselineTestEvals.content, {
        defaultValue: [],
    }) as PromptPexTestEval[]
}

export function parseAllRules(
    files: PromptPexContext
): { rule: string; inverse?: boolean }[] {
    const rules = parseRules(files.rules.content)
    const inverseRules = parseRules(files.inverseRules.content)
    const allRules = [
        ...rules.map((rule) => ({ rule })),
        ...inverseRules.map((rule) => ({ rule, inverse: true })),
    ]
    return allRules
}

export function parseOKERR(text: string): "err" | "ok" | undefined {
    return /(^|\W)ERR\s*$/.test(text)
        ? "err"
        : /(^|\W)OK\s*$/.test(text)
          ? "ok"
          : undefined
}
