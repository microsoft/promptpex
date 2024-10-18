export async function ppFiles(promptFile?: WorkspaceFile) {
  if (!promptFile)
    promptFile = env.files.find(({ filename }) =>
      /\.(md|prompty)$/i.test(filename)
    );
  const dir = path.dirname(promptFile.filename);
  const basename = path.basename(promptFile.filename);
  const rules = path.join(dir, basename + ".rules.md");
  const inverseRules = path.join(dir, basename + ".inverse_rules.md");
  const instructions = path.join(dir, basename + ".instructions.md");
  const inputSpec = path.join(dir, basename + ".input_spec.md");
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

export function ppModelOptions(): PromptGeneratorOptions {
  return {
    model: "large",
    system: ["system.safety_harmful_content", "system.safety_jailbreak"],
  };
}

export function ppCleanRules(text: string) {
  return text
    .split(/\n/g)
    .filter((s) => !!s)
    .join("\n");
}
