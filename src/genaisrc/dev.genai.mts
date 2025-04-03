import { evaluateRulesSpecAgreement } from "./src/rulesspecagreement.mts"
import { loadPromptFiles } from "./src/loaders.mts"
import { evaluateRulesGrounded } from "./src/rulesgroundeness.mts"
import type { PromptPexContext, PromptPexOptions } from "./src/types.mts"
import { generateBaselineTests } from "./src/baselinetestgen.mts"
import { generateTests } from "./src/testgen.mts"
import { generateInputSpec } from "./src/inputspecgen.mts"
import { generateIntent } from "./src/intentgen.mts"
import { generateOutputRules } from "./src/rulesgen.mts"
import { loadFabricPrompts } from "./src/fabricloader.mts"
import { generateInverseOutputRules } from "./src/inverserulesgen.mts"
import { evaluateTestsQuality } from "./src/testquality.mts"

script({
    title: "PromptPex Dev",
    unlisted: true,
    files: [
        "samples/demo/demo.prompty",
        /*        "samples/speech-tag/speech-tag.prompty",
        "samples/text-to-p/text-to-p.prompty",
        "samples/openai-examples/elements.prompty",
        "samples/big-prompt-lib/art-prompt.prompty",
        "samples/prompt-guide/extract-names.prompty",
        "samples/text-classification/classify-input-text.prompty",
        "samples/big-prompt-lib/sentence-rewrite.prompty",
        "samples/azure-ai-studio/shakespearean-writing-assistant.prompty",*/
    ],
    parameters: {
        fabric: {
            type: "string",
            description: "Fabric version to use",
            required: false,
        },
        samplePrompts: {
            type: "integer",
            description: "Number of prompts to sample",
            required: false,
        },
    },
})
const { output, vars } = env
const { fabric, samplePrompts } = vars as {
    fabric: string
    samplePrompts: number
}
const out = "evals/dev"
const commOptions: PromptPexOptions = {
    outputPrompts: true,
    cache: true,
    evalCache: true,
}

const repeatIntent = 1
const repeatInputSpec = 1
const repeatRules = 1
const repeatInverseRules = 1
const repeatTests = 1
const repeatBaselineTests = 0
const repeastRulesGroundedness = 0
const repeatTestsQualityEval = 1
const configs: (PromptPexOptions & { name: string })[] = [
    {
        name: "github",
        modelAliases: {
            large: "not-supported",
            small: "not-supported",
            rules: "github:gpt-4o",
            eval: "github:gpt-4o",
            baseline: "github:gpt-4o",
        },
    },
    /*    {
        name: "gpt-4o",
        modelAliases: {
            large: "not-supported",
            small: "not-supported",
            rules: "azure:gpt-4o_2024-11-20",
            eval: "azure:gpt-2024-11-20",
            baseline: "azure:gpt-4o_2024-11-20",
        },
    },*/
    /*    {
        name: "llama3.3:70b",
        modelAliases: {
            large: "not-supported",
            rules: "ollama:llama3.3",
            eval: "ollama:llama3.3",
        },
    },*/
    /*
    {
        name: "deepskeep-r1:8b",
        modelAliases: {
            large: "not-supported",
            rules: "ollama:deepseek-r1:8b",
            eval: "ollama:deepseek-r1:8b",
        },
    },
    */
    /*
    {
        name: "deepskeep-r1:32b",
        modelAliases: {
            large: "not-supported",
            rules: "ollama:deepseek-r1:32b",
            eval: "ollama:deepseek-r1:32b",
        },
    },
    */
    /*
    {
        name: "deepskeep-r1:70b",
        modelAliases: {
            large: "not-supported",
            rules: "ollama:deepseek-r1:70b",
            eval: "ollama:deepseek-r1:70b",
        },
    },
    */
].filter((c) => !!c)

