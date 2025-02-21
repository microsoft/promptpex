import {
    generateInputSpec,
    generateOutputRules,
    generateInverseOutputRules,
    generateTests,
} from "./src/generation.mts";
import {
    outputBackgroundInformation,
    outputFile,
    outputLines,
} from "./src/output.mts";
import {
    loadPromptFiles,
    parseRulesTests,
    parseTestResults,
} from "./src/parsers.mts";
import { runTests } from "./src/testrun.mts";
import type { PromptPexOptions } from "./src/types.mts";

script({
    title: "PromptPex Test Generator",
    description: `Generate tests for a LLM prompt using PromptPex.

<details><summary>What is PromptPex?</summary>
  This tool accepts a prompt file formatted in Markdown
  and generates tests for them. The tests can be used to validate your prompt
  for various models automatically.

  - [Markdown Prompty Syntax](https://prompty.ai/docs)
  - [GitHub](https://github.com/microsoft/promptpex/)
  - [Archiv](https://github.com/microsoft/promptpex/)

  PromptPex uses an LLM internally to generate and evaluate test cases and results.
  PromptPex was tested using OpenAI GPT-4o / Llama3.3 70b. Results on other models may vary.
</details>

<details><summary>Prompt format</summary>

PromptPex accepts prompts formatted in Markdown with a YAML frontmatter section (optional).

\`\`\`markdown
---
...
inputs:
  some_imput:
    type: "string"
---
system:
This is your system prompt.

user:
This is your user prompt.
{{ some_input }}
 \`\`\`

- The content of the markdoown is the chat conversation. 
\`system:\` is the system prompt and \`user:\` is the user prompt.
- The input variables are defined in the frontmatter of the prompt.
- If not input variables are defined, PromptPex will append the generated test to the user prompt.

### Frontmatter

You can override parts of the test generation
process by providing values in the frontmatter of the prompt (all values are optional).

\`\`\`markdown
---
...
promptPex:
  inputSpec: "input constraints"
  outputRules: "output constraints"
  inverseOutputRules: "inverted output constraints"
  intent: "intent of the prompt"
  instructions:
    inputSpec: "Additional input specification instructions"
    outputRules: "Additional output rules instructions"
    inverseOutputRules: "Additional inverse output rules instructions"
    intent: "Additional intent of the prompt"
---
\`\`\`

</details>
`,
    accept: ".prompty,*.md,*.txt",
    parameters: {
        disableSafety: {
            type: "boolean",
            description:
                "Do not include safety system prompts and do not run safety content service",
            default: false,
        },
        rulesModel: {
            type: "string",
            description: "Model used to generate rules (you can also override the model alias 'rules'",
            enum: [
                "openai:gpt-4o",
                "ollama:llama3.3:70b",
                "lmstudio:llama-3.3-70b"
            ],
        },
        evalModel: {
            type: "string",
            description: "Model used to evaluate rules (you can also override the model alias 'eval'",
            enum: [
                "openai:gpt-4o",
                "ollama:llama3.3:70b",
                "lmstudio:llama-3.3-70b"
            ],
        },
        models: {
            type: "string",
            description:
                "List of models to run the prompt again; semi-colon separated",
        },
        compliance: {
            type: "boolean",
            description: "Evaluate Test Result compliance",
            default: false,
        },
        inputSpecInstructions: {
            type: "string",
            title: "Input Specification instructions",
            description:
                "These instructions will be added to the input specification generation prompt.",
        },
        outputRulesInstructions: {
            type: "string",
            title: "Output Rules instructions",
            description:
                "These instructions will be added to the output rules generation prompt.",
        },
        inverseOutputRulesInstructions: {
            type: "string",
            title: "Inverse Output Rules instructions",
            description:
                "These instructions will be added to the inverse output rules generation prompt.",
        },
    },
});

const { output, meta, vars } = env;
const {
    disableSafety,
    inputSpecInstructions,
    outputRulesInstructions,
    inverseOutputRulesInstructions,
    compliance,
    rulesModel,
    evalModel,
} = vars;
const models = (vars.models || "").split(/;/g).filter((m) => !!m);
const options: PromptPexOptions = {
    disableSafety,
    instructions: {
        inputSpec: inputSpecInstructions,
        outputRules: outputRulesInstructions,
        inverseOutputRules: inverseOutputRulesInstructions,
    },
    workflowDiagram: true,
    rulesModel,
    evalModel,
};
const files = await loadPromptFiles(env.files[0], options);

output.heading(2, `PromptPex for ${files.name}`);
output.itemValue(`model`, meta.model);
output.detailsFenced(`options`, options, "yaml");
await outputBackgroundInformation();

// prompt info
output.heading(3, `Prompt Under Test`);
output.itemValue(`filename`, files.prompt.filename);
output.fence(files.prompt.content, "md");

// generate input spec
output.heading(3, "Input Specification");
files.inputSpec.content = await generateInputSpec(files, options);
outputFile(files.inputSpec);

// generate rules
output.heading(3, "Output Rules");
files.rules.content = await generateOutputRules(files, options);
outputLines(files.rules, "rule");

// generate inverse rules
output.heading(3, "Inverse Output Rules");
files.inverseRules.content = await generateInverseOutputRules(files, options);
outputLines(files.inverseRules, "inverse rule");

// generate tests
output.heading(3, "Tests");
files.tests.content = await generateTests(files, options);
const tests = parseRulesTests(files.tests.content).map(
    ({ testinput, expectedoutput }) => ({ testinput, expectedoutput })
);
output.table(tests);
output.detailsFenced(`data`, tests, "csv");
output.detailsFenced(`generated`, files.tests.content);

if (!models?.length) {
    output.warn(`No models specified. Skipping test run.`);
} else {
    // run tests against the model(s)
    output.heading(3, `Test Results`);
    files.testOutputs.content = await runTests(files, {
        models,
        compliance,
    });
    const results = parseTestResults(files);
    output.table(
        results.map(
            ({
                rule,
                inverse,
                model,
                input,
                output,
                compliance: testCompliance,
            }) => ({
                rule,
                model,
                input,
                output,
                compliance: compliance
                    ? testCompliance === "ok"
                        ? "✓"
                        : "✗"
                    : undefined,
                inverse: inverse ? "✓" : "",
            })
        )
    );
    output.detailsFenced(`data`, results, "csv");
}
