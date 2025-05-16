#!/usr/bin/env zx

import { $ } from "zx";
import path from "path";

// List of 8 .prompty files to substitute for speech-tag.prompty
const promptyFilesAll = [
    "samples/speech-tag/speech-tag.prompty",
    "samples/text-to-p/text-to-p.prompty",
    "samples/openai-examples/elements.prompty",
    "samples/big-prompt-lib/art-prompt.prompty",
    "samples/prompt-guide/extract-names.prompty",
    "samples/text-classification/classify-input-text.prompty",
    "samples/big-prompt-lib/sentence-rewrite.prompty",
    "samples/azure-ai-studio/shakespearean-writing-assistant.prompty",
];

const promptyFilesAll_ = [

    "samples/speech-tag/speech-tag.prompty",

];

// Get current date in YYYY-MM-DD format
const dateStr = new Date().toISOString().slice(0, 10);
const outDir = `evals/test-all-${dateStr}`;

// for (const prompty of promptyFilesAll.slice(0, 1)) {
for (const prompty of promptyFilesAll) {
    const promptyFileBase = path.basename(prompty, path.extname(prompty));

    await $`npm run promptpex ${prompty} -- --vars "splitRules=true" --vars "maxRulesPerTestGeneration=5" --vars "testGenerations=1" --vars "evals=true" --vars "testExpansions=0" --vars "compliance=true" --vars "baselineTests=false" --vars "modelsUnderTest=ollama:llama3.2:1b" --vars "out=${outDir}/${promptyFileBase}"`;
}

//    await $`npm run promptpex ${prompty} -- --vars "splitRules=true" --vars "maxRulesPerTestGeneration=5" --vars "testGenerations=1" --vars "evals=true" --vars"testExpansions=0" --vars "compliance=true" --vars baselineTests=false --vars "modelsUnderTest=azure:gpt-4o-mini_2024-07-18;ollama:gemma2:9b;ollama:qwen2.5:3b;ollama:llama3.2:1b" --vars "out=${outDir}/${promptyFileBase}"`;