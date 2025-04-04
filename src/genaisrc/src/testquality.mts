import {
    modelOptions,
    parseOKERR,
    parseAllRules,
    parseRulesTests,
} from "./parsers.mts"
import { resolveRule, resolvePromptArgs } from "./resolvers.mts"
import { evaluateTestResult } from "./testresulteval.mts"
import type {
    PromptPexContext,
    PromptPexOptions,
    PromptPexTest,
    PromptPexTestEval,
} from "./types.mts"
import { resolveTestEvalPath } from "./filecache.mts"
import { measure } from "./perf.mts"
import {
    OK_ERR_CHOICES,
    PROMPT_EVAL_OUTPUT_RULE_AGREEMENT,
    PROMPT_EVAL_TEST_VALIDITY,
} from "./constants.mts"
const { generator } = env

export async function evaluateTestsQuality(
    files: PromptPexContext,
    options?: PromptPexOptions & { force?: boolean }
): Promise<string> {
    const { force } = options || {}
    const tests = parseRulesTests(files.tests.content)
    if (!tests?.length) throw new Error("No tests found")

    console.log(`evaluating quality of ${tests.length} tests`)
    const testEvals: PromptPexTestEval[] = []
    for (const test of tests) {
        const testEval = await evaluateTestQuality(files, test, options)
        if (testEval) testEvals.push(testEval)
    }
    return JSON.stringify(testEvals, null, 2)
}

function updateTestEval(res: PromptPexTestEval) {
    res.validity = parseOKERR(res.validityText)
    if (!res.coverageEvalText) {
        delete res.coverage
        delete res.coverageText
    } else res.coverage = parseOKERR(res.coverageEvalText)
}

export async function evaluateTestQuality(
    files: PromptPexContext,
    test: PromptPexTest,
    options?: PromptPexOptions & { force?: boolean }
): Promise<PromptPexTestEval> {
    const { force, evalModel = "eval" } = options || {}
    const { id, promptid, file } = await resolveTestEvalPath(
        files,
        test,
        options
    )
    if (file?.content && !force) {
        const res = parsers.JSON5(file) as PromptPexTestEval
        updateTestEval(res)
        if (res && !res.error && res.coverage && res.validity) return res
    }

    const intent = files.intent.content
    if (!intent) throw new Error("No intent found")
    const inputSpec = files.inputSpec.content
    if (!inputSpec) throw new Error("No input spec found")
    const allRules = parseAllRules(files)
    if (!allRules) throw new Error("No rules found")

    const rule = resolveRule(allRules, test)
    if (!rule && !test.baseline)
        throw new Error(`No rule found for test ${test["ruleid"]}`)

    const { args, testInput } = resolvePromptArgs(files, test)
    if (!args || testInput === undefined)
        return {
            id,
            promptid,
            ...rule,
            input: testInput,
            error: "invalid test input",
        } satisfies PromptPexTestEval

    const moptions = modelOptions(evalModel, options)
    const [resCoverage, resValidity] = await measure(
        "llm.eval.test.quality",
        () =>
            Promise.all([
                generator.runPrompt(
                    (ctx) => {
                        ctx.importTemplate(PROMPT_EVAL_OUTPUT_RULE_AGREEMENT, {
                            intent,
                            rules: allRules
                                .filter((r) => !r.inverse)
                                .map((r) => r.rule)
                                .join("\n"),
                            testInput,
                        })
                    },
                    {
                        ...moptions,
                        //        logprobs: true,
                        label: `${files.name}> evaluate coverage of test ${testInput.slice(0, 42)}...`,
                    }
                ),
                generator.runPrompt(
                    (ctx) => {
                        ctx.importTemplate(PROMPT_EVAL_TEST_VALIDITY, {
                            input_spec: inputSpec,
                            test: testInput,
                        })
                    },
                    {
                        ...moptions,
                        choices: OK_ERR_CHOICES,
                        //        logprobs: true,
                        label: `${files.name}> evaluate validity of test ${testInput.slice(0, 42)}...`,
                    }
                ),
            ])
    )

    const error = [resCoverage.error?.message, resValidity?.error?.message]
        .filter((s) => !!s)
        .join(" ")
    const validity = parseOKERR(resValidity.text)
    const testEval: PromptPexTestEval = {
        id,
        promptid,
        model: resCoverage.model,
        ...rule,
        input: testInput,
        validityText: resValidity.text,
        validity: validity,
        validityUncertainty: resValidity.uncertainty,
        coverageText: resCoverage.text,
    } satisfies PromptPexTestEval

    const coverageEval = await evaluateTestResult(
        files,
        {
            id: "cov-" + testEval.id,
            scenario: test.scenario,
            rule: testEval.rule,
            ruleid: test.ruleid,
            promptid,
            model: testEval.model,
            input: testEval.input,
            output: testEval.coverageText,
        },
        options
    )

    testEval.coverageEvalText = coverageEval.content
    testEval.coverage = parseOKERR(testEval.coverageEvalText)
    if (!isNaN(coverageEval.uncertainty))
        testEval.coverageUncertainty = coverageEval.uncertainty
    testEval.error = error || undefined

    if (file)
        await workspace.writeText(
            file.filename,
            JSON.stringify(testEval, null, 2)
        )

    return testEval
}
