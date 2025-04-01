import { CONCURRENCY, PROMPT_ALL } from "./constants.mts"
import { parseInputs, tidyRulesFile } from "./parsers.mts"
import { checkPromptSafety } from "./safety.mts"
import type { PromptPexContext, PromptPexLoaderOptions } from "./types.mts"
const dbg = host.logger("promptpex:loader")

export async function loadPromptContext(
    files: WorkspaceFile[],
    options?: PromptPexLoaderOptions
): Promise<PromptPexContext[]> {
    const q = host.promiseQueue(CONCURRENCY)
    return q.mapAll(
        files.filter((f) => /\.(md|txt|prompty)$/i.test(f.filename)),
        async (f) => await loadPromptFiles(f, options)
    )
}

export async function loadPromptFiles(
    promptFile: WorkspaceFile,
    options?: PromptPexLoaderOptions
): Promise<PromptPexContext> {
    if (!promptFile)
        throw new Error(
            "No prompt file found, did you forget to the prompt file?"
        )
    await checkPromptFiles()
    const { out, disableSafety } = options || {}
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
    const intent = path.join(dir, "intent.txt")
    const rules = path.join(dir, "rules.txt")
    const inverseRules = path.join(dir, "inverse_rules.txt")
    const inputSpec = path.join(dir, "input_spec.txt")
    const baselineTests = path.join(dir, "baseline_tests.txt")
    const tests = path.join(dir, "tests.json")
    const testResults = path.join(dir, "test_results.json")
    const testEvals = path.join(dir, "test_evals.json")
    const baselineTestEvals = path.join(dir, "baseline_test_evals.json")
    const ruleEvals = path.join(dir, "rule_evals.json")
    const ruleCoverage = path.join(dir, "rule_coverage.json")
    const frontmatter = MD.frontmatter(promptFile.content) || {}
    const meta: PromptPexContext["meta"] = frontmatter.promptPex || {}
    const inputs = parseInputs(promptFile)

    const res = {
        dir,
        name: basename,
        frontmatter,
        meta,
        inputs,
        prompt: promptFile,
        testOutputs: await workspace.readText(testResults),
        intent: await workspace.readText(intent),
        inputSpec: await workspace.readText(inputSpec),
        rules: tidyRulesFile(await workspace.readText(rules)),
        ruleEvals: await workspace.readText(ruleEvals),
        inverseRules: tidyRulesFile(await workspace.readText(inverseRules)),
        tests: await workspace.readText(tests),
        testEvals: await workspace.readText(testEvals),
        baselineTests: await workspace.readText(baselineTests),
        ruleCoverages: await workspace.readText(ruleCoverage),
        baselineTestEvals: await workspace.readText(baselineTestEvals),
    } satisfies PromptPexContext

    if (meta.intent) res.intent.content = meta.intent
    if (meta.inputSpec) res.inputSpec.content = meta.inputSpec
    if (meta.outputRules) res.rules.content = meta.outputRules
    if (meta.inverseOutputRules)
        res.inverseRules.content = meta.inverseOutputRules
    if (!disableSafety) await checkPromptSafety(res)
    return res
}

async function checkPromptFiles() {
    for (const filename of PROMPT_ALL) {
        dbg(`validating ${filename}`)
        const file = await workspace.readText(filename)
        if (!file?.content) throw new Error(`prompt file ${filename} not found`)
        const frontmatter = MD.frontmatter(file)
        if (!frontmatter)
            throw new Error(`prompt file ${filename} has no frontmatter`)
        const content = MD.content(file)
        if (!content) throw new Error(`prompt file ${filename} is empty`)
    }
}
