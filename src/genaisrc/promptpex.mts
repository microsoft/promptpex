const CONCURRENCY = 2;
const RULES_NUM = 0;
const TESTS_NUM = 3;
const TEST_EVALUATION_DIR = "test_evals";
const RULE_EVALUATION_DIR = "rule_evals";

export interface PromptPexOptions {
  /**
   * Do not include Responsible AI safety prompts
   */
  disableSafetyPrompts?: boolean;

  /**
   * Generate temperature for requests
   */
  temperature?: number;
}

/**
 * In memory cache of various files involved with promptpex test generation.
 *
 * - Model Used by PromptPex (MPP) - gpt-4o
 * - Model Under Test (MUT) - Model which we are testing against with specific temperature, etc example: gpt-4o-mini
 */
export interface PromptPexContext {
  /**
   * Prompt folder location
   */
  dir: string;
  /**
   * Prompt name
   */
  name: string;
  /**
   * Prompt Under Test
   */
  prompt: WorkspaceFile;
  /**
 0  * Prompt Under Test Intent (PUTI)
   */
  intent: WorkspaceFile;
  /**
   * Output Rules (OR) - Extracted output constraints of PUT using MPP
   */
  rules: WorkspaceFile;
  /**
   * Inverse output rules (IOR) - Negated OR rules
   */
  inverseRules: WorkspaceFile;
  /**
   * Input specification (IS): Extracted input constraints of PUT using MPP
   */
  inputSpec: WorkspaceFile;

  /**
   * Baseline Tests (BT) - Zero shot test cases generated for PUT with MPP
   */
  baselineTests: WorkspaceFile;

  /**
   * PromptPex Tests (PPT) - Test cases generated for PUT with MPP using IS and OR (test)
   */
  tests: WorkspaceFile;

  /**
   * Test Output (TO) - Result generated for PPT and BT on PUT with each MUT (the template is PUT)
   */
  testOutputs: WorkspaceFile;

  /**
   * Coverage and validate test evals
   */
  testEvals: WorkspaceFile;

  /**
   * Groundedness
   */
  ruleEvals;
}

export interface PromptPexTest {
  /**
   * Index of the rule in the OR+IOR rules. undefined for baseline tests.
   */
  ruleid?: number;
  /**
   * Index of the generated test for the given rule. undefined for baseline tests
   */
  testid?: number;
  /**
   * Generated by the baseline prompt
   */
  baseline?: boolean;
  /**
   * Prompt test input text
   */
  testinput: string;
  /**
   * Expected output generated by the PromptPex Test generator
   */
  expectedoutput?: string;
  /**
   * Explanation of the test generation process
   */
  reasoning?: string;
}

export interface PromptPexTestResult {
  id: string;
  promptid: string;
  ruleid: number;
  rule: string;
  inverse?: boolean;
  baseline?: boolean;
  model: string;
  input: string;
  output: string;
  error?: string;

  compliance?: "ok" | "err";
  complianceText?: string;
}

export interface PromptPexTestEval {
  id: string;
  promptid: string;
  model?: string;
  rule: string;
  inverse?: boolean;
  input: string;
  coverage?: string;
  validity?: "ok" | "err";
  validityText?: string;
  error?: string;
}

export interface PromptPexRuleEval {
  id: string;
  promptid: string;
  ruleid: number;
  rule: string;
  groundedText?: string;
  grounded?: "ok" | "err";
}

export async function loadPromptContext(
  out?: string
): Promise<PromptPexContext[]> {
  const q = host.promiseQueue(CONCURRENCY);
  return q.mapAll(
    env.files.filter((f) => /\.(md|txt|prompty)$/i.test(f.filename)),
    async (f) => await loadPromptFiles(f, out)
  );
}

