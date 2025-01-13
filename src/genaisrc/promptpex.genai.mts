import { loadPromptContext, generate, computeOverview } from "./promptpex.mts";

script({
  title: "PromptPex Test Generator",
  description: "Generate tests using PromptPex.",
  files: ["samples/speech-tag/speech-tag.prompty"],
  accept: ".prompty",
  parameters: {
    disableSafety: {
      type: "boolean",
      description:
        "Do not include safety system prompts and do not run safety content service",
      default: false,
    },
    force: {
      type: "boolean",
      description: "Force overwrite of existing files",
      default: false,
    },
    evals: {
      type: "boolean",
      description: "Evaluate quality of generated tests",
      default: true,
    },
    models: {
      type: "string",
      description: "List of models to evaluate",
      default: "",
    },
    out: {
      type: "string",
      description: "Output directory",
      default: "",
    },
  },
});

const { disableSafety, force, out } = env.vars;

const prompts = await loadPromptContext(out);
const models = (env.vars.models || "github:gpt-4o-mini")
  ?.split(/[;\n ,]/g)
  .map((model) => model.trim());

const res = [];
const options = Object.freeze({
  disableSafety,
  force,
  models,
});
for (const files of prompts) {
  try {
    const ctx = await generate(files, options);
    const { testEvals, rules, ruleEvals, overview } = computeOverview(ctx, {
      percent: false,
    });
    res.push({
      prompt: files.name,
      rules: rules.filter((r) => !r.inverse).length,
      ["rules grounded"]: ruleEvals.filter((g) => g.grounded === "ok").length,
      tests: testEvals.length,
      ...Object.fromEntries(
        overview.map((o) => [o.model, o["tests compliant"]])
      ),
    });
  } catch (e) {
    console.error(e);
    console.debug(e.stack);
  }
}

/*
res.sort((a, b) => a.prompt.localeCompare(b.prompt));
await workspace.writeText(
  "evals/README.md",
  `# Eval summary
  
## Test Results

- % represent compliance rate

${CSV.markdownify(res)}

`
);
*/