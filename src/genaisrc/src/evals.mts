import type { OpenAI } from "openai"
import type {
    PromptPexContext,
    PromptPexOptions,
    PromptPexPromptyFrontmatter,
    PromptPexTest,
} from "./types.mts"
import { metricName } from "./parsers.mts"
import { OK_CHOICE, OK_ERR_CHOICES } from "./constants.mts"
const dbg = host.logger("promptpex:evals")
const { output } = env

// OpenAI: https://platform.openai.com/docs/api-reference/evals
// Azure OpenAI: https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/evaluations?tabs=question-eval-input

async function toEvalTemplate(file: WorkspaceFile) {
    const patched = {
        filename: file.filename,
        content: file.content.replace(/\{\{\s*(?<id>\w+)\s*\}\}/g, (_, id) => {
            if (id === "output") return "{{sample.output_text}}"
            return `{{item.${id}}}`
        }),
    }
    const pp = await parsers.prompty(patched)
    return {
        input: pp.messages,
        text: MD.content(patched.content).replace(
            /^(system|user|assistant):/gm,
            ""
        ),
    }
}

async function metricToTestingCriteria(
    metric: WorkspaceFile,
    options?: { model?: string }
): Promise<OpenAI.Evals.EvalCreateParams.LabelModel | any> {
    const { model = "gpt-4o" } = options
    const name = metricName(metric)
    const fm = MD.frontmatter(metric.content) as PromptPexPromptyFrontmatter
    const scorer = fm.tags?.includes("scorer")
    const { input } = await toEvalTemplate(metric)
    dbg(`input: %O`, input)
    // {{output}} -> {{sample.output_text}}
    // {{*}} -> {{item.input}}
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
            input: input.map(({ content, ...rest }) => ({
                type: "message",
                content: content as string,
                ...rest,
            })),
        } satisfies OpenAI.Evals.EvalCreateParams.LabelModel
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
    options?: PromptPexOptions
) {
    const { createEvalRuns } = options ?? {}
    const name = `${files.name} (promptpex)`
    const { metrics, inputs } = files
    const metricOptions = { model: "gpt-4o" } // TODO: support other?
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
        testing_criteria: await Promise.all(
            metrics.map((metric) =>
                metricToTestingCriteria(metric, metricOptions)
            )
        ),
        metadata: {
            promptpex: files.versions.promptpex,
        },
    } satisfies OpenAI.Evals.EvalCreateParams
    output.detailsFenced(`evals.create.json`, body, "json")
    if (files.writeResults)
        await workspace.writeText(
            path.join(files.dir, "evals.create.json"),
            JSON.stringify(body, null, 2)
        )

    let createUrl: string | undefined
    let createHeaders: Record<string, string> | undefined
    let createDashboardUrl: string | undefined

    // OpenAI
    const openaiApiKey: string = process.env.OPENAI_API_KEY
    const azureEndpoint: string =
        process.env.AZURE_OPENAI_ENDPOINT || process.env.AZURE_OPENAI_API_BASE
    if (createEvalRuns && openaiApiKey) {
        dbg(`uploading evals to OpenAI`)
        const apiBase = process.env.OPENAI_API_BASE || "https://api.openai.com/"
        createUrl = apiBase + `v1/evals`
        createHeaders = {
            Authorization: `Bearer ${openaiApiKey}`,
            "Content-Type": "application/json",
        }
        createDashboardUrl = "https://platform.openai.com/evaluations/"
    }
    // Azure OpenAI
    else if (createEvalRuns && azureEndpoint) {
        dbg(`uploading evals to Azure OpenAI`)
        createUrl = azureEndpoint.replace(/\/$/, "") + `/openai/evals`
        const token = await azureGetToken()
        createHeaders = {
            "Content-Type": "application/json",
            "api-key": token,
        }
    }

    if (createUrl) {
        dbg(`create: %s`, createUrl)
        const res = await fetch(createUrl, {
            method: "POST",
            headers: createHeaders,
            body: JSON.stringify(body),
        })
        dbg(`res: %d %s`, res.status, res.statusText)
        if (!res.ok) {
            output.fence(await res.text())
            throw new Error(`failed to upload evals: ${res.statusText}`)
        }
        const evalDef = (await res.json()) as { id: string }
        dbg(`eval: %O`, evalDef)
        if (createDashboardUrl)
            output.itemLink(
                "eval dashboard",
                `${createDashboardUrl}${evalDef.id}`
            )
        else output.itemValue(`eval id`, evalDef.id)
        output.detailsFenced(`eval object`, evalDef, "json")
        return evalDef.id
    }

    return undefined
}

async function azureGetToken(): Promise<string> {
    const { DefaultAzureCredential } = await import("@azure/identity")
    const credential = new DefaultAzureCredential()
    const tokenResponse = await credential.getToken(
        "https://cognitiveservices.azure.com/.default"
    )
    dbg(`Azure token: %s`, tokenResponse.token)
    return tokenResponse.token
}

async function evalsCreateRun(
    evalId: string,
    model: string,
    files: PromptPexContext,
    tests: PromptPexTest[],
    options?: PromptPexOptions
) {
    const { createEvalRuns } = options ?? {}
    const { text } = await toEvalTemplate(files.prompt)
    const parameters = {
        prompt: text,
        intent: files.intent.content || "",
        inputSpec: files.inputSpec.content || "",
        rules: files.rules.content,
    }

    const body = {
        name: model,
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
                            text,
                        },
                    },
                ],
            },
            model,
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
    if (createEvalRuns && apiKey && evalId && tests.length > 0) {
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
        const run = (await res.json()) as { id: string; name: string }
        output.item(
            `[${run.name} dashboard](https://platform.openai.com/evaluations/${evalId}/data?run_id=${run.id})`
        )
        output.detailsFenced(`eval run object`, run, "json")
    }
}

export async function generateEvals(
    models: string[],
    files: PromptPexContext,
    tests: PromptPexTest[],
    options?: PromptPexOptions
) {
    output.heading(3, "Evals")

    const evalId = await evalsCreateRequest(files, options)
    dbg(`eval id: %s`, evalId)
    if (tests?.length) {
        for (const modelId of models) {
            if (!/^openai:/.test(modelId)) {
                dbg(`skipping model %s`, modelId)
                continue
            }
            const model = modelId.replace(/^openai:/, "")
            dbg(`generate eval run for model %s`, model)
            await evalsCreateRun(evalId, model, files, tests, options)
        }
    }
}
