import type { OpenAI } from "openai"
import type {
    PromptPexContext,
    PromptPexOptions,
    PromptPexPromptyFrontmatter,
    PromptPexTest,
} from "./types.mts"
import { metricName } from "./parsers.mts"
import { OK_CHOICE, OK_ERR_CHOICES } from "./constants.mts"
import { resolvePromptArgs } from "./resolvers.mts"
import { fillTemplateVariables } from "./template.mts"
const dbg = host.logger("promptpex:openai:evals")
const { output } = env

// OpenAI: https://platform.openai.com/docs/api-reference/evals
// Azure OpenAI: https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/evaluations?tabs=question-eval-input
// https://learn.microsoft.com/en-us/azure/ai-services/openai/authoring-reference-preview

async function toEvalTemplate(
    file: WorkspaceFile,
    variables: Record<string, string>
) {
    const patched = {
        filename: file.filename,
        content: fillTemplateVariables(file.content, {
            variables,
            idResolver: (id) => {
                if (id === "output") return "{{sample.output_text}}"
                return `{{item.${id}}}`
            },
        }),
    }
    dbg(`patched: %s`, patched.content)
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
    model: string,
    variables: Record<string, string>
): Promise<OpenAI.Evals.EvalCreateParams.LabelModel | any> {
    const name = metricName(metric)
    const fm = MD.frontmatter(metric.content) as PromptPexPromptyFrontmatter
    const scorer = fm.tags?.includes("scorer")
    const { input } = await toEvalTemplate(metric, variables)
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
        input: {
            type: "string",
        },
    },
    required: ["prompt", "input"],
}

interface OpenAIConnection {
    url: string
    headers: Record<string, string>
    dashboardUrl?: string
    version?: string
}

export async function openaiEvalsResolveConnection(): Promise<OpenAIConnection> {
    let url: string | undefined
    let headers: Record<string, string> | undefined
    let dashboardUrl: string | undefined
    let version: string | undefined

    // OpenAI
    const oai = await host.resolveLanguageModelProvider("openai", {
        token: true,
    })
    dbg(`oai: %O`, oai)
    if (oai?.token) {
        dbg(`connection: OpenAI`)
        url = oai.base + `v1/evals`
        headers = {
            Authorization: `Bearer ${oai.token}`,
            "Content-Type": "application/json",
        }
        dashboardUrl = "https://platform.openai.com/evaluations/"
    }

    // Azure OpenAI
    if (!url) {
        const aoia = await host.resolveLanguageModelProvider("azure", {
            token: true,
        })
        dbg(`aoia: %O`, aoia)
        if (aoia?.token) {
            dbg(`connection: Azure OpenAI`)
            url = aoia.base.replace(/\/deployments\/?$/, `/evals`)
            headers = {
                "Content-Type": "application/json",
                Authorization: aoia.token,
            }
            version = aoia.version || "2025-04-01-preview"
        }
    }

    dbg(`connection: %O`, { url, headers, dashboardUrl, version })
    return url ? { url, headers, dashboardUrl, version } : undefined
}

function urlWithVersion(base: string, route: string, version?: string) {
    return `${base}${route}${version ? `?api-version=${version}` : ""}`
}

export async function openaiEvalsListEvals() {
    const { url, headers, version } = await openaiEvalsResolveConnection()
    if (!url) return {}
    const listUrl = urlWithVersion(url, "", version)
    const res = await fetch(listUrl, {
        method: "GET",
        headers: headers,
    })
    const data = await res.json()
    dbg(`evals.list: %O`, data)
    return {
        ok: res.ok,
        status: res.status,
        statusText: res.statusText,
        data,
    }
}

