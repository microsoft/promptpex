script({
    files: "eval/result/**"
})

console.log(env.files)
// placeholder for results
const results: {
    input: string
    assessment: "success" | "fail"
    rules: number
    tests: number
    message: string
    output: string
    filename: string
}[] = []

const testResults = []

// env.files should be the list of tests.csv files
const testFiles = env.files.filter(({filename}) => /tests\.csv$/.test(filename))

for(const file of testFiles) {
    const { filename, content} = file
    console.log(filename)
    const dirname = path.dirname(filename)
    const { content: input } = await workspace.readText(path.join(dirname, 'variant-0.txt'))
    if (!input) continue
    try {
    // read original prompt
        // parse rules
        const { content: rulesF } = await workspace.readText(path.join(dirname, 'rules-0.csv'))
        const rules = CSV.parse(rulesF)
        // parse test file
        const tests = CSV.parse(content) as {
            "Rule ID": string
            "Test ID": string
            "Test Input": string
            "Expected Output": string
            "Reasoning": string
        }[]
        if (!tests?.length && !rules?.length)
                throw new Error('no test or rules generated')
            
        // validate test format
        if (tests.length) {
            const test = tests[0]
            if (test["Rule ID"] === undefined || !test["Test ID"] === undefined || !test["Test Input"] == undefined || !test["Expected Output"] === undefined)
                throw new Error('Invalid test format')
            // append test results
            testResults.push(...tests.map(test => ({
                ...test,
                input,
            })))
        }

        // append summary
        results.push({
            assessment: "success",
            message: `${rules.length} rules, ${tests.length} tests`,
            rules: rules.length,
            tests: tests.length,
            input,
            output: tests.map(({ "Test Input": ti})  => ti).join(";'"),
            filename: path.basename(dirname),
        })
    } catch(e) {
        results.push({
            assessment: "fail",
            message: e.message,
            rules: 0,
            tests: 0,
            input,
            output: "",
            filename: path.basename(dirname),
        })
    }
}

// save results as csv
await workspace.writeText('eval/result/tests.csv', CSV.stringify(testResults, { header: true}))
await workspace.writeText('eval/result/summary.csv', CSV.stringify(results, { header: true }))
