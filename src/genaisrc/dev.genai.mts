import {
    generateInputSpec,
    generateIntent,
    generateRules,
    loadPromptFiles,
    PromptPexContext,
} from "./promptpex.mts";

script({
    title: "PromptPex Dev",
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
const options = {};

const repeatIntent = 1;
const repeatInputSpec = 1;
const repeatRules = 5;

output.heading(1, "PromptPex Dev Mode");
const prompts = await Promise.all(
    env.files.map((file) => loadPromptFiles(file, ""))
);

async function apply(
    title: string,
    repeat: number,
    fn: (files: PromptPexContext) => Awaitable<void>
) {
    output.heading(2, title);
    for (const files of prompts) {
        output.heading(3, files.prompt.filename.replace(/^samples\//, ""));
        for (let i = 0; i < Math.max(1, repeat); ++i) {
            await fn(files);
        }
    }
}

await apply("Intents", repeatIntent, async (files) => {
    files.intent.content = await generateIntent(files, options);
    output.fence(files.intent.content, "text");
});
await apply("Input Specs", repeatInputSpec, async (files) => {
    files.inputSpec.content = await generateInputSpec(files, options);
    output.fence(files.inputSpec.content, "text");
});
await apply("Rules", repeatRules, async (files) => {
    files.rules.content = await generateRules(files, options);
    output.fence(files.rules.content, "text");
});
