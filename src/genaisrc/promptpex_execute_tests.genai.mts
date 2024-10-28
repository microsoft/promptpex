import {
  loadPromptContext,
  executeTests,
  generateReports,
} from "./promptpex.mts";

script({
  title: "PromptPex Test Executor",
  files: ["samples/speech-tag/speech-tag.prompty"],
  description: "",
  parameters: {
    force: {
      type: "boolean",
      description: "Force execution even if tests are already present",
      default: false,
    },
    models: {
      type: "string",
      description: "Models to use for testing",
      default: "github:gpt-4o-mini",
    },
  },
});

const force = env.vars.force;
const models = env.vars.models.split(/;/g).map((model) => model.trim());

const files = (await loadPromptContext())[0];

// generate tests
const testResults = await executeTests(files, { force, models });
await workspace.writeText(files.testResults.filename, testResults);

// generate report
await generateReports(files);
