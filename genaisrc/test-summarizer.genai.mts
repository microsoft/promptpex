script({
    files: "eval/result/**"
})

// placeholder for results
const results: {
    input: string
    assessment: "success" | "fail"
    message: string
    output: string
}[] = []

// env.files should be the list of tests.csv files
const tests = env.files.filter(({filename}) => /tests\.csv$/.test(filename))

for(const file of tests) {
    const { filename, content} = file
    console.log(filename)
    const dirname = path.dirname(filename)
    // read original prompt
    const { content: input } = await workspace.readText(path.join(dirname, 'variant-0.txt'))
    try {
        // parse test file
        const tests = CSV.parse(content) as {
            "Rule ID": string
            "Test ID": string
            "Test Input": string
            "Expected Output": string
            "Reasoning": string
        }[]
        if (!tests?.length)
            throw new Error('No tests found')
        const test = tests[0]
        if (!test["Rule ID"] || !test["Test ID"] || !test["Test Input"] || !test["Expected Output"])
            throw new Error('Invalid test format')
        results.push({
            input,
            assessment: "success",
            message: `${tests.length} tests`,
            output: tests.map(({ "Test Input": ti})  => ti).join(";'"),
        })
    } catch(e) {
        results.push({
            input,
            assessment: "fail",
            message: e.message,
            output: "",
        })
    }
}

// save results as csv
await workspace.writeText('eval/result/summary.yaml', YAML.stringify(results))