#!/usr/bin/env zx

import { $ } from "zx";
import path from "path";

// Parse command line arguments
const args = process.argv.slice(3); // Skip node, zx, and script filename
if (args.length < 2) {
    console.log("Usage: zx run-samples-modular.zx.mjs <useTestSetup> <phase>");
    console.log("  useTestSetup: true/false - determines if it uses the test setup");
    console.log("  phase: gen|run|eval|all - which phases to run");
    process.exit(1);
}

const useTestSetup = args[0].toLowerCase() === 'true';
const phase = args[1].toLowerCase();

if (!['gen', 'run', 'eval', 'all'].includes(phase)) {
    console.error("Error: phase must be one of: gen, run, eval, all");
    process.exit(1);
}

console.log(`Running with testSetup=${useTestSetup}, phase=${phase}`);

// List of 8 .prompty files to substitute for speech-tag.prompty
const promptyFilesAll_8 = [
    "samples/speech-tag/speech-tag.prompty",
    "samples/text-to-p/text-to-p.prompty",
    "samples/openai-examples/elements.prompty",
    "samples/big-prompt-lib/art-prompt.prompty",
    "samples/prompt-guide/extract-names.prompty",
    "samples/text-classification/classify-input-text.prompty",
    "samples/big-prompt-lib/sentence-rewrite.prompty",
    "samples/azure-ai-studio/shakespearean-writing-assistant.prompty",
];

const promptyFilesAll_new = [
"samples/big-prompt-library-chatgpt/crewai_assistant_qqtuuwsby.prompty",
"samples/big-prompt-library-chatgpt/fragrance_finder_deluxe_e9avvjxcw.prompty",
"samples/big-prompt-library-chatgpt/information_kiosk_building_j6ry5iscb.prompty",
"samples/big-prompt-library-chatgpt/thread_weaver_krog0f5tg.prompty",
"samples/big-prompt-library-chatgpt/hurtig_ingeni_r_pgktzdcfk.prompty"
];

const promptyFilesAll_full = [
"samples/big-prompt-library-chatgpt/crewai_assistant_qqtuuwsby.prompty",
"samples/big-prompt-library-chatgpt/fragrance_finder_deluxe_e9avvjxcw.prompty",
"samples/big-prompt-library-chatgpt/information_kiosk_building_j6ry5iscb.prompty",
"samples/big-prompt-library-chatgpt/thread_weaver_krog0f5tg.prompty",
"samples/big-prompt-library-chatgpt/hurtig_ingeni_r_pgktzdcfk.prompty",

    "samples/speech-tag/speech-tag.prompty",
    "samples/text-to-p/text-to-p.prompty",
    "samples/openai-examples/elements.prompty",
    "samples/big-prompt-lib/art-prompt.prompty",
    "samples/prompt-guide/extract-names.prompty",
    "samples/text-classification/classify-input-text.prompty",
    "samples/big-prompt-lib/sentence-rewrite.prompty",
    "samples/azure-ai-studio/shakespearean-writing-assistant.prompty",
];

const promptyFilesAll_Sept26 = [
"samples/awesome-chatgpt-prompts/architect_guide_for_programmers.prompty",
"samples/awesome-chatgpt-prompts/unconstrained_ai_model_dan.prompty",
"samples/awesome-chatgpt-prompts/idea_clarifier_gpt.prompty",
"samples/awesome-chatgpt-prompts/structured_iterative_reasoning_protocol_sirp.prompty",
"samples/awesome-chatgpt-prompts/tech_challenged_customer.prompty",

"samples/big-prompt-library-gemini/learning_coach.prompty",
"samples/big-prompt-library-gemini/writing_editor.prompty",
"samples/big-prompt-library-gemini/coding_partner.prompty",
"samples/big-prompt-library-gemini/brainstormer.prompty",
"samples/big-prompt-library-gemini/career_guide.prompty"
];

