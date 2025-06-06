import { checkConfirm } from "./confirm.mts"
import { METRIC_SEPARATOR, MODEL_ALIAS_EVAL } from "./constants.mts"
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
): Promise<PromptPexTestResult> {
    const { metrics } = files

    checkConfirm("metric")


    // Remove all previous metrics before computing new ones
    testResult.metrics = {}

    for (const eModel of options.evalModel) {
        dbg(`evaluating ${metrics.length} metrics with eval model(s) %O`, eModel)
        for (const metric of metrics) {
            const key = metricName(metric)+METRIC_SEPARATOR+eModel
            const res = await evaluateTestMetric(metric, eModel, files, testResult, options)
            testResult.metrics[key] = res
        }
    }
    // After all evalModels, compute combined metric for each metric
    let evalModelArr: string[] = []
    if (typeof options.evalModel === "string") {
        evalModelArr = options.evalModel.split(";").map(s => s.trim()).filter(Boolean)
    } else if (Array.isArray(options.evalModel)) {
        evalModelArr = options.evalModel
    }
    for (const metric of metrics) {
        const n = metricName(metric)
        const keys = evalModelArr.map((eModel) => `${n}${METRIC_SEPARATOR}${eModel}`)
        const metricResults = keys
            .map((k) => testResult.metrics[k])
            .filter((m) => m && typeof m.score === "number" && !isNaN(m.score))
        if (metricResults.length > 0 && evalModelArr.length > 1) {
            const avgScore = metricResults.reduce((sum, m) => sum + m.score, 0) / metricResults.length
            testResult.metrics[`${n}${METRIC_SEPARATOR}combined`] = {
                score: avgScore,
                outcome: undefined,
                content: `Average of evalModels: ${keys.join(", ")}`,
            }
        }
    }
    return testResult
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
        groundtruth: testResult.groundtruth || "",
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