export async function loadPromptFiles(
  promptFile: WorkspaceFile,
  out?: string
): Promise<PromptPexContext> {
  const basename = path
    .basename(promptFile.filename)
    .slice(0, -path.extname(promptFile.filename).length);
  const dir = path.join(out || path.dirname(promptFile.filename), basename);
  const intent = path.join(dir, "intent.txt");
  const rules = path.join(dir, "rules.txt");
  const inverseRules = path.join(dir, "inverse_rules.txt");
  const inputSpec = path.join(dir, "input_spec.txt");
  const baselineTests = path.join(dir, "baseline_tests.txt");
  const tests = path.join(dir, "tests.csv");
  const testResults = path.join(dir, "test_results.csv");
  const testEvals = path.join(dir, "test_evals.csv");
  const ruleEvals = path.join(dir, "rule_evals.csv");

  return {
    dir,
    name: basename,
    prompt: promptFile,
    testOutputs: await workspace.readText(testResults),
    intent: await workspace.readText(intent),
    inputSpec: await workspace.readText(inputSpec),
    rules: tidyRulesFile(await workspace.readText(rules)),
    ruleEvals: await workspace.readText(ruleEvals),
    inverseRules: tidyRulesFile(await workspace.readText(inverseRules)),
    tests: await workspace.readText(tests),
    testEvals: await workspace.readText(testEvals),
    baselineTests: await workspace.readText(baselineTests),
  } satisfies PromptPexContext;
}

function modelOptions(
  options: PromptPexOptions | undefined
): PromptGeneratorOptions {
  const { disableSafetyPrompts, temperature = 1 } = options || {};
  return {
    model: "large",
    temperature,
    system: disableSafetyPrompts
      ? []
      : ["system.safety_jailbreak", "system.safety_harmful_content"],
  };
}

function isUnassistedResponse(text: string) {
  return /i can't assist with that|i'm sorry/i.test(text);
}

function checkLLMResponse(res: RunPromptResult) {
  if (res.error) throw new Error(res.error.message);
  if (isUnassistedResponse(res.text))
    throw new Error("LLM failed to generate response");
  return res.text;
}

function tidyRules(text: string) {
  if (isUnassistedResponse(text)) return "";
  return text
    .split(/\n/g)
    .map((line) => line.replace(/^(\d+\.|_|-|\*)\s+/i, "")) // unneded numbering
    .filter((s) => !!s)
    .filter((s) => !/^\s*Rules:\s*$/i.test(s))
    .join("\n");
}

function tidyRulesFile(file: WorkspaceFile) {
  if (file?.content) file.content = tidyRules(file.content);
  return file;
}

export async function checkRuleGrounded(
  files: PromptPexContext,
  rule: string,
  options?: PromptPexOptions
) {
  const description = MD.content(files.prompt.content);
  const res = await runPrompt(
    (ctx) => {
      ctx.importTemplate("src/prompts/check_rule_grounded.prompty", {
        rule,
        description,
      });
    },
    {
      ...modelOptions(options),
      //      logprobs: true,
      label: `check rule grounded ${rule.slice(0, 18)}...`,
    }
  );
  checkLLMResponse(res);
  return res.text;
}

export async function generateInputSpec(
  files: PromptPexContext,
  options?: PromptPexOptions
) {
  const context = MD.content(files.prompt.content);
  const res = await runPrompt(
    (ctx) => {
      ctx.importTemplate("src/prompts/input_spec.prompty", {
        context,
      });
    },
    {
      ...modelOptions(options),
      //      logprobs: true,
      label: "generate input spec",
    }
  );
  checkLLMResponse(res);
  return tidyRules(res.text);
}

export async function generateIntent(
  files: PromptPexContext,
  options?: PromptPexOptions
) {
  const context = MD.content(files.prompt.content);
  const res = await runPrompt(
    (ctx) => {
      ctx.importTemplate("src/prompts/extract_intent.prompty", {
        prompt: context,
      });
    },
    {
      ...modelOptions(options),
      //      logprobs: true,
      label: "generate intent",
    }
  );
  checkLLMResponse(res);
  return res.text;
}

export async function generateRules(
  files: PromptPexContext,
  options?: PromptPexOptions & { numRules?: number }
) {
  const { numRules = RULES_NUM } = options || {};
  // generate rules
  const input_data = MD.content(files.prompt.content);
  const res = await runPrompt(
    (ctx) => {
      ctx.importTemplate("src/prompts/rules_global.prompty", {
        num_rules: numRules,
        input_data,
      });
    },
    {
      ...modelOptions(options),
      //      logprobs: true,
      label: "generate rules",
    }
  );
  checkLLMResponse(res);
  return tidyRules(res.text);
}

export async function generateInverseRules(
  files: PromptPexContext,
  options?: PromptPexOptions
) {
  const rule = MD.content(files.rules.content);
  const res = await runPrompt(
    (ctx) => {
      ctx.importTemplate("src/prompts/inverse_rule.prompty", {
        rule,
      });
    },
    {
      ...modelOptions(options),
      //      logprobs: true,
      label: "inverse rules",
    }
  );
  checkLLMResponse(res);
  return tidyRules(res.text);
}

