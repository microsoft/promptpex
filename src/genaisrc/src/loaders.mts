import { checkConfirm } from "./confirm.mts"
import {
    CONCURRENCY,
    GITHUB_MODELS_RX,
    PARAMETER_INPUT_TEXT,
    PROMPT_ALL,
    PROMPT_DIR,
    TEST_SAMPLES_COUNT_DEFAULT,
} from "./constants.mts"
import { tidyRulesFile } from "./parsers.mts"
import { checkPromptSafety } from "./safety.mts"
import type {
    PromptPexContext,
    PromptPexLoaderOptions,
    PromptPexOptions,
    PromptPexPromptyFrontmatter,
} from "./types.mts"
import frontMatterSchema from "./frontmatter.json" with { type: "json" }
import packageJson from "../../../package.json" with { type: "json" }
import { githubModelsToPrompty } from "./githubmodels.mts"
const dbg = host.logger("promptpex:loaders")

if (!frontMatterSchema) throw new Error("frontmatter schema not found")

export async function loadPromptContexts(
    files: WorkspaceFile[],
    options?: PromptPexOptions
): Promise<PromptPexContext[]> {
    const q = host.promiseQueue(CONCURRENCY)
    const promptFiles = files.filter((f) =>
        /\.(md|txt|prompty|prompt\.yml|json)$/i.test(f.filename)
    )
    return q.mapAll(
        promptFiles,
        async (f) => await loadPromptContext(f, options)
    )
}

const converters = [
    {
        rx: GITHUB_MODELS_RX,
        convert: githubModelsToPrompty,
    },
]