output.heading(1, "PromptPex Dev Mode")
output.detailsFenced(`configurations`, configs, "yaml")
let prompts = await Promise.all([
    ...(!fabric
        ? env.files.map((file) =>
              loadPromptFiles(file, { disableSafety: true, out })
          )
        : []),
    ...(fabric
        ? await loadFabricPrompts(fabric, { disableSafety: true, out })
        : []),
])
if (samplePrompts)
    prompts = parsers.tidyData(prompts, {
        sliceSample: samplePrompts,
    }) as PromptPexContext[]
output.itemValue("prompts", prompts.length)
prompts.forEach((files) => output.itemValue(files.name, files.prompt.filename))

async function apply(
    title: string,
    repeat: number,
    selector: (files: PromptPexContext) => WorkspaceFile,
    fn: (
        files: PromptPexContext,
        options: PromptPexOptions
    ) => Awaitable<string>
) {
    output.heading(2, title)
    const table = []
    for (const files of prompts) {
        const row = { prompt: files.name }
        table.push(row)

        output.heading(3, files.prompt.filename.replace(/^samples\//, ""))
        const file = selector?.(files)
        if (repeat === 0 && file?.content) continue

        for (const config of configs) {
            const { name, ...restConfig } = config
            output.heading(4, name)
            for (let i = 0; i < repeat; ++i) {
                const res = await fn(files, { ...commOptions, ...restConfig })
                if (file) {
                    file.content = res
                    output.fence(file.content, "text")
                }
                row[`${config.name}/${i}`] = res
            }
        }
        if (file) await workspace.writeText(file.filename, file.content)
    }
    output.table(table)
    output.detailsFenced(`data`, table, "csv")
}

await apply(
    "Intents",
    repeatIntent,
    (_) => _.intent,
    (files, options) => generateIntent(files, options)
)
await apply(
    "Input Specs",
    repeatInputSpec,
    (ctx) => ctx.inputSpec,
    (files, options) => generateInputSpec(files, options)
)
await apply("Rules", repeatRules, undefined, async (files, options) => {
    files.rules.content = await generateOutputRules(files, options)
    output.fence(files.rules.content, "text")

    output.heading(3, "Evaluating Rules Groundedness")
    const groundedness = await evaluateRulesGrounded(files, options)
    output.table([
        ...groundedness.map(({ rule, grounded }) => ({
            rule,
            grounded,
        })),
        {
            rule: "ok",
            grounded: groundedness.reduce(
                (acc, { grounded }) => acc + (grounded === "ok" ? 1 : 0),
                0
            ),
        },
    ])
    output.detailsFenced(`data`, groundedness, "csv")
    return ""
})
await apply(
    "Inverse Rules",
    repeatInverseRules,
    (_) => _.inverseRules,
    (files, options) => generateInverseOutputRules(files, options)
)
await apply(
    "Tests",
    repeatTests,
    (_) => _.tests,
    (files, options) => generateTests(files, options)
)
await apply(
    "Baseline Tests",
    repeatBaselineTests,
    (_) => _.baselineTests,
    (files, options) => generateBaselineTests(files, options)
)
await apply(
    "Evaluating Rules Coverage",
    repeastRulesGroundedness,
    undefined,
    async (files, options) => {
        output.heading(3, "Evaluating Rules Spec Agreement")
        const res = await evaluateRulesSpecAgreement(files, options)
        output.table([
            ...res.map(({ rule, coverage, coverageText }) => ({
                rule,
                agreement: coverage,
            })),
            {
                rule: "ok",
                agreement: res.reduce(
                    (acc, { coverage }) => acc + (coverage === "ok" ? 1 : 0),
                    0
                ),
            },
        ])
        output.detailsFenced(`data`, res, "csv")
        return ""
    }
)
await apply(
    "Evaluate Tests Quality",
    repeatTestsQualityEval,
    (_) => _.testEvals,
    async (files, options) => await evaluateTestsQuality(files, options)
)
