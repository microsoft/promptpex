import { ppModelOptions, ppFiles, ppCleanRules } from "./promptpex.mts";

script({
  title: "PromptPex Rules Generator",
  description:
    "Generate a rules file for a prompt template. Runs this script against a prompt authored in markdown or prompty format.",
  files: ["samples/speech-tag.prompty"],
});

const files = await ppFiles();

const res = await runPrompt(
  (ctx) => {
    ctx.importTemplate("src/prompts/rules_global.prompty", {
      input_data: files.prompt.content,
    });
  },
  {
    ...ppModelOptions(),
    label: "generate rules",
  }
);
if (res.error) throw res.error;
await workspace.writeText(files.rules.filename, ppCleanRules(res.text));
