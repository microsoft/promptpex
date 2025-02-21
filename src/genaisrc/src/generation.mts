import {
    PROMPT_GENERATE_INPUT_SPEC,
    PROMPT_GENERATE_INTENT,
    PROMPT_GENERATE_RULES,
    PROMPT_GENERATE_INVERSE_RULES,
    PROMPT_GENERATE_BASELINE_TESTS,
    PROMPT_GENERATE_TESTS,
    RULES_NUM,
    TESTS_NUM,
} from "./constants.mts";
import { outputWorkflowDiagram, outputPrompty } from "./output.mts";
import {
    modelOptions,
    checkLLMResponse,
    tidyRules,
    isUnassistedResponse,
    cleanBaselineTests,
} from "./parsers.mts";
import { parseRulesTests, parseAllRules } from "./parsers.mts";
import { PromptPexContext, PromptPexOptions } from "./types.mts";

export async function generateInputSpec(
    files: PromptPexContext,
    options?: PromptPexOptions
) {
    const instructions = options?.instructions?.inputSpec || "";
    outputWorkflowDiagram(
        `PUT(["Prompt Under Test (PUT)"])
IS["Input Specification (IS)"]
PUT --> IS`,
        options
    );

    const { rulesModel = "rules" } = options || {};
    const context = MD.content(files.prompt.content);
    const pn = PROMPT_GENERATE_INPUT_SPEC;
    await outputPrompty(pn, options);
    const res = await runPrompt(
        (ctx) => {
            ctx.importTemplate(pn, {
                context,
                instructions,
            });
        },
        {
            ...modelOptions(rulesModel, options),
            //      logprobs: true,
            label: `${files.name}> generate input spec`,
        }
    );
    checkLLMResponse(res);
    return tidyRules(res.text);
}

export async function generateIntent(
    files: PromptPexContext,
    options?: PromptPexOptions
) {
    const { rulesModel = "rules" } = options || {};
    const context = MD.content(files.prompt.content);
    const instructions = options?.instructions?.intent || "";
    const pn = PROMPT_GENERATE_INTENT;
    await outputPrompty(pn, options);
    const res = await runPrompt(
        (ctx) => {
            ctx.importTemplate(pn, {
                prompt: context,
                instructions,
            });
        },
        {
            ...modelOptions(rulesModel, options),
            //      logprobs: true,
            label: `${files.name}> generate intent`,
        }
    );
    checkLLMResponse(res);
    return res.text;
}

export async function generateOutputRules(
    files: PromptPexContext,
    options?: PromptPexOptions & { numRules?: number }
) {
    const { numRules = RULES_NUM, rulesModel = "rules" } = options || {};
    const instructions = options?.instructions?.outputRules || "";

    outputWorkflowDiagram(
        `PUT(["Prompt Under Test (PUT)"])
OR["Output Rules (OR)"]

PUT --> OR        
`,
        options
    );

    // generate rules
    const input_data = MD.content(files.prompt.content);
    const pn = PROMPT_GENERATE_RULES;
    await outputPrompty(pn, options);
    const res = await runPrompt(
        (ctx) => {
            ctx.importTemplate(pn, {
                num_rules: numRules,
                input_data,
                instructions,
            });
        },
        {
            ...modelOptions(rulesModel, options),
            //      logprobs: true,
            label: `${files.name}> generate rules`,
        }
    );
    checkLLMResponse(res);
    const rules = tidyRules(res.text);
    return rules;
}

export async function generateInverseOutputRules(
    files: PromptPexContext,
    options?: PromptPexOptions
) {
    const { rulesModel = "rules" } = options || {};
    const instructions = options?.instructions?.inverseOutputRules || "";
    outputWorkflowDiagram(
        `OR["Output Rules (OR)"]
IOR["Inverse Output Rules (IOR)"]
OR --> IOR    
`,
        options
    );

    const rule = MD.content(files.rules.content);
    const pn = PROMPT_GENERATE_INVERSE_RULES;
    await outputPrompty(pn, options);
    const res = await runPrompt(
        (ctx) => {
            ctx.importTemplate(pn, {
                rule,
                instructions,
            });
        },
        {
            ...modelOptions(rulesModel, options),
            //      logprobs: true,
            label: `${files.name}> inverse rules`,
        }
    );
    checkLLMResponse(res);
    return tidyRules(res.text);
}

export async function generateBaselineTests(
    files: PromptPexContext,
    options?: PromptPexOptions & { num?: number }
): Promise<string> {
    const { rulesModel = "rules" } = options || {};
    const tests = parseRulesTests(files.tests.content);
    const { num = tests.length } = options || {};
    const context = MD.content(files.prompt.content);
    const pn = PROMPT_GENERATE_BASELINE_TESTS;
    await outputPrompty(pn, options);
    const res = await runPrompt(
        (ctx) => {
            ctx.importTemplate(pn, {
                num,
                prompt: context,
            });
        },
        {
            ...modelOptions(rulesModel, options),
            //      logprobs: true,
            label: `${files.name}> generate baseline tests`,
        }
    );

    if (isUnassistedResponse(res.text)) return "";
    checkLLMResponse(res);
    return cleanBaselineTests(res.text).join("\n===\n");
}

export async function generateTests(
    files: PromptPexContext,
    options?: PromptPexOptions & { num?: number }
) {
    const { num = TESTS_NUM, rulesModel = "rules" } = options || {};

    if (!files.rules.content) throw new Error("No rules found");
    if (!files.inputSpec.content) throw new Error("No input spec found");
    const allRules = parseAllRules(files);
    if (!allRules) throw new Error("No rules found");

    outputWorkflowDiagram(
        `PUT(["Prompt Under Test (PUT)"])
IS["Input Specification (IS)"]
OR["Output Rules (OR)"]
IOR["Inverse Output Rules (IOR)"]
PPT["PromptPex Tests (PPT)"]

PUT --> IS

PUT --> OR
OR --> IOR

PUT --> PPT
IS --> PPT
OR --> PPT
IOR --> PPT        
`,
        options
    );

    const context = MD.content(files.prompt.content);
    let repaired = false;
    const pn = PROMPT_GENERATE_TESTS;
    await outputPrompty(pn, options);
    const res = await runPrompt(
        (ctx) => {
            ctx.importTemplate(pn, {
                input_spec: files.inputSpec.content,
                context,
                num,
                rule: allRules
                    .map((r, index) => `${index + 1}. ${r.rule}`)
                    .join("\n"),
                num_rules: allRules.length,
            });
            ctx.defChatParticipant((p, c) => {
                const last: string = c.at(-1)?.content;
                const csv = parseRulesTests(last);
                if (!csv.length) {
                    if (!repaired) {
                        console.warn(
                            "Invalid generated test format or no test generated, trying to repair"
                        );
                        repaired = true;
                        p.$`The generated tests are not valid CSV. Please fix formatting issues and try again.`;
                    } else {
                        env.output.warn(
                            "Invalid generated test format, skipping repair."
                        );
                        env.output.fence(last, "txt");
                    }
                }
            });
        },
        {
            ...modelOptions(rulesModel, options),
            //      logprobs: true,
            label: `${files.name}> generate tests`,
        }
    );
    checkLLMResponse(res);
    return res.text;
}
