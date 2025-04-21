import type { OpenAI } from "openai"
import type { PromptPexContext } from "./types.mts"
import { metricName } from "./parsers.mts"
import { OK_CHOICE, OK_ERR_CHOICES } from "./constants.mts"
const dbg = host.logger("promptpex:evals")

export interface EvalsOptions {
    name?: string
    share_with_openai?: boolean
    model?: string
}

function metricToTestingCriteria(
    metric: WorkspaceFile,
    options?: { model?: string }
): OpenAI.Evals.EvalCreateParams.LabelModel | any {
    const { model = "gpt-4o" } = options
    const name = metricName(metric)
    const fm = MD.frontmatter(metric.content) as { tags?: string[] }
    const scorer = fm.tags?.includes("scorer")
    const content = MD.content(metric.content).replace(
        /\{\{\s*(?<id>\w+)\s*\}\}/g,
        (_, id) => {
            if (id === "output") return "{{ sample.output_text }}"
            return `{{ item.${id} }}`
        }
    )
    // {{ output }} -> {{ sample.output_text }}
    // {{ * }} -> {{ item.input }}
    const input = [
        {
            role: "system",
            content,
        },
    ]
    if (scorer)
        return {
            type: "score_model",
            name,
            model,
            input,
            pass_threshold: 50,
            range: [0, 100],
        }
    else
        return {
            type: "label_model",
            name,
            model,
            labels: OK_ERR_CHOICES,
            passing_labels: [OK_CHOICE],
            input,
        }
}

const METRIC_SCHEMA = {
    properties: {
        prompt: {
            type: "string",
        },
        intent: {
            type: "string",
        },
        inputSpec: {
            type: "string",
        },
        rules: {
            type: "string",
        },
        input: {
            type: "string",
        },
    },
    required: ["prompt", "intent", "inputSpec", "rules", "input"],
}

async function evalsCreateRequest(
    files: PromptPexContext,
    options?: EvalsOptions
) {
    const {
        name = `promptpex_${files.name}`,
        share_with_openai = false,
        model,
    } = options ?? {}
    const { metrics } = files
    const metricOptions = { model }
    const item_schema = METRIC_SCHEMA
    const res = {
        name,
        share_with_openai,
        data_source_config: {
            type: "custom",
            include_sample_schema: true,
            item_schema,
        },
        testing_criteria: metrics.map((metric) =>
            metricToTestingCriteria(metric, metricOptions)
        ),
    } satisfies OpenAI.Evals.EvalCreateParams
    dbg(`%O`, res)
    return res
}

export async function generateEvals(
    files: PromptPexContext,
    options?: EvalsOptions
) {
    const create = await evalsCreateRequest(files, options)
    await workspace.writeText(
        path.join(files.dir, "evals.create.json"),
        JSON.stringify(create, null, 2)
    )
}
