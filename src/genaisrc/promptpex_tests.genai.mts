import { ppFiles, generateTests } from "./promptpex.mts";

script({
  title: "PromptPex Rules Generator",
  files: ["samples/speech-tag.prompty"],
  description:
    "Generate a rules file for a prompt template. Runs this script against a prompt authored in markdown or prompty format.",
});

const num = parseInt(env.vars.num) || 10;
const files = await ppFiles();

const tests = await generateTests(files, { num });
await workspace.writeText(files.tests.filename, tests);