export async function loadPromptContext(
    promptFile: WorkspaceFile,
    options?: PromptPexLoaderOptions
): Promise<PromptPexContext> {
    if (!promptFile)
        throw new Error(
            "No prompt file found, did you forget to include the prompt file?"
        )
    dbg(`loading files from ${promptFile.filename}`)

    if (/\.json$/i.test(promptFile.filename))
        return await loadPromptContextFromJSON(promptFile, options)

    const { out, disableSafety } = options || {}
    dbg(`out: ${out}`)
    const writeResults = !!out
    let originalPromptFile: WorkspaceFile
    // pre-convert other formats to prompty
    for (const converter of converters) {
        if (converter.rx.test(promptFile.filename)) {
            dbg(`converting file %s`, promptFile.filename)
            const newFile = await converter.convert(promptFile, options)
            if (newFile) {
                originalPromptFile = promptFile
                promptFile = newFile
                dbg(`converted file %s`, promptFile.filename)
                if (writeResults)
                    await workspace.writeText(
                        path.join(out, path.basename(promptFile.filename)),
                        promptFile.content
                    )
                break
            }
        }
    }
    dbg(`prompt file: %O`, promptFile)

    await checkPromptFiles()
    const filename =
        promptFile.filename ||
        (await parsers.hash(promptFile.content, {
            length: 16,
            version: true,
        })) + ".md"
    dbg(`filename: ${filename}`)
    const basename = filename
        ? path.basename(filename).slice(0, -path.extname(filename).length)
        : "prompt"
    const dir = filename
        ? path.join(out || path.dirname(filename), basename)
        : ""
    dbg(`dir: ${dir}`)
    const runId = Math.random().toString(36).slice(2, 10)
    let intent = path.join(dir, "intent.txt")
    let rules = path.join(dir, "rules.txt")
    let inverseRules = path.join(dir, "inverse_rules.txt")
    let inputSpec = path.join(dir, "input_spec.txt")
    let baselineTests = path.join(dir, "baseline_tests.txt")
    let tests = path.join(dir, "tests.json")
    let rateTests = path.join(dir, "test_collection_review.md")
    let testData = path.join(dir, "test_data.json")
    let testResults = path.join(dir, "test_results.json")
    let testEvals = path.join(dir, "test_evals.json")
    let baselineTestEvals = path.join(dir, "baseline_test_evals.json")
    let ruleEvals = path.join(dir, "rule_evals.json")
    let ruleCoverage = path.join(dir, "rule_coverage.json")
    const { messages } = await parsers.prompty(promptFile)
    const frontmatter = await validateFrontmatter(promptFile, {
        patchFrontmatter: true,
    })
    const inputs = frontmatter.inputs as Record<string, JSONSchemaSimpleType>
    if (!inputs) throw new Error(`prompt ${promptFile.filename} has no inputs`)
    const testSamples = await parseTestSamples(
        filename ? path.dirname(filename) : undefined,
        frontmatter,
        options
    )
    const metricGlobs = [path.join(PROMPT_DIR, "*.metric.prompty")]
    if (filename)
        metricGlobs.push(path.join(path.dirname(filename), "*.metric.prompty"))
    let metrics = await workspace.findFiles(metricGlobs)
    if (options?.customMetric)
        metrics.push({
            filename: "custom.metric.prompty",
            content: options.customMetric,
        })
    dbg(
        `metrics (unfiltered): %O`,
        metrics.map(({ filename }) => filename)
    )

    // now apply metric files
    metrics = metrics
        .filter((m) => {
            const fm = MD.frontmatter(m) as PromptPexPromptyFrontmatter
            if (fm?.tags?.includes("experimental")) {
                dbg(`metric %s is experimental, skip`, m.filename)
                return undefined
            }
            return m
        })
        .filter(Boolean)
    dbg(
        `metrics (filtered): %O`,
        metrics.map(({ filename }) => filename)
    )

    const res = {
        runId,
        writeResults,
        dir,
        name: basename,
        frontmatter,
        inputs,
        messages,
        prompt: promptFile,
        originalPrompt: originalPromptFile,
        testOutputs: await workspace.readText(testResults),
        intent: await workspace.readText(intent),
        inputSpec: await workspace.readText(inputSpec),
        rules: tidyRulesFile(await workspace.readText(rules)),
        ruleEvals: await workspace.readText(ruleEvals),
        inverseRules: tidyRulesFile(await workspace.readText(inverseRules)),
        tests: await workspace.readText(tests),
        rateTests: await workspace.readText(rateTests),
        testData: await workspace.readText(testData),
        testEvals: await workspace.readText(testEvals),
        baselineTests: await workspace.readText(baselineTests),
        ruleCoverages: await workspace.readText(ruleCoverage),
        baselineTestEvals: await workspace.readText(baselineTestEvals),
        promptPexTests: [],
        metrics,
        testSamples,
        versions: {
            promptpex: packageJson.version,
            node: process.version,
        },
        options,
    } satisfies PromptPexContext

    if (!disableSafety) await checkPromptSafety(res)
    await checkConfirm("loader")

    res.promptPexTests = parsers.JSON5(res.tests.content) || []

    return res
}

function parseInputs(
    file: WorkspaceFile,
    frontmatter: PromptPexPromptyFrontmatter
) {
    const content = MD.content(file)
    const inputs: Record<string, JSONSchemaSimpleType> = ((
        JSONSchema.fromParameters(frontmatter["inputs"]) as JSONSchemaObject
    )?.properties || {}) as any
    dbg(`inputs: %O`, inputs)
    let patched = false
    content.replace(/{{\s*(\w+)\s*}}/g, (_, key) => {
        if (!inputs[key]) {
            dbg(`found unspecified input %s`, key)
            patched = true
            inputs[key] = {
                type: "string",
            } satisfies JSONSchemaString
        }
        return ""
    })
    if (!Object.keys(inputs).length) {
        dbg(`no inputs found, appending default`)
        patched = true
        inputs[PARAMETER_INPUT_TEXT] = {
            type: "string",
            description: "Detailed input provided to the software.",
        } satisfies JSONSchemaString
        file.content += `\n{{${PARAMETER_INPUT_TEXT}}}`
    }

    return { patched, inputs }
}

async function checkPromptFiles() {
    dbg(`checking prompt files`)
    for (const filename of PROMPT_ALL) {
        dbg(`validating ${filename}`)
        const file = await workspace.readText(filename)
        if (!file?.content) throw new Error(`prompt file ${filename} not found`)
        await validateFrontmatter(file)
        const content = MD.content(file)
        if (!content) throw new Error(`prompt file ${filename} is empty`)
    }
}