async function evalsCreateRequest(
    connection: OpenAIConnection,
    files: PromptPexContext,
    options?: PromptPexOptions
) {
    const name = `${files.name} (promptpex)`
    const { metrics, inputs, intent, inputSpec, rules } = files
    const model = "gpt-4o"
    const variables = {
        intent: intent.content ?? "",
        inputSpec: inputSpec.content ?? "",
        rules: rules.content ?? "",
    }
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
                metricToTestingCriteria(metric, model, variables)
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

    if (connection) {
        const { url, version, headers, dashboardUrl } = connection
        const createUrl = urlWithVersion(url, "", version)
        dbg(`create:\nPOST %s\n%O\n%O`, createUrl, headers, body)
        const res = await fetch(createUrl, {
            method: "POST",
            headers: headers,
            body: JSON.stringify(body),
        })
        dbg(`res: %d %s`, res.status, res.statusText)
        if (!res.ok) {
            output.fence(await res.text())
            throw new Error(`failed to upload evals: ${res.statusText}`)
        }
        const evalDef = (await res.json()) as { id: string }
        dbg(`eval: %O`, evalDef)
        if (dashboardUrl)
            output.itemLink("eval dashboard", `${dashboardUrl}${evalDef.id}`)
        else output.itemValue(`eval id`, evalDef.id)
        output.detailsFenced(`eval object`, evalDef, "json")
        return evalDef.id
    }

    return undefined
}

async function evalsCreateRun(
    connection: OpenAIConnection | undefined,
    evalId: string,
    model: string,
    files: PromptPexContext,
    tests: PromptPexTest[],
    options?: PromptPexOptions
) {
    const variables = {
        intent: files.intent.content ?? "",
        inputSpec: files.inputSpec.content ?? "",
        rules: files.rules.content ?? "",
    }
    const { text } = await toEvalTemplate(files.prompt, variables)
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
                content: tests.map((test) => {
                    const { args } = resolvePromptArgs(files, test)
                    return {
                        item: {
                            ...variables,
                            input: test.testinput,
                            ...args,
                        },
                    }
                }),
            },
        },
    }

    dbg(`%O`, body)
    await workspace.writeText(
        path.join(files.dir, "evals.run.json"),
        JSON.stringify(body, null, 2)
    )

    if (connection && evalId && tests.length > 0) {
        const { url, headers, dashboardUrl, version } = connection
        dbg(`uploading eval run`)
        const createRunUrl = urlWithVersion(url, `/${evalId}/runs`, version)
        dbg(`POST %s\n%O\n%O`, createRunUrl, headers, body)
        const res = await fetch(createRunUrl, {
            method: "POST",
            headers,
            body: JSON.stringify(body),
        })
        dbg(`res: %d %s`, res.status, res.statusText)
        if (!res.ok) {
            output.fence(await res.text())
            throw new Error(`failed to upload eval run: ${res.statusText}`)
        }
        const run = (await res.json()) as { id: string; name: string }
        if (dashboardUrl)
            output.itemLink(
                run.name,
                `${dashboardUrl}${evalId}/data?run_id=${run.id}`
            )
        else output.itemValue(`eval run id`, run.id)
        output.detailsFenced(`eval run object`, run, "json")
    }
}

export async function openaiEvalsGenerate(
    files: PromptPexContext,
    tests: PromptPexTest[],
    options?: PromptPexOptions
) {
    output.heading(3, "OpenAI Evals")
    const { createEvalRuns, modelsUnderTest } = options || {}

    const connection = createEvalRuns
        ? await openaiEvalsResolveConnection()
        : undefined
    const evalId = await evalsCreateRequest(connection, files, options)
    output.itemValue(`eval id`, evalId)
    dbg(`eval id: %s`, evalId)
    if (tests?.length) {
        for (const modelId of modelsUnderTest) {
            if (!/^(openai|azure):/.test(modelId)) {
                dbg(`skipping model %s`, modelId)
                continue
            }
            const model = modelId.replace(/^(openai|azure):/, "")
            dbg(`generate eval run for model %s`, model)
            await evalsCreateRun(
                connection,
                evalId,
                model,
                files,
                tests,
                options
            )
        }
    }
}
