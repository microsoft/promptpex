import { diagnostics } from "./flags.mts"
import type {
    PromptPexContext,
    PromptPexEvalResultType,
    PromptPexEvaluation,
    PromptPexModelAliases,
    PromptPexOptions,
    PromptPexRuleEval,
    PromptPexTest,
    PromptPexTestEval,
    PromptPexTestResult,
} from "./types.mts"
const dbg = host.logger("promptpex:parsers")

const { output } = env

export function metricName(metric: WorkspaceFile) {
    return path.basename(metric.filename).replace(/\.metric\.prompty$/, "") 
}

export function modelOptions(
    modelAlias: PromptPexModelAliases,
    options: PromptPexOptions
): PromptGeneratorOptions {
    const { temperature = 1, modelAliases, cache } = options || {}
    return {
        model: modelAliases?.[modelAlias] || modelAlias,
        temperature,
        system: [],
        cache,
    }
}

export function isUnassistedResponse(text: string) {
    return /i can't assist with that|i'm sorry/i.test(text)
}

export function checkLLMResponse(
    res: RunPromptResult,
    options?: { allowUnassisted: boolean }
) {
    if (!res) throw new Error("LLM response is undefined")
    if (res.error) {
        dbg(`LLM error: %O`, res.error)
        output.warn(`LLM error: ${res.error.message}`)
        output.fence(res.error, "yaml")
        throw new Error(res.error.message)
    }
    if (isUnassistedResponse(res.text)) {
        if (!options?.allowUnassisted)
            throw new Error("LLM failed to generate response")
        else output.warn(`unassisted response: ${res.text}`)
    }
    return parsers.unfence(res.text, "")
}

export function checkLLMEvaluation(
    res: RunPromptResult,
    options?: { allowUnassisted: boolean }
): PromptPexEvaluation {
    const content = checkLLMResponse(res, options)
    return {
        content,
        uncertainty: res.uncertainty,
        perplexity: res.perplexity,
        outcome: parseOKERR(content),
    } satisfies PromptPexEvaluation
}

export function tidyRules(text: string) {
    if (isUnassistedResponse(text)) return ""
    return parsers
        .unfence(text, "")
        .split(/\n/g)
        .map((line) => line.replace(/^(\d+\.|_|-|\*)\s+/i, "")) // unneded numbering
        .filter((s) => !!s)
        .filter((s) => !/^\s*Rules:\s*$/i.test(s))
        .map((line) => line.replace(/^\["(.*)"\]$/, (_, rule) => rule)) // ["..."]
        .join("\n")
}

export function tidyRulesFile(file: WorkspaceFile) {
    if (file?.content) file.content = tidyRules(file.content)
    return file
}

export function parseRules(rules: string, options?: PromptPexOptions) {
    const { maxRules } = options || {}
    const res = rules
        ? tidyRules(rules)
            .split(/\r?\n/g)
            .map((l) => l.trim())
            .filter((l) => !!l)
        : []
    return maxRules > 0 ? res.slice(0, maxRules) : res
}

export function parseRulesTests(text: string): PromptPexTest[] {
    if (!text) return []
    if (isUnassistedResponse(text)) return []
    const rulesTests: PromptPexTest[] = parsers.JSON5(text) || []
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
        r.metrics = r.metrics || {}
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
    if (!content) return []
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
    return (parsers.JSON5(files.testEvals.content, {
        defaultValue: [],
    }) || []) as PromptPexTestEval[]
}

export function parseRuleEvals(files: PromptPexContext) {
    return (parsers.JSON5(files.ruleEvals.content, {
        defaultValue: [],
    }) || []) as PromptPexRuleEval[]
}

export function parsBaselineTestEvals(files: PromptPexContext) {
    return (parsers.JSON5(files.baselineTestEvals.content, {
        defaultValue: [],
    }) || []) as PromptPexTestEval[]
}

export function parseAllRules(
    files: PromptPexContext,
    options?: PromptPexOptions
) {
    const rules = parseRules(files.rules.content, options)
    const inverseRules = parseRules(files.inverseRules.content, options)
    const allRules = [
        ...rules.map((rule) => ({ rule, inverse: false })),
        ...inverseRules.map((rule) => ({ rule, inverse: true })),
    ]
    return allRules
}

export function parseOKERR(text: string): PromptPexEvalResultType | undefined {
    return /(^|\W)ERR\s*$/.test(text)
        ? "err"
        : /(^|\W)OK\s*$/.test(text)
            ? "ok"
            : "unknown"
}
