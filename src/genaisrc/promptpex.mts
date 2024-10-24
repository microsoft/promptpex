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

export async function loadPromptContext(): Promise<PromptPexContext[]> {
  const q = host.promiseQueue(5);
  return q.mapAll(
    env.files.filter((f) => /\.(md|txt|prompty)$/i.test(f.filename)),
    async (f) => await loadPromptFiles(f)
  );
}

export async function loadPromptFiles(
  promptFile: WorkspaceFile
): Promise<PromptPexContext> {
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
  } satisfies PromptPexContext;
}

function modelOptions(): PromptGeneratorOptions {
  return {
    model: "large",
    system: ["system.safety_harmful_content", "system.safety_jailbreak"],
  };
}

function tidyRules(text: string) {
  if (/i can't assist with that/i.test(text)) return "";
  return text
    .split(/\n/g)
    .map((line) => line.replace(/^(\d+\.|_|\*)\s+/i, "")) // unneded numbering
    .filter((s) => !!s)
    .join("\n");
}

export async function generateInputSpec(
  files: Pick<PromptPexContext, "prompt">
) {
  const context = MD.content(files.prompt.content);
  const res = await runPrompt(
    (ctx) => {
      ctx.importTemplate("src/prompts/input_spec.prompty", {
        context,
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
  const input_data = MD.content(files.prompt.content);
  const res = await runPrompt(
    (ctx) => {
      ctx.importTemplate("src/prompts/rules_global.prompty", {
        num_rules: numRules,
        input_data,
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
  const rule = MD.content(files.rules.content);
  const res = await runPrompt(
    (ctx) => {
      ctx.importTemplate("src/prompts/inverse_rule.prompty", {
        rule,
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
  options?: { num: number }
) {
  const { num = 3 } = options || {};

  if (!files.rules.content) throw new Error("No rules found");
  if (!files.inputSpec.content) throw new Error("No input spec found");
  const rules = [files.rules.content, files.inverseRules.content]
    .filter((s) => !!s)
    .join("\n");
  if (!rules) throw new Error("No rules found");

  const context = MD.content(files.prompt.content);
  const res = await runPrompt(
    (ctx) => {
      ctx.importTemplate("src/prompts/test.prompty", {
        input_spec: files.inputSpec.content,
        context,
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

export async function generate(
  files: PromptPexContext,
  options?: { force?: boolean; q: PromiseQueue }
) {
  const { force = false, q } = options || {};
  // generate input spec
  if (!files.inputSpec.content || force) {
    files.inputSpec.content = await generateInputSpec(files);
    await workspace.writeText(
      files.inputSpec.filename,
      files.inputSpec.content
    );
  } else {
    console.log(
      `input spec ${files.inputSpec.filename} already exists. Skipping generation.`
    );
  }

  // generate rules
  if (!files.rules.content || force) {
    files.rules.content = await generateRules(files);
    await workspace.writeText(files.rules.filename, files.rules.content);
    files.inverseRules.content = undefined;
    files.tests.content = undefined;
  } else {
    console.log(
      `rules ${files.rules.filename} already exists. Skipping generation.`
    );
  }

  // generate inverse rules
  if (!files.inverseRules.content || force) {
    const inverseRules = await generateInverseRules(files);
    if (!inverseRules) console.warn("No inverse rules generated");
    await workspace.writeText(files.inverseRules.filename, inverseRules);
    files.tests.content = undefined;
  } else {
    console.log(
      `inverse rules ${files.inverseRules.filename} already exists. Skipping generation.`
    );
  }

  // generate tests
  if (!files.tests.content || force) {
    files.tests.content = await generateTests(files);
    await workspace.writeText(files.tests.filename, files.tests.content);
  } else {
    console.log(
      `tests ${files.tests.filename} already exists. Skipping generation.`
    );
  }
}
