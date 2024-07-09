script({
    title: "refine-test-strategy",
    description: "Refine a strategy for testing LLM prompts systematically",
    model: "gpt-4o",
    maxTokens: 4000,
})

const file1 = await workspace.readText("commit-prompt.md")
const prompt1 = file1.content

const file2 = await workspace.readText("test-strategy.md")
const strategy1 = file2.content

def("EXPROMPT", prompt1)
def("STRATEGY", strategy1)

$`You are an experience software developer with knowledge of
LLMs and writing prompts for LLMs.  You have observed that prompts
are much like software in that they describe tasks, specify inputs and 
outputs, and specify constraints.    As a result, you need to refine
a strategy for testing LLM prompts systematically. A specific  
strategy has been developed for the prompt in EXPROMPT.  The strategy is 
described in the file STRATEGY.  

There are some major problems with the current strategy. IN particular,
many details are missing to make it something that can be acted upon.
For example:
- The strategy does not concrete details about how to actually generate test inputs.
- The strategy does not describe how to extract testable properties from the prompt.
- The strategy does not describe how to generate specific test cases that can be used to test 
the extracted properties.

Refine the strategy by generating python code that when executed will correctly
address the above problems. 

Write out the refined strategy
in a markdown file named refined-strategy.md.
`

