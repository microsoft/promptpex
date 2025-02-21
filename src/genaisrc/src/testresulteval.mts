import { modelOptions, checkLLMResponse } from "./parsers.mts";
import {
    PromptPexContext,
    PromptPexTestResult,
    PromptPexOptions,
} from "./types.mts";

export async function evaluateTestResult(
    files: PromptPexContext,
    testResult: PromptPexTestResult,
    options: PromptPexOptions
): Promise<string> {
    const { evalModel = "eval" } = options || {};
    const moptions = {
        ...modelOptions(evalModel, options),
    };

    const content = MD.content(files.prompt.content);
    const res = await runPrompt(
        (ctx) => {
            // removes frontmatter
            ctx.importTemplate(
                "src/prompts/check_violation_with_system_prompt.prompty",
                {
                    system: content.replace(/^(system|user):/gm, ""),
                    result: testResult.output,
                }
            );
        },
        {
            ...moptions,
            choices: ["OK", "ERR"],
            //      logprobs: true,
            label: `${files.name}> evaluate test result ${testResult.model} ${testResult.input.slice(0, 42)}...`,
        }
    );
    checkLLMResponse(res);
    const evaluation = res.text;
    return evaluation;
}
