import {
    generateInputSpec,
    generateInverseRules,
    generateRules,
    generateTests,
    loadPromptFiles,
    outputBackgroundInformation,
    outputFile,
    parseRulesTests,
    parseTestResults,
    PromptPexOptions,
    runTests,
} from "./promptpex.mts";

script({
    title: "PromptPex Test Generator",
    description: `Generate tests for a LLM prompt using PromptPex.
<details><summary>Frontmatter configuration</summary>
You can override parts of the test generation
process by providing values in the frontmatter of the prompt.

\`\`\`yaml
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
\`\`\`

</details>
<details><summary>What is PromptPex?</summary>
  This tool accepts a prompt file formatted in Markdown (Prompty format)
  and generates tests for them. The tests can be used to validate your prompt
  for various models automatically.

  - [Markdown Prompty Syntax](https://prompty.ai/docs)
  - [GitHub](https://github.com/microsoft/promptpex/)
  - [Archiv](https://github.com/microsoft/promptpex/)

  PromptPex uses an LLM internally to generate and evaluate test cases and results.
  PromptPex was tested using OpenAI GPT-4o / Llama3.3 70b. Results on other models may vary.
</details>
`,
    accept: ".prompty,*.md",
    parameters: {
        disableSafety: {
            type: "boolean",
            description:
                "Do not include safety system prompts and do not run safety content service",
            default: false,
        },
        models: {
            type: "string",
            description:
                "List of models to run the prompt again; semi-colon separated",
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
files.rules.content = await generateRules(files, options);
outputFile(files.rules);

// generate inverse rules
output.heading(3, "Inverse Output Rules");
files.inverseRules.content = await generateInverseRules(files, options);
outputFile(files.inverseRules);

// generate tests
output.heading(3, "Tests");
files.tests.content = await generateTests(files, options);
const tests = parseRulesTests(files.tests.content).map(
    ({ testinput, expectedoutput }) => ({ testinput, expectedoutput })
);
output.table(tests);
output.detailsFenced(`data`, tests, "json");
output.detailsFenced(`generated`, files.tests.content);

// run tests against the model(s)
for (const model of models) {
    output.heading(3, `Testing against ${model}`);
    files.testOutputs.content = await runTests(files, model);
    const results = parseTestResults(files);
    output.table(results);
    output.detailsFenced(`data`, results, "json");
}
