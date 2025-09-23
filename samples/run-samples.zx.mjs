#!/usr/bin/env zx

import { $ } from "zx";
import path from "path";

// List of 8 .prompty files to substitute for speech-tag.prompty
const promptyFilesAll__ = [
    "samples/speech-tag/speech-tag.prompty",
    "samples/text-to-p/text-to-p.prompty",
    "samples/openai-examples/elements.prompty",
    "samples/big-prompt-lib/art-prompt.prompty",
    "samples/prompt-guide/extract-names.prompty",
    "samples/text-classification/classify-input-text.prompty",
    "samples/big-prompt-lib/sentence-rewrite.prompty",
    "samples/azure-ai-studio/shakespearean-writing-assistant.prompty",
];

const promptyFilesAll___ = [
    //"samples/awesome-chatgpt-prompts/prompt_generator.prompty",
    "samples/speech-tag/speech-tag.prompty",
    // "samples/big-prompt-lib/sentence-rewrite.prompty",
    // "samples/awesome-chatgpt-prompts/recruiter.prompty",

];

const promptyFilesAll__head = [
//-long "samples/awesome-chatgpt-prompts/scientific_data_visualizer.prompty",
"samples/awesome-chatgpt-prompts/startup_idea_generator.prompty", //+ 
"samples/awesome-chatgpt-prompts/tea_taster.prompty",
"samples/awesome-chatgpt-prompts/recruiter.prompty",
"samples/awesome-chatgpt-prompts/yes_or_no_answer.prompty",
"samples/awesome-chatgpt-prompts/virtual_fitness_coach.prompty",
"samples/awesome-chatgpt-prompts/fancy_title_generator.prompty",
"samples/awesome-chatgpt-prompts/restaurant_owner.prompty",
"samples/awesome-chatgpt-prompts/prompt_generator.prompty",
"samples/awesome-chatgpt-prompts/solr_search_engine.prompty",
"samples/10k-chatbot-prompts/sewing_951_7.prompty",
"samples/10k-chatbot-prompts/hearing_impairments_124_7.prompty",
"samples/10k-chatbot-prompts/speaker_identification_595_2.prompty",
"samples/10k-chatbot-prompts/real_time_analytics_609_2.prompty",
];

const promptyFilesAll__all = [
//-long "samples/awesome-chatgpt-prompts/scientific_data_visualizer.prompty",
"samples/awesome-chatgpt-prompts/startup_idea_generator.prompty", //+ 
"samples/awesome-chatgpt-prompts/tea_taster.prompty",
"samples/awesome-chatgpt-prompts/recruiter.prompty",
"samples/awesome-chatgpt-prompts/yes_or_no_answer.prompty",
"samples/awesome-chatgpt-prompts/virtual_fitness_coach.prompty",
"samples/awesome-chatgpt-prompts/fancy_title_generator.prompty",
"samples/awesome-chatgpt-prompts/restaurant_owner.prompty",
"samples/awesome-chatgpt-prompts/prompt_generator.prompty",
"samples/awesome-chatgpt-prompts/solr_search_engine.prompty",
"samples/10k-chatbot-prompts/sewing_951_7.prompty",
"samples/10k-chatbot-prompts/hearing_impairments_124_7.prompty",
"samples/10k-chatbot-prompts/speaker_identification_595_2.prompty",
"samples/10k-chatbot-prompts/real_time_analytics_609_2.prompty",
"samples/10k-chatbot-prompts/housing_market_dynamics_338_1.prompty",
"samples/10k-chatbot-prompts/bayesian_games_29_7.prompty",
"samples/10k-chatbot-prompts/canopy_management_298_8.prompty",
"samples/10k-chatbot-prompts/initial_public_offerings_ipos_70_9.prompty",
"samples/10k-chatbot-prompts/news_broadcasting_693_9.prompty",
"samples/10k-chatbot-prompts/bullet_journaling_145_1.prompty",
    "samples/speech-tag/speech-tag.prompty",
    "samples/text-to-p/text-to-p.prompty",
    "samples/openai-examples/elements.prompty",
    "samples/big-prompt-lib/art-prompt.prompty",
    "samples/prompt-guide/extract-names.prompty",
    "samples/text-classification/classify-input-text.prompty",
    "samples/big-prompt-lib/sentence-rewrite.prompty",
    "samples/azure-ai-studio/shakespearean-writing-assistant.prompty",
"samples/10k-chatbot-prompts/modular_arithmetic_26_4.prompty",
"samples/10k-chatbot-prompts/sleep_hygiene_174_3.prompty",
"samples/10k-chatbot-prompts/supply_chain_risk_management_347_8.prompty",
"samples/10k-chatbot-prompts/supporting_homework_and_study_habits_547_7.prompty",
"samples/10k-chatbot-prompts/decentralized_finance_defi_937_2.prompty",
"samples/10k-chatbot-prompts/fashion_brand_marketing_strategies_889_3.prompty",
"samples/10k-chatbot-prompts/kombucha_brewing_479_10.prompty",
"samples/10k-chatbot-prompts/smart_security_systems_554_2.prompty",
"samples/10k-chatbot-prompts/autism_spectrum_disorder_124_2.prompty",
"samples/10k-chatbot-prompts/sleep_hygiene_practices_163_4.prompty",
"samples/awesome-chatgpt-prompts/virtual_fitness_coach.prompty",
"samples/awesome-chatgpt-prompts/dentist.prompty",
"samples/awesome-chatgpt-prompts/personal_stylist.prompty",
"samples/awesome-chatgpt-prompts/developer_relations_consultant.prompty",
"samples/awesome-chatgpt-prompts/biblical_translator.prompty",
"samples/awesome-chatgpt-prompts/ai_assisted_doctor.prompty",
"samples/awesome-chatgpt-prompts/web_design_consultant.prompty",
"samples/awesome-chatgpt-prompts/public_speaking_coach.prompty",
"samples/awesome-chatgpt-prompts/buddha.prompty",
"samples/awesome-chatgpt-prompts/screenwriter.prompty",
];

