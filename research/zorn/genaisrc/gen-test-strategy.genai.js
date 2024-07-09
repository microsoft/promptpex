script({
    title: "gen-test-strategy",
    description: "Generate a strategy for testing LLM prompts systematically",
    model: "gpt-4o",
    maxTokens: 4000,
})

def("FILE", env.files)

$`You are an experience software developer with knowledge of
LLMs and writing prompts for LLMs.  You have observed that prompts
are much like software in that they describe tasks, specify inputs and 
outputs, and specify constraints.    As a result, you need to create
a strategy for testing LLM prompts systematically.  The strategy should
include:
- A way to generate test inputs for the prompt
- A way to extract testable properties from the prompt
- A way to generate specific test cases that can be used to test
if the prompt is functioning correctly
- A way to score a given prompt and set of tests on objective metrics such as 
how good the coverage of the tests is, how well the prompt performs on the tests,
and what additional tests might be needed to improve the coverage of the tests.

Use the prompt in FILE as a concrete example to describe your strategy.
Write out the strategy in a markdown file named test-strategy.md.
`