async function parseTestSamples(
    dir: string,
    fm: PromptPexPromptyFrontmatter,
    options?: PromptPexLoaderOptions
) {
    const { testSamples } = fm
    if (!testSamples) return []

    dbg(`parsing test samples`)
    let res: Record<string, string>[] = []
    for (const sample of testSamples) {
        if (typeof sample === "string") {
            dbg(`loading test sample %s`, sample)
            const sampleFile = path.resolve(
                dir ? path.join(dir, sample) : sample
            )
            dbg(`resolved sample file %s`, sampleFile)
            let data = await workspace.readData(sampleFile)
            dbg(`%O`, data)
            if (!data) throw new Error(`test sample ${sample} not found`)
            if (
                !Array.isArray(data) &&
                typeof data === "object" &&
                Object.keys(data).length === 1
            ) {
                dbg(`using first field`)
                data = data[Object.keys(data)[0]]
            }
            if (!Array.isArray(data))
                throw new Error(`test sample is not an array`)
            if (data.some((d) => typeof d !== "object"))
                throw new Error(`test sample contains invalid data`)
            res.push(...data)
        } else if (typeof sample === "object") {
            res.push(sample as any)
        } else {
            throw new Error(`test sample ${sample} is not a string or object`)
        }
    }

    dbg(`found %d test samples`, res.length)
    const count = options?.testSamplesCount ?? TEST_SAMPLES_COUNT_DEFAULT
    // shuffle first
    if (options?.testSamplesShuffle) res.sort(() => Math.random() - 0.5)
    // then slice
    res = res.slice(0, count)
    return res
}

export async function validateFrontmatter(
    file: WorkspaceFile,
    options?: { patchFrontmatter?: boolean }
): Promise<PromptPexPromptyFrontmatter> {
    const { patchFrontmatter } = options || {}
    let frontmatter = MD.frontmatter(file)
    if (!frontmatter) frontmatter = {}

    const { patched, inputs } = parseInputs(file, frontmatter)
    if (patched && !patchFrontmatter)
        throw new Error(`prompt ${file.filename} has unspecified inputs`)
    if (patched && patchFrontmatter) {
        frontmatter.inputs = inputs
        file.content = MD.updateFrontmatter(file.content, frontmatter)
        frontmatter = MD.frontmatter(file)
        dbg(`updated frontmatter: %O`, frontmatter)
    }

    const res = parsers.validateJSON(
        frontMatterSchema as JSONSchema,
        frontmatter
    )
    if (res.schemaError) {
        dbg(`schema error for ${file.filename}`)
        dbg(`error: %O`, res.schemaError)
        dbg(`frontmatter: %O`, frontmatter)
        throw new Error(`schema error for ${file.filename}: ${res.schemaError}`)
    }

    return frontmatter
}

async function loadPromptContextFromJSON(
    file: WorkspaceFile,
    options: PromptPexOptions
): Promise<PromptPexContext> {
    const { out } = options
    dbg(`loading json...`)
    const ctx = JSON.parse(file.content) as PromptPexContext

    const dir = out || path.dirname(file.filename)
    dbg(`using dir: %s`, dir)

    const ctxFiles = [
        ctx.intent,
        ctx.rules,
        ctx.inverseRules,
        ctx.inputSpec,
        ctx.baselineTests,
        ctx.tests,
        ctx.rateTests,
        ctx.testData,
        ctx.testOutputs,
        ctx.testEvals,
        ctx.baselineTestEvals,
        ctx.ruleEvals,
        ctx.ruleCoverages,
    ]
    for (const file of ctxFiles) {
        file.filename = path.join(dir, path.basename(file.filename))
    }

    await workspace.writeFiles(ctxFiles.filter((f) => f.content))
    ctx.options = { ...options, ...ctx.options }
    return ctx
}

export async function saveContextState(
    ctx: PromptPexContext,
    filename: string
): Promise<void> {
    const json = JSON.stringify(ctx, null, 2)
    dbg(`saving context to ${filename}`)
    await workspace.writeText(filename, json)
}