const promptyFilesAll____ = [
// original batch of 8
    "samples/speech-tag/speech-tag.prompty",
    "samples/text-to-p/text-to-p.prompty",
    "samples/openai-examples/elements.prompty",
    "samples/big-prompt-lib/art-prompt.prompty",
    "samples/prompt-guide/extract-names.prompty",
    "samples/text-classification/classify-input-text.prompty",
    "samples/big-prompt-lib/sentence-rewrite.prompty",
    "samples/azure-ai-studio/shakespearean-writing-assistant.prompty",
// rest of batch 1
// "samples/10k-chatbot-prompts/housing_market_dynamics_338_1.prompty",
"samples/10k-chatbot-prompts/bayesian_games_29_7.prompty",
"samples/10k-chatbot-prompts/canopy_management_298_8.prompty",
"samples/10k-chatbot-prompts/initial_public_offerings_ipos_70_9.prompty",
"samples/10k-chatbot-prompts/news_broadcasting_693_9.prompty",
"samples/10k-chatbot-prompts/bullet_journaling_145_1.prompty",
// batch 2
"samples/10k-chatbot-prompts/modular_arithmetic_26_4.prompty",
"samples/10k-chatbot-prompts/sleep_hygiene_174_3.prompty",
"samples/10k-chatbot-prompts/supply_chain_risk_management_347_8.prompty",
"samples/10k-chatbot-prompts/supporting_homework_and_study_habits_547_7.prompty",
"samples/10k-chatbot-prompts/decentralized_finance_defi_937_2.prompty",
"samples/10k-chatbot-prompts/fashion_brand_marketing_strategies_889_3.prompty",
"samples/10k-chatbot-prompts/kombucha_brewing_479_10.prompty",
"samples/10k-chatbot-prompts/smart_security_systems_554_2.prompty",
"samples/10k-chatbot-prompts/autism_spectrum_disorder_124_2.prompty",
"samples/10k-chatbot-prompts/sleep_hygiene_practices_163_4.prompty",
"samples/awesome-chatgpt-prompts/virtual_fitness_coach.prompty",
"samples/awesome-chatgpt-prompts/dentist.prompty",
"samples/awesome-chatgpt-prompts/personal_stylist.prompty",
"samples/awesome-chatgpt-prompts/developer_relations_consultant.prompty",
"samples/awesome-chatgpt-prompts/biblical_translator.prompty",
"samples/awesome-chatgpt-prompts/ai_assisted_doctor.prompty",
"samples/awesome-chatgpt-prompts/web_design_consultant.prompty",
"samples/awesome-chatgpt-prompts/public_speaking_coach.prompty",
"samples/awesome-chatgpt-prompts/buddha.prompty",
"samples/awesome-chatgpt-prompts/screenwriter.prompty",
];

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

// Get current date in YYYY-MM-DD format
// const dateStr = new Date().toISOString().slice(0, 10);
const dateStr = "2025-09-23";
const outDir = `evals/test-all-${dateStr}`;

// for (const prompty of promptyFilesAll.slice(0, 1)) {

for (const prompty of promptyFilesAll) {
    const promptyFileBase = path.basename(prompty, path.extname(prompty));
    try {
        await $`npm run promptpex ${prompty} --  --vars \"effort=min\" --vars \"groundtruthModel=azure:gpt-5_2025-08-07\" --vars \"evals=true\" --vars \"modelsUnderTest=ollama:gemma2:9b;ollama:qwen2.5:3b;ollama:gpt-oss;ollama:llama3.2:1b\" --vars \"compliance=true\" --vars \"testValidity=true\" --vars \"baselineTests=true\" --vars \"baselineModel=azure:gpt-5_2025-08-07\" --vars \"evalModelGroundtruth=azure:o4-mini_2025-04-16\" --env .env-gpt41 --vars \"out=${outDir}/${promptyFileBase}\"`;
    } catch (err) {
        console.error(`Error running test for ${prompty}:`, err);
    }
}

