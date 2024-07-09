script({
    title: "apply-inputs",
    description: "Apply a prompt to a set of tests",
    model: "gpt-4o",
    maxTokens: 4000,
})

const file1 = await workspace.readText("classify-prompt.md")
const content1 = file1.content

const file2 = await workspace.readText("test-variants.md")
const content2 = file2.content

def("FILE1", content1)
def("FILE2", content2)

$`FILE1 contains a system prompt that will be given to an LLM as input.  
The prompt implements an interactive chat between the user and the LLM 
that helps the user achieve their goals.

The prompt refers to additional inputs that are specified by the LLM user
using the notation <INPUT>. 

FILE2 contains input examples that the user might give to the prompt that 
is defined in FILE1.  For each of the examples in FILE2, 
generate the output for the prompt in FILE1 and write out the pair
of input/output in a markdown file named input-output.md.`