// rerun original samples with more tests, balanced rule/inverse rules
const promptyFilesAll_Sept29 = [
    "samples/speech-tag/speech-tag.prompty",
    "samples/text-to-p/text-to-p.prompty",
    "samples/openai-examples/elements.prompty",
    "samples/big-prompt-lib/art-prompt.prompty",
    "samples/prompt-guide/extract-names.prompty",
    "samples/text-classification/classify-input-text.prompty",
    "samples/big-prompt-lib/sentence-rewrite.prompty",
    "samples/azure-ai-studio/shakespearean-writing-assistant.prompty",

"samples/awesome-chatgpt-prompts/synonym_finder.prompty",
"samples/awesome-chatgpt-prompts/instructor_in_a_school.prompty",

"samples/big-prompt-library-chatgpt/dev_helper_upyxwdlcg.prompty",
"samples/big-prompt-library-chatgpt/url_to_business_plan_a3znu5fsn.prompty",
"samples/big-prompt-library-chatgpt/prompt_creator_8ope0amfj.prompty"
];

const promptyFilesAll_Sept29new = [
"samples/awesome-chatgpt-prompts/synonym_finder.prompty",
"samples/awesome-chatgpt-prompts/instructor_in_a_school.prompty",

"samples/big-prompt-library-chatgpt/dev_helper_upyxwdlcg.prompty",
"samples/big-prompt-library-chatgpt/url_to_business_plan_a3znu5fsn.prompty",
"samples/big-prompt-library-chatgpt/prompt_creator_8ope0amfj.prompty"
];

const promptyFilesAll_1 = [

    "samples/openai-examples/elements.prompty",

];

// Get current date in YYYY-MM-DD format
const dateStr = new Date().toISOString().slice(0, 10);

const testGeneration = useTestSetup ? "debug" : "all-2025-09-29";

// Select prompty files based on useTestSetup
// const promptyFilesAll = useTestSetup ? promptyFilesAll_1 : promptyFilesAll_8;
// const promptyFilesAll = useTestSetup ? promptyFilesAll_1 : promptyFilesAll_1;
const promptyFilesAll = useTestSetup ? promptyFilesAll_1 : promptyFilesAll_Sept29;

console.log("=== Settings ===");
console.log(`useTestSetup: ${useTestSetup}`);
console.log(`phase: ${phase}`);
console.log(`promptyFilesAll: ${promptyFilesAll.join(", ")}`);
//
// generate the tests
//

const outDirG = `evals/test-${testGeneration}/gen`;
const outDirR = `evals/test-${testGeneration}/run`;
const outDirE = `evals/test-${testGeneration}/eval`;

const testSetup = useTestSetup;

if (phase === 'gen' || phase === 'all') {
    console.log("=== GENERATION PHASE ===");
    // generate the set of tests
    for (const prompty of promptyFilesAll) {
        const promptyFileBase = path.basename(prompty, path.extname(prompty));

        try {
            if (testSetup) {
                const evalModel = "azure:gpt-4.1-mini_2025-04-14";
                const groundTruthModel="azure:gpt-4.1-mini_2025-04-14"
                const evalModelGroundtruth="azure:gpt-4.1-mini_2025-04-14"
                console.log(`Running generation for ${promptyFileBase} with testSetup models (${groundTruthModel})`);
                await $`npm run promptpex ${prompty} -- --vars \"effort=min\" --vars \"groundtruthModel=${groundTruthModel}\" --vars \"evals=false\" --vars \"compliance=true\" --vars \"testValidity=true\" --vars \"baselineTests=true\" --vars \"baselineModel=${groundTruthModel}\" --vars \"evalModel=${evalModel}\" --vars \"evalModelGroundtruth=${evalModelGroundtruth}\" --vars \"out=${outDirG}/${promptyFileBase}\"`;
            } else {
                const evalModel = "azure:o4-mini_2025-04-16";
                const groundTruthModel="azure:gpt-5_2025-08-07"
                const evalModelGroundtruth="azure:o4-mini_2025-04-16"
                console.log(`Running generation for ${promptyFileBase} with production models (${groundTruthModel})`);
                await $`npm run promptpex ${prompty} -- --vars \"effort=min\" --vars \"groundtruthModel=${groundTruthModel}\" --vars \"evals=false\" --vars \"compliance=true\" --vars \"testValidity=true\" --vars \"baselineTests=true\" --vars \"baselineModel=${groundTruthModel}\" --vars \"evalModel=${evalModel}\" --vars \"evalModelGroundtruth=${evalModelGroundtruth}\" --vars \"out=${outDirG}/${promptyFileBase}\"`;
            }
        } catch (err) {
            console.error(`Error generating tests with promptpex for ${prompty}:`, err);
        }
    }
}

