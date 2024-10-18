import { ppModelOptions, ppFiles, ppCleanRules } from "./promptpex.mts";

script({
  title: "PromptPex Input Spec Generator",
  description:
    "Generate an input spec for a prompt template. Runs this script against a prompt authored in markdown or prompty format.",
  files: ["samples/speech-tag.prompty"],
  system: ["system.safety_harmful_content", "system.safety_jailbreak"],
});

const files = await ppFiles();

const res = await runPrompt(
  (ctx) => {
    ctx.importTemplate("src/prompts/input_spec.prompty", {
      context: files.prompt.content,
      input_spec: files.inputSpec?.content || "",
    });
  },
  {
    ...ppModelOptions(),
  }
);
if (res.error) throw res.error;
await workspace.writeText(files.inputSpec.filename, ppCleanRules(res.text));
