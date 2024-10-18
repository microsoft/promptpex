export async function ppFiles(promptFile?: WorkspaceFile) {
  if (!promptFile)
    promptFile = env.files.find(({ filename }) =>
      /\.(md|prompty)$/i.test(filename)
    );
  const dir = path.dirname(promptFile.filename);
  const basename = path.basename(promptFile.filename);
  const rules = path.join(dir, basename + ".rules.md");
  const instructions = path.join(dir, basename + ".instructions.md");
  const inputSpec = path.join(dir, basename + ".input_spec.md");

  return {
    dir,
    basename,
    prompt: promptFile,
    rules: await workspace.readText(rules),
    instructions: await workspace.readText(instructions),
    inputSpec: await workspace.readText(inputSpec),
  };
}

export function ppModelOptions(): ModelOptions {
  return {
    model: "large",
  };
}

export function ppCleanRules(text: string) {
  return text
    .split(/\n/g)
    .filter((s) => !!s)
    .join("\n");
}
