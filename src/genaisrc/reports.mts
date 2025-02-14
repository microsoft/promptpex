import {
    computeOverview,
    parseBaselineTests,
    parseRuleEvals,
    parseRules,
    parseRulesTests,
    parseTestResults,
} from "./promptpex.mts";
import type { PromptPexContext } from "./types.mts";

export async function generateMarkdownReport(files: PromptPexContext) {
    const tests = [
        ...parseRulesTests(files.tests.content),
        ...parseBaselineTests(files),
    ];
    const rules = parseRules(files.rules.content);
    const ruleEvals = parseRuleEvals(files);
    const groundedRuleEvals = ruleEvals.filter((r) => r.grounded === "ok");
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
        `- ${rules?.length ?? 0} rules, ${rp(groundedRuleEvals.length, ruleEvals.length)} grounded`,
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
- Model Used by PromptPex (MPP) - gpt-4o/llama3.3

- Intent (I) - 
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
                      : file === files.ruleEvals
                        ? ["ruleid", "rule", "grounded"]
                        : file === files.baselineTestEvals
                          ? ["input", "validity"]
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

function addLineNumbers(text: string, start: number) {
    return text
        .split(/\r?\n/gi)
        .map((l, i) => `${start + i}: ${l}`)
        .join("\n");
}
