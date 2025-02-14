import {
    generateInputSpec,
    generateIntent,
    generateRules,
    loadPromptFiles,
    PromptPexContext,
    generateBaselineTests,
    generateInverseRules,
    PromptPexOptions,
    evaluateRulesGrounded,
    evaluateRulesCoverage,
    generateTests,
} from "./promptpex.mts";

script({
    title: "PromptPex Dev",
    model: "large",
    unlisted: true,
    files: [
        "samples/speech-tag/speech-tag.prompty",
        "samples/text-to-p/text-to-p.prompty",
        "samples/openai-examples/elements.prompty",
        "samples/big-prompt-lib/art-prompt.prompty",
        "samples/prompt-guide/extract-names.prompty",
        "samples/text-classification/classify-input-text.prompty",
        "samples/big-prompt-lib/sentence-rewrite.prompty",
        "samples/azure-ai-studio/shakespearean-writing-assistant.prompty",
    ],
});
const { output } = env;
const out = "evals/dev";
const options: PromptPexOptions = {
    outputPrompts: true,
};

const repeatIntent = 1;
const repeatInputSpec = 1;
const repeatRules = 1;
const repeatInverseRules = 1;
const repeatTests = 1;
const repeatBaselineTests = 1;
const repeastRulesGroundedness = 5;

output.heading(1, "PromptPex Dev Mode");
output.itemValue(`model`, env.meta.model);
const prompts = await Promise.all(
    env.files.map((file) => loadPromptFiles(file, { disableSafety: true, out }))
);
prompts.forEach((files) => output.itemValue(files.name, files.prompt.filename));

async function apply(
    title: string,
    repeat: number,
    selector: (files: PromptPexContext) => WorkspaceFile,
    fn: (files: PromptPexContext) => Awaitable<string>
) {
    output.heading(2, title);
    for (const files of prompts) {
        output.heading(3, files.prompt.filename.replace(/^samples\//, ""));
        const file = selector?.(files);
        if (repeat === 0 && file?.content) continue;
        for (let i = 0; i < repeat; ++i) {
            const res = await fn(files);
            if (file) {
                file.content = res;
                output.fence(file.content, "text");
            }
        }
        if (file) await workspace.writeText(file.filename, file.content);
    }
}

await apply(
    "Intents",
    repeatIntent,
    (_) => _.intent,
    (files) => generateIntent(files, options)
);
await apply(
    "Input Specs",
    repeatInputSpec,
    (_) => _.inputSpec,
    (files) => generateInputSpec(files, options)
);
await apply("Rules", repeatRules, undefined, async (files) => {
    files.rules.content = await generateRules(files, options);
    output.fence(files.rules.content, "text");

    output.heading(3, "Evaluating Rules Groundedness");
    const groundedness = await evaluateRulesGrounded(files, options);
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
    ]);
    output.detailsFenced(`data`, groundedness, "json");
    return "";
});
await apply(
    "Inverse Rules",
    repeatInverseRules,
    (_) => _.inverseRules,
    (files) => generateInverseRules(files, options)
);
await apply(
    "Tests",
    repeatTests,
    (_) => _.tests,
    (files) => generateTests(files, options)
);
await apply(
    "Baseline Tests",
    repeatBaselineTests,
    (_) => _.baselineTests,
    (files) => generateBaselineTests(files, options)
);
await apply(
    "Evaluating Rules Coverage",
    repeastRulesGroundedness,
    undefined,
    async (files) => {
        output.heading(3, "Evaluating Rules Coverage");
        const coverage = await evaluateRulesCoverage(files, options);
        output.table([
            ...coverage.map(({ rule, coverage, coverageText }) => ({
                rule,
                coverage,
                coverageText,
            })),
            {
                rule: "ok",
                coverage: coverage.reduce(
                    (acc, { coverage }) => acc + (coverage === "ok" ? 1 : 0),
                    0
                ),
            },
        ]);
        output.detailsFenced(`data`, coverage, "json");
        return "";
    }
);
