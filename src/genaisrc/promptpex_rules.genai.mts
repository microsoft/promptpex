import { ppModelOptions, ppFiles, ppCleanRules } from "./promptpex.mts";

script({
  title: "PromptPex Rules Generator",
  description:
    "Generate a rules file for a prompt template. Runs this script against a prompt authored in markdown or prompty format.",
  files: ["samples/speech-tag.prompty"],
  system: [],
  parameters: {
    allow: {
      type: "string",
      description: "Additional instructions for allowed rules.",
    },
    deny: {
      type: "string",
      description: "Additional instructions for denied rules.",
    },
    numRules: {
      type: "number",
      description: "Number of rules to generate.",
      default: 3,
    },
  },
});

const { deny, allow, numRules } = env.vars;
const files = await ppFiles();

const res = await runPrompt((ctx) => {
  ctx.importTemplate(
    "src/prompts/generic_rules_global.prompty",
    {
      allow,
      deny,
      numRules,
      instructions: files.instructions?.content || "",
      inputData: files.prompt.content,
    },
    {
      ...ppModelOptions(),
    }
  );
});
if (res.error) throw res.error;
await workspace.writeText(files.rules.filename, ppCleanRules(res.text));
