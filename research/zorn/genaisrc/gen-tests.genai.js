script({
    title: "gen-tests",
    description: "Generate variants of tests for a system prompt.",
    model: "gpt-4o",
    maxTokens: 4000,
})

const user_input = "What SQL query should I use to find employees with salaries above $50,000?"

const file1 = await workspace.readText("classify-prompt.md")
const content1 = file1.content

const file2 = await workspace.readText("rules.md")
const content2 = file2.content

def("FILE1", content1)
def("RULES", content2)
def("USER_INPUT", user_input)

$`FILE1 contains a system prompt that will be given to an LLM as input.  
The prompt implements an interactive chat between the user and the LLM 
that helps the user achieve their goals.

The prompt refers to additional inputs that are specified by the LLM user
using the notation <INPUT>. 

USER_INPUT is one example of user input.

RULES describes the specific rules that the input and ouput
of the prompt must follow, extracted from the prompt in FILE1.

Generate 10 variants of the USER_INPUT that, as a group, test the system's ability to
understand the user's intent and generate a correct response.  Specifically,
modify the input to attempt to determine if each of the rules is being followed.
Write the variants as a list in a markdown file named test-variants.
For each variant, describe which rule it is testing and why it is a good test.

Make sure that your tests cover all of the rules in RULES equally.`

