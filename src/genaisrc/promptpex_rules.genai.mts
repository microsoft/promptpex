import { ppModelOptions, ppFiles, ppCleanRules } from "./promptpex.mts";

script({
  title: "PromptPex Rules Generator",
  description:
    "Generate a rules file for a prompt template. Runs this script against a prompt authored in markdown or prompty format.",
  files: ["samples/speech-tag.prompty"],
});

const files = await ppFiles();

// generate rules
const resRules = await runPrompt(
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
if (resRules.error) throw resRules.error;
const rules = ppCleanRules(resRules.text);
await workspace.writeText(files.rules.filename, rules);

// inverse rules
const resInverseRules = await runPrompt(
  (ctx) => {
    ctx.importTemplate("src/prompts/inverse_rule.prompty", {
      rule: rules,
    });
  },
  {
    ...ppModelOptions(),
    label: "inverse rules",
  }
);
if (resInverseRules.error) throw resInverseRules.error;
await workspace.writeText(
  files.inverseRules.filename,
  ppCleanRules(resInverseRules.text)
);
