import { modelOptions, loadPromptContext, tidyRules } from "./promptpex.mts";

script({
  title: "PromptPex Rules Generator",
  description:
    "Generate a rules file for a prompt template. Runs this script against a prompt authored in markdown or prompty format.",
  files: ["samples/speech-tag.prompty"],
});

const files = await loadPromptContext();

// generate rules
const resRules = await runPrompt(
  (ctx) => {
    ctx.importTemplate("src/prompts/rules_global.prompty", {
      input_data: files.prompt.content,
    });
  },
  {
    ...modelOptions(),
    label: "generate rules",
  }
);
if (resRules.error) throw resRules.error;
const rules = tidyRules(resRules.text);
await workspace.writeText(files.rules.filename, rules);

// inverse rules
const resInverseRules = await runPrompt(
  (ctx) => {
    ctx.importTemplate("src/prompts/inverse_rule.prompty", {
      rule: rules,
    });
  },
  {
    ...modelOptions(),
    label: "inverse rules",
  }
);
if (resInverseRules.error) throw resInverseRules.error;
await workspace.writeText(
  files.inverseRules.filename,
  tidyRules(resInverseRules.text)
);
