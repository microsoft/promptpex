import { loadPromptContext, generateInputSpec } from "./promptpex.mts";

script({
  title: "PromptPex Input Spec Generator",
  description:
    "Generate an input spec for a prompt template. Runs this script against a prompt authored in markdown or prompty format.",
  files: ["samples/speech-tag/speech-tag.prompty"],
});

const files = await loadPromptContext();

// generate input specs
const inputSpec = await generateInputSpec(files);
await workspace.writeText(files.inputSpec.filename, inputSpec);
