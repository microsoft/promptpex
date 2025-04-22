import type { OpenAI } from "openai"
import type {
    PromptPexContext,
    PromptPexOptions,
    PromptPexTest,
} from "./types.mts"
import { metricName, parseTestEvals } from "./parsers.mts"
import { OK_CHOICE, OK_ERR_CHOICES } from "./constants.mts"
const dbg = host.logger("promptpex:evals")
const { output } = env

export interface EvalsOptions {
    name?: string
    model?: string
    upload?: boolean
}

function toEvalTemplate(file: WorkspaceFile) {
    const content = MD.content(file.content)
        .replace(/\{\{\s*(?<id>\w+)\s*\}\}/g, (_, id) => {
            if (id === "output") return "{{ sample.output_text }}"
            return `{{ item.${id} }}`
        })
        .replace(/^(system|user):/gm, "")
    return content
}

function metricToTestingCriteria(
    metric: WorkspaceFile,
    options?: { model?: string }
): OpenAI.Evals.EvalCreateParams.LabelModel | any {
    const { model = "gpt-4o" } = options
    const name = metricName(metric)
    const fm = MD.frontmatter(metric.content) as { tags?: string[] }
    const scorer = fm.tags?.includes("scorer")
    const content = toEvalTemplate(metric)
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
    type: "object",
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
    options?: PromptPexOptions & EvalsOptions
) {
    const {
        name = `promptpex_${files.name}`,
        model,
        createEvalRun,
    } = options ?? {}
    const { metrics, inputs } = files
    const metricOptions = { model }
    const body = {
        name,
        data_source_config: {
            type: "custom",
            include_sample_schema: true,
            item_schema: {
                type: "object",
                properties: {
                    ...inputs,
                    ...METRIC_SCHEMA.properties,
                },
                required: [...Object.keys(inputs), ...METRIC_SCHEMA.required],
            },
        },
        testing_criteria: metrics.map((metric) =>
            metricToTestingCriteria(metric, metricOptions)
        ),
    } satisfies OpenAI.Evals.EvalCreateParams
    dbg(`%O`, body)

    await workspace.writeText(
        path.join(files.dir, "evals.create.json"),
        JSON.stringify(body, null, 2)
    )

    const apiKey = process.env.OPENAI_API_KEY
    if (createEvalRun && apiKey) {
        dbg(`uploading evals to OpenAI`)
        const apiBase = process.env.OPENAI_API_BASE || "https://api.openai.com/"
        const res = await fetch(apiBase + `v1/evals`, {
            method: "POST",
            headers: {
                Authorization: `Bearer ${apiKey}`,
                "Content-Type": "application/json",
            },
            body: JSON.stringify(body),
        })
        dbg(`res: %d %s`, res.status, res.statusText)
        if (!res.ok) {
            output.fence(await res.text())
            throw new Error(`failed to upload evals: ${res.statusText}`)
        }
        const evalDef = (await res.json()) as { id: string }
        dbg(`eval: %O`, evalDef)
        output.detailsFenced(`eval object`, evalDef, "json")
        return evalDef.id
    }

    return undefined
}

async function evalsCreateRun(
    evalId: string,
    files: PromptPexContext,
    tests: PromptPexTest[],
    options?: PromptPexOptions
) {
    const { createEvalRun } = options ?? {}
    const content = toEvalTemplate(files.prompt)
    const parameters = {
        prompt: content,
        intent: files.intent.content || "",
        inputSpec: files.inputSpec.content || "",
        rules: files.rules.content,
    }

    const body = {
        name: `promptpex_${files.name}`,
        data_source: {
            type: "completions",
            input_messages: {
                type: "template",
                template: [
                    {
                        type: "message",
                        role: "system",
                        content: {
                            type: "input_text",
                            text: content,
                        },
                    },
                ],
            },
            model: "gpt-4o-mini",
            source: {
                type: "file_content",
                content: tests.map((test) => ({
                    item: {
                        ...parameters,
                        input: test.testinput,
                        ...JSON.parse(test.testinput),
                    },
                })),
            },
        },
    }

    dbg(`%O`, body)
    await workspace.writeText(
        path.join(files.dir, "evals.run.json"),
        JSON.stringify(body, null, 2)
    )

    const apiKey = process.env.OPENAI_API_KEY
    if (createEvalRun && apiKey && evalId && tests.length > 0) {
        dbg(`uploading eval run to OpenAI`)
        const apiBase = process.env.OPENAI_API_BASE || "https://api.openai.com/"
        const res = await fetch(apiBase + `v1/evals/${evalId}/runs`, {
            method: "POST",
            headers: {
                Authorization: `Bearer ${apiKey}`,
                "Content-Type": "application/json",
            },
            body: JSON.stringify(body),
        })
        dbg(`res: %d %s`, res.status, res.statusText)
        if (!res.ok) {
            output.fence(await res.text())
            throw new Error(`failed to upload eval run: ${res.statusText}`)
        }
        const run = (await res.json()) as any
        output.detailsFenced(`eval run object`, run, "json")
    }
}

export async function generateEvals(
    files: PromptPexContext,
    tests: PromptPexTest[],
    options?: PromptPexOptions & EvalsOptions
) {
    const evalId = await evalsCreateRequest(files, options)
    if (tests?.length) await evalsCreateRun(evalId, files, tests, options)
}