//
// run the tests
// 

if (phase === 'run' || phase === 'all') {
    console.log("=== RUN PHASE ===");
    // run the tests
    for (const prompty of promptyFilesAll) {
        const promptyFileBase = path.basename(prompty, path.extname(prompty));
        const ctxFile = `${outDirG}/${promptyFileBase}/${promptyFileBase}/promptpex_context.json`
        //const ctxFile = `promptpex_context.json`
        console.log(`Running tests for ${promptyFileBase} ... from  ${ctxFile}`);
        // copy into current directory
        await $`cp ${ctxFile} .`

        try {
            if (testSetup) {
                const modelsUnderTest="ollama:qwen2.5:3b"
                console.log(`Running tests for ${promptyFileBase} with testSetup models (${modelsUnderTest})`);
                await $`npm run promptpex promptpex_context.json -- --vars \"evals=false\" --vars \"compliance=false\" --vars \"baselineTests=false\" --vars \"modelsUnderTest=${modelsUnderTest}\" --vars \"out=${outDirR}/${promptyFileBase}\"`;
            } else {
                const modelsUnderTest="ollama:gemma2:9b;ollama:qwen2.5:3b;ollama:gpt-oss;ollama:llama3.2:1b"
                console.log(`Running tests for ${promptyFileBase} with production models (${modelsUnderTest})`);
                await $`npm run promptpex promptpex_context.json -- --vars \"evals=false\" --vars \"compliance=false\" --vars \"baselineTests=false\" --vars \"modelsUnderTest=ollama:gemma2:9b;ollama:qwen2.5:3b;ollama:gpt-oss;ollama:llama3.2:1b\" --vars \"maxTestsToRun=50\" --vars \"runsPerTest=1\" --vars \"out=${outDirR}/${promptyFileBase}\"`;
            }
        } catch (err) {
            console.error(`Error running tests for ${prompty}:`, err);
        }
    }
}

//
// eval the tests
//

if (phase === 'eval' || phase === 'all') {
    console.log("=== EVAL PHASE ===");
    // evaluate the tests
    for (const prompty of promptyFilesAll) {
        const promptyFileBase = path.basename(prompty, path.extname(prompty));
        const ctxFile = `${outDirR}/${promptyFileBase}/${promptyFileBase}/promptpex_context.json`
        console.log(`Evaling tests for ${promptyFileBase} ... from  ${ctxFile}`);
        await $`cp ${ctxFile} .`
        
        try {
            if (testSetup) {
                const evalModel = "azure:gpt-4.1-mini_2025-04-14";
                console.log(`Running eval for ${promptyFileBase} with testSetup model (${evalModel})`);
                await $`npm run promptpex promptpex_context.json --  --vars \"evals=true\" --vars \"compliance=false\" --vars \"baselineTests=false\" --vars \"evalModel=${evalModel}\" --vars \"out=${outDirE}/${promptyFileBase}\"`;
            } else {
                const evalModel = "azure:o4-mini_2025-04-16";
                console.log(`Running eval for ${promptyFileBase} with production model (${evalModel})`);
                await $`npm run promptpex promptpex_context.json --  --vars \"evals=true\" --vars \"compliance=false\" --vars \"baselineTests=false\" --vars \"evalModel=${evalModel}\" --vars \"out=${outDirE}/${promptyFileBase}\"`;
            }
        } catch (err) {
            console.error(`Error running evals for ${prompty}:`, err);
        } 
    }  
}