export async function generateBaselineTests(
  files: PromptPexContext,
  options?: PromptPexOptions & { num?: number }
): Promise<string> {
  const tests = parseRulesTests(files.tests.content);
  const { num = tests.length } = options || {};
  const context = MD.content(files.prompt.content);
  const res = await runPrompt(
    (ctx) => {
      ctx.importTemplate("src/prompts/baseline_test.prompty", {
        num,
        prompt: context,
      });
    },
    {
      ...modelOptions(options),
      //      logprobs: true,
      label: `generate baseline tests`,
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
  const { num = TESTS_NUM } = options || {};

  if (!files.rules.content) throw new Error("No rules found");
  if (!files.inputSpec.content) throw new Error("No input spec found");
  const allRules = parseAllRules(files);
  if (!allRules) throw new Error("No rules found");

  const context = MD.content(files.prompt.content);
  let repaired = false;
  const res = await runPrompt(
    (ctx) => {
      ctx.importTemplate("src/prompts/test.prompty", {
        input_spec: files.inputSpec.content,
        context,
        num,
        rule: allRules.map((r, index) => `${index + 1}. ${r.rule}`).join("\n"),
        num_rules: allRules.length,
      });
      ctx.defChatParticipant((p, c) => {
        const last: string = c.at(-1)?.content;
        const csv = parseRulesTests(last);
        if (!csv.length) {
          if (!repaired) {
            console.warn("invalid generated test format, trying to repair");
            repaired = true;
            p.$`The generated tests are not valid CSV. Please try again.`;
          } else {
            console.warn("invalid generated test format, skipping repair");
          }
        }
      });
    },
    {
      ...modelOptions(options),
      //      logprobs: true,
      label: `generate tests`,
    }
  );
  checkLLMResponse(res);
  return res.text;
}

function parseInputs(file: WorkspaceFile) {
  const frontmatter = MD.frontmatter(file.content);
  const inputs = frontmatter["inputs"] || {};
  // under specified inputs, try to find any missing inputs
  // using regex
  if (!Object.keys(inputs).length) {
    file.content.replace(/{{\s*([^}\s]+)\s*}}/g, (_, key) => {
      inputs[key] = { type: "string" };
      return "";
    });
  }

  return inputs;
}

export async function runTests(
  files: PromptPexContext,
  options?: { models?: ModelType[]; force?: boolean; q?: PromiseQueue }
): Promise<string> {
  const { force, models } = options || {};
  const rulesTests = parseRulesTests(files.tests.content);
  const baselineTests = parseBaselineTests(files);
  const tests = [...rulesTests, ...baselineTests];
  if (!tests?.length) throw new Error("No tests found");

  console.log(`executing ${tests.length} tests with ${models.length} models`);
  const testResults: PromptPexTestResult[] = [];
  for (let testi = 0; testi < tests.length; ++testi) {
    const test = tests[testi];
    console.log(
      `run test ${testi + 1}/${tests.length} ${test.testinput.slice(0, 42)}...`
    );
    await evaluateTestQuality(files, test, { force });
    for (const model of models) {
      const testRes = await runTest(files, test, { model, force });
      if (testRes) testResults.push(testRes);
    }
  }

  return CSV.stringify(testResults, { header: true });
}

function toLatexTable(
  data: any[],
  options?: { headers?: string[]; label?: string; caption?: string }
) {
  if (!data?.length) return "no data";
  const { headers = Object.keys(data[0]), label, caption } = options || {};
  const latexTable = `
  \\begin{table}[h!]
  \\centering
  \\begin{tabular}{|${headers.map(() => `c`).join("|")}|}
  \\hline
  ${headers.join(" & ")} \\\\
  \\hline
  ${data
    .map((raw) =>
      headers.map((k) => ("" + raw[k]).replace(/&/g, "\\&")).join(" & ")
    )
    .join(`\\\\\n\\hline\n`)}
  \\end{tabular}
  ${caption ? `\\caption{${caption}}` : ""}
  ${label ? `\\label{${label}}` : ""}
  \\end{table}
  `;
  return latexTable;
}

async function resolveTestId(files: PromptPexContext, test: PromptPexTest) {
  const context = MD.content(files.prompt.content);
  const testid = await parsers.hash(
    context + test.testinput + (test.baseline ? ";baseline" : ""),
    {
      length: 7,
    }
  );
  return testid;
}

async function resolveTestPath(
  files: PromptPexContext,
  test: PromptPexTest,
  options: { model: string }
) {
  const { model } = options;
  const id = await resolveTestId(files, test);
  const promptid = await resolvePromptId(files);
  const dir = path.join(
    files.dir,
    model
      .replace(/^[^:]+:/g, "")
      .replace(/[^a-z0-9\.\-]/g, "_")
      .replace(/_+/g, "_")
      .replace(/^_+|_+$/g, "")
      .toLowerCase()
  );
  const file = await workspace.readText(path.join(dir, `${id}.json`));
  return { id, promptid, file };
}

async function resolveTestEvalPath(
  files: PromptPexContext,
  test: PromptPexTest
) {
  const id = await resolveTestId(files, test);
  const promptid = await resolvePromptId(files);
  const dir = path.join(files.dir, TEST_EVALUATION_DIR);
  const file = await workspace.readText(path.join(dir, `${id}.json`));
  return { id, promptid, file };
}

function resolvePromptArgs(files: PromptPexContext, test: PromptPexTest) {
  const inputs = parseInputs(files.prompt);
  const inputKeys = Object.keys(inputs);
  const expectedOutput = test["expectedoutput"];
  const testInput = test["testinput"];
  const args: Record<string, any> = {};
  if (inputKeys.length === 1) args[inputKeys[0]] = testInput;
  else if (inputKeys.length > 1) {
    // not supported yet
    throw new Error("multiple inputs not supported yet");
    /*
    const testInputArgs =
      parsers.INI(testInput) ||
      parsers.YAML(testInput) ||
      parsers.JSON5(testInput);
    if (!testInputArgs) return undefined;
    for (const key of inputKeys) args[key] = testInputArgs[key];
    */
  }
  return { inputs, args, testInput, expectedOutput };
}

async function resolvePromptId(files: PromptPexContext) {
  const content = MD.content(files.prompt.content);
  return parsers.hash(content, { length: 7 });
}

function parseOKERR(text: string): "err" | "ok" | undefined {
  return /(^|\W)ERR\s*$/.test(text)
    ? "err"
    : /(^|\W)OK\s*$/.test(text)
      ? "ok"
      : undefined;
}

function updateTestResultCompliant(testRes: PromptPexTestResult) {
  testRes.compliance = parseOKERR(testRes.complianceText);
}

export async function runTest(
  files: PromptPexContext,
  test: PromptPexTest,
  options?: { model?: ModelType; force?: boolean }
): Promise<PromptPexTestResult> {
  const { model, force } = options || {};
  const moptions = {
    ...modelOptions(),
  };
  const { id, promptid, file } = await resolveTestPath(files, test, {
    model,
  });
  if (file.content && !force) {
    const res = parsers.JSON5(file);
    if (res && !res.error) {
      updateTestResultCompliant(res);
      res.baseline = test.baseline;
      return res;
    }
  }
  const { inputs, args, testInput } = resolvePromptArgs(files, test);
  const allRules = parseAllRules(files);
  const rule = resolveRule(allRules, test);
  if (!args)
    return {
      id,
      promptid,
      ...rule,
      baseline: test.baseline,
      model: "",
      error: "invalid test input",
      input: testInput,
      output: "invalid test input",
    } satisfies PromptPexTestResult;

  const res = await runPrompt(
    (ctx) => {
      // removes frontmatter
      ctx.importTemplate(files.prompt.filename, args);
      if (!inputs.length) ctx.writeText(testInput);
    },
    {
      ...moptions,
      model,
      label: `run test ${testInput.slice(0, 42)}...`,
    }
  );
  const actualOutput = res.text;
  const testRes: PromptPexTestResult = {
    id,
    promptid,
    ...rule,
    baseline: test.baseline,
    model: res.model,
    error: res.error?.message,
    input: testInput,
    output: actualOutput,
  } satisfies PromptPexTestResult;
  testRes.compliance = undefined;
  testRes.complianceText = await evaluateTestResult(files, testRes, { model });
  updateTestResultCompliant(testRes);

  await workspace.writeText(file.filename, JSON.stringify(testRes, null, 2));
  return testRes;
}

export async function evaluateTestsQuality(
  files: PromptPexContext,
  options?: { force?: boolean }
): Promise<string> {
  const { force } = options || {};
  const tests = parseRulesTests(files.tests.content);
  if (!tests?.length) throw new Error("No tests found");

  console.log(`evaluating quality of ${tests.length} tests`);
  const testEvals: PromptPexTestEval[] = [];
  for (const test of tests) {
    const testEval = await evaluateTestQuality(files, test, { force });
    if (testEval) testEvals.push(testEval);
  }
  return CSV.stringify(testEvals, { header: true });
}

export async function evaluateTestQuality(
  files: PromptPexContext,
  test: PromptPexTest,
  options?: { force?: boolean }
): Promise<PromptPexTestEval> {
  const { force } = options || {};
  const moptions = {
    ...modelOptions(),
  };
  const { id, promptid, file } = await resolveTestEvalPath(files, test);
  if (file.content && !force) {
    const res = parsers.JSON5(file) as PromptPexTestEval;
    if (res && !res.error) return res;
  }

  const intent = files.intent.content;
  if (!intent) throw new Error("No intent found");
  const inputSpec = files.inputSpec.content;
  if (!inputSpec) throw new Error("No input spec found");
  const allRules = parseAllRules(files);
  if (!allRules) throw new Error("No rules found");

  const rule = resolveRule(allRules, test);
  if (!rule && !test.baseline)
    throw new Error(`No rule found for test ${test["ruleid"]}`);

  const { args, testInput } = resolvePromptArgs(files, test);
  if (!args)
    return {
      id,
      promptid,
      ...rule,
      input: testInput,
      error: "invalid test input",
    } satisfies PromptPexTestEval;

  const [resCoverage, resValidity] = await Promise.all([
    runPrompt(
      (ctx) => {
        ctx.importTemplate("src/prompts/evaluate_test_coverage.prompty", {
          intent,
          rules: allRules
            .filter((r) => !r.inverse)
            .map((r) => r.rule)
            .join("\n"),
          testInput,
        });
      },
      {
        ...moptions,
        //        logprobs: true,
        label: `evaluate coverage of test ${testInput.slice(0, 42)}...`,
      }
    ),
    runPrompt(
      (ctx) => {
        ctx.importTemplate(
          "src/prompts/check_violation_with_input_spec.prompty",
          {
            input_spec: inputSpec,
            test: testInput,
          }
        );
      },
      {
        ...moptions,
        choices: ["OK", "ERR"],
        //        logprobs: true,
        label: `evaluate validity of test ${testInput.slice(0, 42)}...`,
      }
    ),
  ]);

  const error = [resCoverage.error?.message, resValidity?.error?.message]
    .filter((s) => !!s)
    .join(" ");
  const testEval = {
    id,
    promptid,
    model: resCoverage.model,
    ...rule,
    input: testInput,
    coverage: resCoverage.text,
    validityText: resValidity.text,
    validity: parseOKERR(resValidity.text),
    error: error || undefined,
  } satisfies PromptPexTestEval;

  await workspace.writeText(file.filename, JSON.stringify(testEval, null, 2));

  return testEval;
}

function parseRules(rules: string) {
  return rules
    ? tidyRules(rules)
        .split(/\r?\n/g)
        .map((l) => l.trim())
        .filter((l) => !!l)
    : [];
}

function parseRulesTests(text: string): PromptPexTest[] {
  if (isUnassistedResponse(text)) return [];
  const content = text?.replace(/\\"/g, '""');
  const rulesTests = content
    ? (CSV.parse(content, { delimiter: ",", repair: true }) as PromptPexTest[])
    : [];
  return rulesTests;
}

function parseTestResults(files: PromptPexContext): PromptPexTestResult[] {
  const rules = parseRules(files.rules.content);
  const res = CSV.parse(files.testOutputs.content, {
    delimiter: ",",
  }) as PromptPexTestResult[];
  res?.forEach((r) => {
    r.inverse = r.ruleid !== null && parseInt(r.ruleid as any) > rules.length;
  });
  return res;
}

function cleanBaselineTests(content: string) {
  const tests = parsers
    .unfence(content, "")
    .split(/\s*===\s*/g)
    .map((l) =>
      l
        .trim()
        .replace(/^(#+\s+)?(test case)( \d+)?:?$/gim, "")
        .trim()
    )
    .filter((l) => !!l);
  return tests;
}

function parseBaselineTests(files: PromptPexContext): PromptPexTest[] {
  const tests = cleanBaselineTests(files.baselineTests.content).map(
    (l) => ({ testinput: l, baseline: true }) satisfies PromptPexTest
  );
  return tests;
}

function parseTestEvals(files: PromptPexContext) {
  return CSV.parse(files.testEvals.content, {
    delimiter: ",",
  }) as PromptPexTestEval[];
}

function parseAllRules(
  files: PromptPexContext
): { rule: string; inverse?: boolean }[] {
  const rules = parseRules(files.rules.content);
  const inverseRules = parseRules(files.inverseRules.content);
  const allRules = [
    ...rules.map((rule) => ({ rule })),
    ...inverseRules.map((rule) => ({ rule, inverse: true })),
  ];
  return allRules;
}

function resolveRule(
  rules: { rule: string; inverse?: boolean }[],
  test: PromptPexTest
) {
  const index = test.ruleid - 1;
  const rule = rules[index];
  return { ruleid: index + 1, ...rule };
}

async function evaluateTestResult(
  files: PromptPexContext,
  testResult: PromptPexTestResult,
  options?: PromptPexOptions & { model?: ModelType }
): Promise<string> {
  const { model } = options || {};
  const moptions = {
    ...modelOptions(options),
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
      label: `evaluate test result ${testResult.model} ${testResult.input.slice(0, 42)}...`,
    }
  );
  if (res.error) console.warn(res.error?.message);

  const evaluation = res.text;
  return evaluation;
}

export async function generateJSONReport(files: PromptPexContext) {
  const prompt = files.prompt.content;
  const inputSpec = files.inputSpec.content;
  const errors: string[] = [];
  const rules = parseRules(files.rules.content);
  const inverseRules = parseRules(files.inverseRules.content);
  const allRules = parseAllRules(files);
  const rulesTests = parseRulesTests(files.tests.content);
  const baseLineTests = parseBaselineTests(files);
  const testEvals = parseTestEvals(files);
  const testResults = parseTestResults(files);
  if (files.tests.content && !rulesTests.length) {
    console.warn(`failed to parse tests in ${files.tests.filename}`);
    errors.push(`failed to parse tests in ${files.tests.filename}`);
  }

  const tests = [...rulesTests, ...baseLineTests].map((test) => {
    const rule = resolveRule(allRules, test);
    if (!rule && !test.baseline)
      errors.push(
        `test '${test.ruleid}' references non-existent rule in ${files.tests.filename}`
      );
    const res: any = {
      ...rule,
      ...test,
    };
    return res;
  });

  return {
    prompt,
    inputSpec,
    rules,
    inverseRules,
    tests,
    testEvals,
    testResults,
    errors: errors.length ? errors : undefined,
  };
}

function addLineNumbers(text: string, start: number) {
  return text
    .split(/\r?\n/gi)
    .map((l, i) => `${start + i}: ${l}`)
    .join("\n");
}

export function computeOverview(
  files: PromptPexContext,
  options?: { percent?: boolean }
) {
  const { percent } = options || {};
  const testResults = parseTestResults(files);
  const testEvals = parseTestEvals(files);
  const testResultsPerModels = testResults.reduce(
    (acc, result) => {
      if (!acc[result.model]) {
        acc[result.model] = [];
      }
      acc[result.model].push(result);
      return acc;
    },
    {} as Record<string, PromptPexTestResult[]>
  );
  const overview = Object.entries(testResultsPerModels).map(
    ([model, results]) => {
      const tests = results.filter((tr) => tr.rule).length;
      const norm = (v: number) =>
        percent ? Math.round((v / tests) * 100) + "%" : v;
      const baseline = results.filter((tr) => !tr.rule).length;
      const bnorm = (v: number) =>
        percent ? Math.round((v / baseline) * 100) + "%" : v;
      return {
        model,
        tests,
        ["tests compliant"]: norm(
          results.filter((tr) => tr.rule && tr.compliance === "ok").length
        ),
        ["baseline compliant"]: bnorm(
          results.filter((tr) => !tr.rule && tr.compliance === "ok").length
        ),
        ["tests positive"]: results.filter((tr) => tr.rule && !tr.inverse)
          .length,
        ["tests positive compliant"]: results.filter(
          (tr) => tr.rule && !tr.inverse && tr.compliance === "ok"
        ).length,
        ["tests negative"]: results.filter((tr) => tr.rule && tr.inverse)
          .length,
        ["tests negative compliant"]: results.filter(
          (tr) => tr.rule && tr.inverse && tr.compliance === "ok"
        ).length,
        baseline,
        ["tests valid"]: results.filter(
          (tr) =>
            tr.rule &&
            testEvals.find((te) => te.id === tr.id)?.validity === "ok"
        ).length,
        ["tests valid compliant"]: results.filter(
          (tr) =>
            tr.rule &&
            tr.compliance === "ok" &&
            testEvals.find((te) => te.id === tr.id)?.validity === "ok"
        ).length,
      };
    }
  );
  return {
    testResults,
    testEvals,
    overview,
  };
}

export async function generateMarkdownReport(files: PromptPexContext) {
  const tests = [
    ...parseRulesTests(files.tests.content),
    ...parseBaselineTests(files),
  ];
  const rules = parseRules(files.rules.content);
  const inverseRules = parseRules(files.inverseRules.content);
  const testResults = parseTestResults(files);
  const ts = testResults.length;
  const oks = testResults.filter((t) => t.compliance === "ok").length;
  const errs = testResults.filter((t) => t.compliance === "err").length;
  const rp = (n: number, t: number) =>
    `${n}/${t} (${Math.floor((n / t) * 100)}%)`;

  const res: string[] = [
    `## ${files.name} ([json](./${files.dir}/report.json))`,
    ``,
    `- ${rules?.length ?? 0} rules`,
    `- ${inverseRules?.length ?? 0} inverse rules`,
    `- ${tests.length ?? 0} tests, ${tests.filter((t) => t.baseline).length} baseline tests`,
    testResults?.length
      ? `- ${testResults?.length ?? 0} test results, ${rp(oks, ts)} oks, ${rp(errs, ts)} errs`
      : undefined,
    ``,
  ].filter((l) => l !== undefined);

  res.push("### Overview", "");
  res.push(`<details><summary>Glossary</summary>
    
- Prompt Under Test (PUT) - like Program Under Test; the prompt
- Model Under Test (MUT) - Model which we are testing against with specific temperature, etc example: gpt-4o-mini
- Model Used by PromptPex (MPP) - gpt-4o

- Input Specification (IS) - Extracting input constraints of PUT using MPP
- Output Rules (OR) - Extracting output constraints of PUT using MPP
- Output Rules Groundedness (ORG) - Checks if OR is grounded in PUT using MPP

- Prompt Under Test Intent (PUTI) - Extracting the exact task from PUT using MMP

- PromptPex Tests (PPT) - Test cases generated for PUT with MPP using IS and OR
- Baseline Tests (BT) - Zero shot test cases generated for PUT with MPP

- Test Input Compliance (TIC) - Checking if PPT and BT meets the constraints in IS using MPP
- Test Coverage (TC) - Result generated for PPT and BT on PUTI + OR with MPP

- Test Output (TO) - Result generated for PPT and BT on PUT with each MUT
- Test Output Compliance (TOC) - Checking if TO meets the constraints in PUT using MPP

</details>
`);
  const { overview } = computeOverview(files, { percent: true });
  await workspace.writeText(
    path.join(files.dir, "overview.csv"),
    CSV.stringify(overview, { header: true })
  );
  await workspace.writeText(
    path.join(files.dir, "overview.tex"),
    toLatexTable(overview, { caption: "Test results overview" })
  );
  res.push(
    "",
    `### [${path.basename(files.testOutputs.filename)}](./${path.basename(files.testOutputs.filename)})`,
    "",
    // Three more same columns with the same data but only for valid tests
    CSV.markdownify(overview)
  );

  const fence = "`````";
  const appendFile = (file: WorkspaceFile) => {
    const ext = path.extname(file.filename).slice(1);
    const headers =
      file === files.testOutputs
        ? ["model", "rule", "input", "output", "compliance"]
        : file === files.tests
          ? ["testinput", "expectedoutput", "reasoning"]
          : file === files.baselineTests
            ? ["testinput"]
            : file === files.testEvals
              ? ["rule", "model", "input", "coverage", "validity"]
              : undefined;
    const lang =
      {
        prompty: "md",
      }[ext] || ext;
    res.push(
      "",
      `### [${path.basename(file.filename)}](./${path.basename(file.filename)})`,
      ""
    );

    if (lang === "csv")
      res.push(CSV.markdownify(CSV.parse(file.content), { headers }));
    else {
      let content = file.content;
      if (file === files.rules) content = addLineNumbers(content, 1);
      else if (file === files.inverseRules)
        content = addLineNumbers(content, 1 + inverseRules.length);
      res.push(`${fence}${lang}`, content || "", `${fence}`, ``);
    }
  };

  for (const file of Object.values(files))
    if (typeof file === "object" && file.filename && file.content)
      appendFile(file as WorkspaceFile);

  return res.filter((l) => l !== undefined).join("\n");
}

export async function generateReports(files: PromptPexContext) {
  const jsonreport = await generateJSONReport(files);
  await workspace.writeText(
    path.join(files.dir, "report.json"),
    JSON.stringify(jsonreport, null, 2)
  );

  const mdreport = await generateMarkdownReport(files);
  const fn = path.join(files.dir, "README.md");
  await workspace.writeText(fn, mdreport);
  return fn;
}

export async function generate(
  files: PromptPexContext,
  options?: PromptPexOptions & {
    force?: boolean;
    forceBaselineTests?: boolean;
    forceIntent?: boolean;
    forceInputSpec?: boolean;
    forceTests?: boolean;
    forceTestEvals?: boolean;
    forceExecuteTests?: boolean;
    models?: ModelType[];
  }
) {
  const {
    force = false,
    forceBaselineTests = false,
    forceTestEvals = false,
    forceIntent = false,
    forceInputSpec = false,
    forceTests = false,
    forceExecuteTests = false,
    models,
  } = options || {};

  console.log(`generating tests for ${files.name} at ${files.dir}`);

  // generate intent
  if (!files.intent.content || force || forceIntent) {
    files.intent.content = await generateIntent(files, options);
    await workspace.writeText(files.intent.filename, files.intent.content);
  }

  // generate input spec
  if (!files.inputSpec.content || force || forceInputSpec) {
    files.inputSpec.content = await generateInputSpec(files, options);
    await workspace.writeText(
      files.inputSpec.filename,
      files.inputSpec.content
    );
    files.tests.content = undefined;
    files.testOutputs.content = undefined;
  }

  // generate rules
  if (!files.rules.content || force) {
    files.rules.content = await generateRules(files, options);
    await workspace.writeText(files.rules.filename, files.rules.content);
    files.inverseRules.content = undefined;
    files.tests.content = undefined;
    files.testOutputs.content = undefined;
    files.testEvals.content = undefined;
  }

  // generate inverse rules
  if (!files.inverseRules.content || force) {
    files.inverseRules.content = await generateInverseRules(files, options);
    await workspace.writeText(
      files.inverseRules.filename,
      files.inverseRules.content
    );
    files.tests.content = undefined;
    files.testOutputs.content = undefined;
    files.testEvals.content = undefined;
  }

  // generate tests
  if (!files.tests.content || force || forceTests) {
    files.tests.content = await generateTests(files, options);
    await workspace.writeText(files.tests.filename, files.tests.content);
    files.testEvals.content = undefined;
    files.testOutputs.content = undefined;
  }

  // generate baseline tests
  if (!files.baselineTests.content || force || forceBaselineTests) {
    files.baselineTests.content = await generateBaselineTests(files, options);
    await workspace.writeText(
      files.baselineTests.filename,
      files.baselineTests.content
    );
    files.testEvals.content = undefined;
    files.testOutputs.content = undefined;
  }

  await generateReports(files);

  // test exhaustiveness
  if (!files.testEvals.content || force || forceTestEvals) {
    files.testEvals.content = await evaluateTestsQuality(files, {
      ...(options || {}),
      ...{
        force: force || forceTestEvals,
      },
    });
    await workspace.writeText(
      files.testEvals.filename,
      files.testEvals.content
    );
  }

  await generateReports(files);

  if (models?.length) {
    files.testOutputs.content = await runTests(files, {
      models,
      force: force || forceExecuteTests,
    });
    await workspace.writeText(
      files.testOutputs.filename,
      files.testOutputs.content
    );
    await workspace.writeText(
      files.testOutputs.filename + ".tex",
      toLatexTable(CSV.parse(files.testOutputs.content), {
        caption: "Test results and compliance",
      })
    );
  }

  // final report
  const report = await generateReports(files);
  console.log(`  report: ${report}`);

  return files;
}
