import { modelOptions, checkLLMResponse, parseTestResults, parseOKERR, checkLLMEvaluation } from "./parsers.mts"
import { measure } from "./perf.mts"
import type {
    PromptPexContext,
    PromptPexTestResult,
    PromptPexOptions,
    PromptPexEvaluation,
} from "./types.mts"
const { generator } = env
const dbg = host.logger("promptpex:eval:metric")

export function metricName(metric: WorkspaceFile) {
    return path.basename(metric.filename).replace(/\.metric\.prompty$/, "")
}

export async function evaluateTestMetrics(files: PromptPexContext, options: PromptPexOptions) {
    const { metrics } = files
    const testResults = await parseTestResults(files)
    for (const testResult of testResults) {
        for (const metric of metrics) {
            const res = await evaluateTestMetric(
                metric,
                files,
                testResult,
                options
            )
            testResult.metrics[metricName(metric)] = res
        }
    }
}

async function evaluateTestMetric(
    metric: WorkspaceFile,
    files: PromptPexContext,
    testResult: PromptPexTestResult,
    options: PromptPexOptions
): Promise<PromptPexEvaluation> {
    const { metricsEvalModel: customTestEvalModel = "usereval" } =
        options || {}
    dbg(metric.filename)
    const moptions = modelOptions(customTestEvalModel, options)

    const content = MD.content(files.prompt.content)
    const res = await measure("eval.metric", () =>
        generator.runPrompt(
            (ctx) => {
                // removes frontmatter
                ctx.importTemplate(
                    metric,
                    {
                        prompt: content.replace(/^(system|user):/gm, ""),
                        intent: files.intent.content,
                        inputSpec: files.inputSpec.content,
                        rules: files.rules.content,
                        input: testResult.input,
                        output: testResult.output,
                    },
                    { allowExtraArguments: true }
                )
            },
            {
                ...moptions,
                label: `${files.name}> evaluate metric ${testResult.model} ${testResult.input.slice(0, 42)}...`,
            }
        )
    )
    const evaluation = checkLLMEvaluation(res, { allowUnassisted: true })
    return evaluation
}