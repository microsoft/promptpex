import type {
    PromptPexContext,
    PromptPexLoaderOptions,
    PromptPexOptions,
    PromptPexPromptyFrontmatter,
    PromptPexTest,
} from "./types.mts"
import { fillTemplateVariables, resolvePromptArgs } from "./resolvers.mts"
import { GITHUB_MODELS_RX } from "./constants.mts"
import { metricName } from "./parsers.mts"

const { output } = env
const dbg = host.logger("promptpex:github:models")
/*


name: Custom LLM Evaluator Example
description: Example showing how to use a custom LLM-based evaluator as a judge
model: openai/gpt-4o
modelParameters:
  temperature: 0.3
  maxTokens: 200

testData:
  - input: "What is machine learning?"
    expected: "Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed."
  - input: "Explain photosynthesis in simple terms"
    expected: "Photosynthesis is the process by which plants use sunlight, water, and carbon dioxide to create their own food and produce oxygen."
  - input: "What are the benefits of exercise?"
    expected: "Exercise improves physical health, mental well-being, helps maintain healthy weight, strengthens muscles and bones, and reduces the risk of chronic diseases."

messages:
  - role: system
    content: You are a helpful and knowledgeable assistant that provides accurate, clear, and concise explanations on various topics.
  - role: user
    content: "{{input}}"

evaluators:
  # String-based evaluator for basic checks
  - name: response-length-check
    string:
      contains: "is"
  
  # Custom LLM evaluator as a judge
  - name: answer-quality-judge
    llm:
      modelId: openai/gpt-4o
      systemPrompt: |
        You are an expert judge evaluating the quality of answers to questions. 
        You must assess how well the actual answer compares to the expected answer in terms of:
        1. Accuracy of information
        2. Completeness of the response
        3. Clarity and understandability
        
        Rate the answer on a scale from 1-5 where:
        1 = Poor (completely wrong or irrelevant)
        2 = Below Average (partially correct but missing key information)
        3 = Average (mostly correct with minor gaps)
        4 = Good (accurate and complete with clear explanation)
        5 = Excellent (exceptionally accurate, complete, and well-explained)
        
        You must respond with ONLY the number rating (1, 2, 3, 4, or 5).
      prompt: |
        Question: {{input}}
        
        Expected Answer: {{expected}}
        
        Actual Answer: {{completion}}
        
        Please rate the actual answer compared to the expected answer using the 1-5 scale defined in your instructions. 
        Consider accuracy, completeness, and clarity in your evaluation.
        
        Rating:
      choices:
        - choice: "1"
          score: 0.0
        - choice: "2" 
          score: 0.25
        - choice: "3"
          score: 0.5
        - choice: "4"
          score: 0.75
        - choice: "5"
          score: 1.0
  
    */

export type GitHubModelsTestDataItem = Record<string, string> & {
    expected: string
}

export type GitHubModelsMessageRole = "system" | "user" | "assistant"

export interface GitHubModelsMessage {
    role: GitHubModelsMessageRole
    content: string
}

export interface GitHubModelsStringEvaluator {
    contains?: string
}

export interface GitHubModelsLlmEvaluatorChoice {
    choice: string
    score: number
}

export interface GitHubModelsLlmEvaluator {
    modelId: string
    systemPrompt: string
    prompt: string
    choices: GitHubModelsLlmEvaluatorChoice[]
}

export interface GitHubModelsEvaluator {
    name: string
    string?: GitHubModelsStringEvaluator
    llm?: GitHubModelsLlmEvaluator
}

export interface GitHubModelsPrompt {
    name: string
    description?: string
    model: string
    modelParameters?: {
        temperature?: number
        maxTokens?: number
    }
    messages: GitHubModelsMessage[]
    testData?: GitHubModelsTestDataItem[]
    evaluators?: GitHubModelsEvaluator[]
}

async function resolveInternalVariables(
    file: WorkspaceFile,
    files: PromptPexContext,
    idResolver?: (id: string) => string
) {
    const { filename, content } = file
    const { intent, inputSpec, rules, prompt } = files
    const variables: Record<string, string> = {
        intent: intent.content ?? "",
        inputSpec: inputSpec.content ?? "",
        rules: rules.content ?? "",
        output: "completion",
    }
    const promptPatched = {
        filename: prompt.filename,
        content: fillTemplateVariables(prompt.content, {
            variables,
            idResolver,
        }),
    }
    const { messages } = await parsers.prompty(promptPatched)
    variables.prompt = messages.map(messageContentToString).join("\n")

    return {
        filename,
        content: fillTemplateVariables(content, {
            variables,
            idResolver,
        }),
    }
}

