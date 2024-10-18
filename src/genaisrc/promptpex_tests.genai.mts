import { ppCleanRules, ppFiles, ppModelOptions } from "./promptpex.mts";

script({
  title: "PromptPex Rules Generator",
  files: ["samples/speech-tag.prompty"],
  description:
    "Generate a rules file for a prompt template. Runs this script against a prompt authored in markdown or prompty format.",
});

const num = env.vars || 10;
const files = await ppFiles();

if (!files.inputSpec.content) throw new Error("No input spec found");

const rules = [files.rules.content, files.inverseRules.content]
  .filter((s) => !!s)
  .join("\n");

if (!rules) throw new Error("No rules found");

const resTests = await runPrompt(
  (ctx) => {
    ctx.importTemplate("src/prompts/test.prompty", {
      input_spec: files.inputSpec.content,
      context: files.prompt.content,
      num,
      rule: rules,
    });
  },
  {
    ...ppModelOptions(),
    label: "generate tests",
  }
);
if (resTests.error) throw resTests.error;
await workspace.writeText(files.tests.filename, resTests.text);
