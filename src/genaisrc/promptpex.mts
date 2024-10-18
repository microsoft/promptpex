export interface PromptPexContext {
  dir: string;
  basename: string;
  prompt: WorkspaceFile;
  rules: WorkspaceFile;
  inverseRules: WorkspaceFile;
  instructions: WorkspaceFile;
  inputSpec: WorkspaceFile;
  tests: WorkspaceFile;
}

export async function loadPromptContext(
  promptFile?: WorkspaceFile
): Promise<PromptPexContext> {
  if (!promptFile)
    promptFile = env.files.find(({ filename }) =>
      /\.(md|prompty)$/i.test(filename)
    );
  const dir = path.dirname(promptFile.filename);
  const basename = path
    .basename(promptFile.filename)
    .slice(0, -path.extname(promptFile.filename).length);
  const rules = path.join(dir, basename + ".rules.txt");
  const inverseRules = path.join(dir, basename + ".inverse_rules.txt");
  const instructions = path.join(dir, basename + ".instructions.txt");
  const inputSpec = path.join(dir, basename + ".input_spec.txt");
  const tests = path.join(dir, basename + ".tests.csv");

  return {
    dir,
    basename,
    prompt: promptFile,
    rules: await workspace.readText(rules),
    inverseRules: await workspace.readText(inverseRules),
    instructions: await workspace.readText(instructions),
    inputSpec: await workspace.readText(inputSpec),
    tests: await workspace.readText(tests),
  };
}

function modelOptions(): PromptGeneratorOptions {
  return {
    model: "large",
    system: ["system.safety_harmful_content", "system.safety_jailbreak"],
  };
}

function tidyRules(text: string) {
  return text
    .split(/\n/g)
    .filter((s) => !!s)
    .join("\n");
}

export async function generateInputSpec(
  files: Pick<PromptPexContext, "inputSpec" | "prompt">
) {
  const res = await runPrompt(
    (ctx) => {
      ctx.importTemplate("src/prompts/input_spec.prompty", {
        context: files.prompt.content,
        input_spec: files.inputSpec?.content || "",
      });
    },
    {
      ...modelOptions(),
      label: "generate input spec",
    }
  );
  if (res.error) throw res.error;
  return tidyRules(res.text);
}

export async function generateRules(
  files: Pick<PromptPexContext, "prompt">,
  options?: { numRules: number }
) {
  const { numRules = 3 } = options || {};
  // generate rules
  const res = await runPrompt(
    (ctx) => {
      ctx.importTemplate("src/prompts/rules_global.prompty", {
        num_rules: numRules,
        input_data: files.prompt.content,
      });
    },
    {
      ...modelOptions(),
      label: "generate rules",
    }
  );
  if (res.error) throw res.error;
  return tidyRules(res.text);
}

export async function generateInverseRules(
  files: Pick<PromptPexContext, "prompt" | "rules" | "inverseRules">
) {
  const res = await runPrompt(
    (ctx) => {
      ctx.importTemplate("src/prompts/inverse_rule.prompty", {
        rule: files.rules.content,
      });
    },
    {
      ...modelOptions(),
      label: "inverse rules",
    }
  );
  if (res.error) throw res.error;
  return tidyRules(res.text);
}

export async function generateTests(
  files: Pick<
    PromptPexContext,
    "prompt" | "inputSpec" | "rules" | "inverseRules"
  >,
  options: { num: number }
) {
  const { num } = options;

  if (!files.rules.content) throw new Error("No rules found");
  if (!files.inputSpec.content) throw new Error("No input spec found");
  const rules = [files.rules.content, files.inverseRules.content]
    .filter((s) => !!s)
    .join("\n");
  if (!rules) throw new Error("No rules found");

  const res = await runPrompt(
    (ctx) => {
      ctx.importTemplate("src/prompts/test.prompty", {
        input_spec: files.inputSpec.content,
        context: files.prompt.content,
        num,
        rule: rules,
      });
    },
    {
      ...modelOptions(),
      label: "generate tests",
    }
  );
  if (res.error) throw res.error;
  return res.text;
}