export async function githubModelsToPrompty(
    file: WorkspaceFile,
    options?: PromptPexLoaderOptions
): Promise<WorkspaceFile> {
    dbg(`loading prompt: %s`, file.filename)
    dbg(`prompt.yml:\s%s`, file.content)
    const prompt = YAML.parse(file.content) as GitHubModelsPrompt
    const {
        name,
        description,
        model,
        modelParameters,
        testData,
        messages,
        ...imported
    } = prompt
    const fm: any = {
        name,
        description,
        model: {
            api: "chat",
            configuration: {
                name: "github:" + model,
                azure_deployment: undefined,
                azure_endpoint: undefined,
            },
            parameters: {
                temperature: modelParameters?.temperature,
                max_tokens: modelParameters?.maxTokens,
            },
        },
        testSamples: testData?.map((item) => item),
        imported,
    } satisfies PromptPexPromptyFrontmatter
    const content = `---
${YAML.stringify(fm)}
---
${prompt.messages
    .map(
        (msg) => `${msg.role}:
${messageContentToString(msg)}
`
    )
    .join("\n")}
`
    dbg(`prompt:\n%s`, content)
    return {
        filename: file.filename.replace(GITHUB_MODELS_RX, ".prompty"),
        content,
    }
}

async function toModelsPrompt(
    modelUnderTest: string,
    messages: ChatMessage[],
    files: PromptPexContext
): Promise<GitHubModelsPrompt> {
    const { frontmatter, promptPexTests } = files
    const { name, description, model, imported } = frontmatter
    const { parameters } = model || {}
    const { temperature, max_tokens: maxTokens } = parameters || {}

    const { model: resolvedModel } =
        await host.resolveLanguageModel(modelUnderTest)
    dbg(`model: %s`, resolvedModel)

    const testData = promptPexTests
        .map((test) => resolvePromptArgs(files, test))
        .map((test) => ({
            ...test.args,
            expected: test.groundtruth,
        }))

    const res: GitHubModelsPrompt = {
        name,
        description,
        model: resolvedModel,
        modelParameters: {
            temperature,
            maxTokens,
        },
        messages: messages.map(toMessage),
        testData,
        ...(imported || {}),
    } satisfies GitHubModelsPrompt
    res.evaluators = res.evaluators || []
    for (const metric of files.metrics) {
        const evaluator = await metricToEvaluator(metric, files)
        res.evaluators.push(evaluator)
    }
    dbg(`prompt: %s`, YAML.stringify(res))
    return res

    function toMessage(msg: ChatMessage): GitHubModelsMessage {
        const content = messageContentToString(msg)
        return {
            role: msg.role as GitHubModelsMessageRole,
            content,
        }
    }
}

async function metricToEvaluator(
    metric: WorkspaceFile,
    files: PromptPexContext
) {
    const resolvedMetric = await resolveInternalVariables(metric, files)
    const resolvedPrompt = await parsers.prompty(resolvedMetric)
    const evaluator: GitHubModelsEvaluator = {
        name: metricName(resolvedMetric),
        llm: {
            modelId: resolvedPrompt?.meta?.model ?? "openai/gpt-4o",
            systemPrompt: resolvedPrompt.messages
                .filter((msg) => msg.role === `system`)
                .map(messageContentToString)
                .join("\n"),
            prompt: resolvedPrompt.messages
                .filter((msg) => msg.role !== `system`)
                .map(messageContentToString)
                .join("\n"),
            choices: [
                { choice: "OK", score: 1 },
                { choice: "ERR", score: 0 },
            ],
        },
    }
    return evaluator
}

function messageContentToString(msg: ChatMessage): string {
    let content: string = ""
    if (Array.isArray(msg.content)) {
        content = msg.content.map((part) => partToString(part)).join("\n")
    } else content = partToString(msg.content)
    return content
}

function partToString(part: string | ChatContentPart) {
    if (typeof part === "string") return part
    if (part.type === "text") return part.text
    if (part.type === "file") return part.file.filename
    return part.type
}

export async function githubModelsEvalsGenerate(
    files: PromptPexContext,
    tests: PromptPexTest[],
    options?: PromptPexOptions
) {
    output.heading(3, "GitHub Models Evals")
    const { messages } = files
    const { modelsUnderTest } = options || {}
    if (!modelsUnderTest?.length)
        throw new Error("No models under test specified in options")

    if (tests?.length) {
        for (const modelId of modelsUnderTest) {
            if (!/^github:/.test(modelId)) {
                dbg(`skipping model %s`, modelId)
                continue
            }
            const res = await toModelsPrompt(modelId, messages, files)
            const evalPromptFile = {
                filename: path.join(
                    files.dir,
                    `${res.model.replace(/\//g, "_")}.prompt.yml`
                ),
                content: YAML.stringify(res),
            }
            output.detailsFenced(
                evalPromptFile.filename,
                evalPromptFile.content,
                "yaml"
            )
            await workspace.writeFiles(evalPromptFile)
        }
    }
}
