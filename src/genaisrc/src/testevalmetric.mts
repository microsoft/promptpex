import { checkConfirm } from "./confirm.mts"
import { MODEL_ALIAS_EVAL } from "./constants.mts"
import { modelOptions, checkLLMEvaluation, metricName } from "./parsers.mts"
import { measure } from "./perf.mts"
import type {
    PromptPexContext,
    PromptPexTestResult,
    PromptPexOptions,
    PromptPexEvaluation,
} from "./types.mts"
const { generator } = env
const dbg = host.logger("promptpex:eval:metric")

export async function evaluateTestMetrics(
    testResult: PromptPexTestResult,
    files: PromptPexContext,
    options: PromptPexOptions
) {
    const { metrics } = files
    dbg(`evaluating ${metrics.length} metrics`)
    checkConfirm("metric")

    for (const metric of metrics) {
        const res = await evaluateTestMetric(metric, files, testResult, options)
        testResult.metrics[metricName(metric)] = res
    }
}

const outputFormat = `
### Evaluation:
Ensure your response is valid JSON using the following JSON schema:

{
    "type": "object",
    "properties": {
        "explanation": {
            "type": "string",
            "description": "Explain reasoning behind generating the score based on the criteria outlined in the instruction. Only keep a minimum draft with 5 words at most."
        },
        "score": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100,
            "description": "Provide a score from 0 to 100 based on the criteria of the chatbot output as defined above"
        }
    },
    "required": ["explanation", "score"],
}

`

async function evaluateTestMetric(
    metric: WorkspaceFile,
    files: PromptPexContext,
    testResult: PromptPexTestResult,
    options: PromptPexOptions
): Promise<PromptPexEvaluation> {
    const { evalModel = MODEL_ALIAS_EVAL } = options || {}
    const moptions = modelOptions(evalModel, options)
    const content = MD.content(files.prompt.content)
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
        outputFormat,
    }
    dbg(`metric: ${metric.filename} for %O`, {
        input: parameters.input,
        output: parameters.output,
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
