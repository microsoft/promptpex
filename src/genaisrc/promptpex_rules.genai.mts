import {
  modelOptions,
  loadPromptContext,
  tidyRules,
  generateRules,
  generateInverseRules,
} from "./promptpex.mts";

script({
  title: "PromptPex Rules Generator",
  description:
    "Generate a rules file for a prompt template. Runs this script against a prompt authored in markdown or prompty format.",
  files: ["samples/speech-tag/speech-tag.prompty"],
});

const files = await loadPromptContext();

// generate rules
files.rules.content = await generateRules(files);
await workspace.writeText(files.rules.filename, files.rules.content);

// generate inverse rules
const inverseRules = await generateInverseRules(files);
await workspace.writeText(files.inverseRules.filename, inverseRules);