// attempt at final config:
//     await $`npm run promptpex ${prompty} --  --vars \"effort=min\" --vars \"groundtruthModel=azure:gpt-5_2025-08-07\" --vars \"evals=true\" --vars \"modelsUnderTest=ollama:qwen3;ollama:gpt-oss;ollama:llama3.2:1b;ollama:llama3.3\" --vars \"compliance=true\" --vars \"testValidity=true\" --vars \"baselineTests=true\" --vars \"baselineModel=azure:gpt-5_2025-08-07\" --vars \"evalModelGroundtruth=azure:o4-mini_2025-04-16\" --env .env-gpt41 --vars \"out=${outDir}/${promptyFileBase}\"`;

// fast local
// await $`npm run promptpex ${prompty} --  --vars \"effort=min\" --vars \"groundtruthModel=ollama:llama3.3\" --vars \"evals=true\" --vars \"modelsUnderTest=ollama:qwen2.5:3b;ollama:llama3.2:1b;ollama:llama3.3\" --vars \"compliance=true\" --vars \"testValidity=true\" --vars \"baselineTests=true\" --vars \"baselineModel=ollama:llama3.3\" --vars \"evalModelGroundtruth=ollama:llama3.3\" --env .env --vars \"out=${outDir}/${promptyFileBase}\"`;

// fast turn-around, no trapi
 //   await $`npm run promptpex ${prompty} --  --vars \"effort=min\" --vars \"groundtruthModel=ollama:llama3.3\" --vars \"evals=true\" --vars \"modelsUnderTest=ollama:qwen2.5:3b;ollama:llama3.2:1b;ollama:llama3.3\" --vars \"compliance=true\" --vars \"testValidity=true\" --vars \"baselineTests=true\" --vars \"baselineModel=ollama:llama3.3\" --vars \"evalModelGroundtruth=ollama:llama3.3\" --env .env --vars \"out=${outDir}/${promptyFileBase}\"`;

//     await $`npm run promptpex ${prompty} --  --vars \"effort=min\" --vars \"groundtruthModel=azure:gpt-4.1_2025-04-14\" --vars \"evals=true\" --vars \"modelsUnderTest=ollama:qwen2.5:3b;ollama:llama3.2:1b;ollama:llama3.3\" --vars \"compliance=true\" --vars \"baselineTests=true\" --vars \"baselineModel=ollama:llama3.3\" --vars \"evalModelGroundtruth=azure:gpt-4.1_2025-04-14\" --env .env --vars \"out=${outDir}/${promptyFileBase}\"`;

//  await $`npm run promptpex ${prompty} --  --vars \"effort=min\" --vars \"groundtruthModel=azure:gpt-4.1_2025-04-14\" --vars \"evals=true\" --vars \"modelsUnderTest=ollama:qwen2.5:3b;ollama:llama3.2:1b;ollama:llama3.3\" --vars \"compliance=false\" --vars \"baselineTests=false\" --vars \"evalModelGroundtruth=azure:gpt-4.1_2025-04-14\" --env .env --vars \"out=${outDir}/${promptyFileBase}\"`;

// uses gp4 models from TRAPI
//     await $`npm run promptpex ${prompty} --  --vars \"effort=min\" --vars \"groundtruthModel=azure:gpt-4o_2024-11-20\" --vars \"evals=true\" --vars \"modelsUnderTest=ollama:qwen2.5:3b;ollama:llama3.2:1b;ollama:llama3.3\" --vars \"compliance=false\" --vars \"baselineTests=false\" --vars \"evalModelGroundtruth=azure:gpt-4o_2024-11-20;ollama:llama3.3\" --env .env.ollama  --vars \"out=${outDir}/${promptyFileBase}\"`;

// await $`npm run promptpex ${prompty} --  --vars \"effort=medium\" --vars \"evals=true\" --vars \"compliance=true\" --vars \"baselineTests=false\"  --vars \"modelsUnderTest=azure:gpt-4o-mini_2024-07-18;ollama:gemma2:9b;ollama:qwen2.5:3b;ollama:llama3.2:1b\" --vars "out=${outDir}/${promptyFileBase}"`;     

//    await $`npm run promptpex ${prompty} -- --vars "splitRules=true" --vars "maxRulesPerTestGeneration=5" --vars "testGenerations=1" --vars "evals=true" --vars"testExpansions=0" --vars "compliance=true" --vars baselineTests=false --vars "modelsUnderTest=azure:gpt-4o-mini_2024-07-18;ollama:gemma2:9b;ollama:qwen2.5:3b;ollama:llama3.2:1b" --vars "out=${outDir}/${promptyFileBase}"`;

//    await $`npm run promptpex ${prompty} -- --vars "splitRules=true" --vars "maxRulesPerTestGeneration=5" --vars "testGenerations=1" --vars "evals=true" --vars "testExpansions=0" --vars "compliance=true" --vars "baselineTests=false" --vars "modelsUnderTest=ollama:llama3.2:1b" --vars "out=${outDir}/${promptyFileBase}"`;