import { PROMPT_CHECK_RULE_GROUNDED } from "./constants.mts";
import { outputPrompty } from "./output.mts";
import {
    modelOptions,
    checkLLMResponse,
    parseOKERR,
    parseRules,
} from "./parsers.mts";
import { resolveRuleEvalPath } from "./filecache.mts";
import type {
    PromptPexContext,
    PromptPexOptions,
    PromptPexRuleEval,
} from "./types.mts";

export async function evaluateRuleGrounded(
    files: PromptPexContext,
    ruleid: number,
    rule: string,
    options?: PromptPexOptions
): Promise<PromptPexRuleEval> {
    const { evalModel = "eval" } = options || {};
    const { id, promptid, file } = await resolveRuleEvalPath(
        files,
        rule,
        options
    );
    if (file?.content) {
        const res = parsers.JSON5(file) as PromptPexRuleEval;
        if (res && !res.error) {
            res.ruleid = ruleid;
            return res;
        }
    }

    const description = MD.content(files.prompt.content);
    const res = await runPrompt(
        (ctx) => {
            ctx.importTemplate(PROMPT_CHECK_RULE_GROUNDED, {
                rule,
                description,
            });
        },
        {
            ...modelOptions(evalModel, options),
            choices: ["OK", "ERR"],
            label: `${files.name}> eval rule grounded ${rule.slice(0, 18)}...`,
        }
    );
    checkLLMResponse(res);

    const ruleEval: PromptPexRuleEval = {
        id,
        promptid,
        ruleid,
        rule,
        groundedText: res.text,
        grounded: parseOKERR(res.text),
        error: res.error?.message,
    };
    if (file)
        await workspace.writeText(
            file.filename,
            JSON.stringify(ruleEval, null, 2)
        );
    return ruleEval;
}

export async function evaluateRulesGrounded(
    files: PromptPexContext,
    options?: PromptPexOptions
) {
    const rules = parseRules(files.rules.content);
    if (!rules) throw new Error("No rules found");
    await outputPrompty(PROMPT_CHECK_RULE_GROUNDED, options);
    const res: PromptPexRuleEval[] = [];
    for (let i = 0; i < rules.length; ++i) {
        const ev = await evaluateRuleGrounded(files, i + 1, rules[i], options);
        res.push(ev);
    }

    files.ruleEvals.content = CSV.stringify(res, { header: true });
    await workspace.writeText(
        files.ruleEvals.filename,
        files.ruleEvals.content
    );
    return res;
}
