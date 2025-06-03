import { checkConfirm } from "./confirm.mts"
import { MODEL_ALIAS_EVAL } from "./constants.mts"
import { modelOptions, checkLLMEvaluation, metricName } from "./parsers.mts"
import { measure } from "./perf.mts"
import type {
    PromptPexContext,
    PromptPexTestResult,
    PromptPexOptions,
    PromptPexEvaluation,
    PromptPexPromptyFrontmatter,
} from "./types.mts"
const { generator } = env
const dbg = host.logger("promptpex:eval:metric")

export async function evaluateTestMetrics(
    testResult: PromptPexTestResult,
    files: PromptPexContext,
    options: PromptPexOptions
) {
    const { metrics } = files

    checkConfirm("metric")

    for (const evalModel of options.evalModelSet) {
        dbg(`evaluating ${metrics.length} metrics with eval model(s) %O`, evalModel)
        for (const metric of metrics) {
            const key = metricName(metric)+"|em|"+evalModel
            const res = await evaluateTestMetric(metric, evalModel, files, testResult, options)
            testResult.metrics[key] = res
        }
    }
    // After all evalModels, compute combined metric for each metric
    let evalModelSetArr: string[] = []
    if (typeof options.evalModelSet === "string") {
        evalModelSetArr = options.evalModelSet.split(";").map(s => s.trim()).filter(Boolean)
    } else if (Array.isArray(options.evalModelSet)) {
        evalModelSetArr = options.evalModelSet
    }
    for (const metric of metrics) {
        const n = metricName(metric)
        const keys = evalModelSetArr.map((evalModel) => `${n}|em|${evalModel}`)
        const metricResults = keys
            .map((k) => testResult.metrics[k])
            .filter((m) => m && typeof m.score === "number" && !isNaN(m.score))
        if (metricResults.length > 0 && evalModelSetArr.length > 1) {
            const avgScore = metricResults.reduce((sum, m) => sum + m.score, 0) / metricResults.length
            testResult.metrics[`${n}|em|combined`] = {
                score: avgScore,
                outcome: undefined,
                content: `Average of evalModels: ${keys.join(", ")}`,
            }
        }
    }
}

async function evaluateTestMetric(
    metric: WorkspaceFile,
    evalModel: ModelType,
    files: PromptPexContext,
    testResult: PromptPexTestResult,
    options: PromptPexOptions
): Promise<PromptPexEvaluation> {

    const moptions = modelOptions(evalModel, options)
    const content = MD.content(files.prompt.content)
    const metricMeta = MD.frontmatter(metric) as PromptPexPromptyFrontmatter
    const scorer = metricMeta?.tags?.includes("scorer")
    if (testResult.input === undefined)
        return {
            outcome: "unknown",
            content: "test result input missing",
        } satisfies PromptPexEvaluation
    if (testResult.output === undefined)
        return {
            outcome: "unknown",
            content: "test result output missing",
        } satisfies PromptPexEvaluation
    const parameters = {
        prompt: content.replace(/^(system|user):/gm, ""),
        intent: files.intent.content || "",
        inputSpec: files.inputSpec.content || "",
        rules: files.rules.content,
        input: testResult.input,
        output: testResult.output,
    }
    dbg(`metric: ${metric.filename} for %O`, {
        input: parameters.input,
        output: parameters.output,
        scorer,
    })
    const res = await measure("eval.metric", () =>
        generator.runPrompt(
            (ctx) => {
                // removes frontmatter
                ctx.importTemplate(metric, parameters, {
                    allowExtraArguments: true,
                })
            },
            {
                ...moptions,
                label: `${files.name}> evaluate metric ${metricName(metric)} ${testResult.model} ${testResult.input.slice(0, 42)}...`,
            }
        )
    )
    const evaluation = checkLLMEvaluation(res, { allowUnassisted: true })
    dbg(`metric eval: %o`, evaluation)
    return evaluation
}
