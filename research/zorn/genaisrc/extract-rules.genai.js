script({
    title: "extract-rules",
    description: "Identify independent rules about input and output expressed in a system prompt",
    model: "gpt-4o",
    maxTokens: 4000,
})

def("FILE", env.files)

$`FILE contains a system prompt that will be given to an LLM as input.  
The prompt implements an interactive chat between the user and the LLM 
that helps the user achieve their goals.

The prompt refers to additional inputs that are specified by the LLM user
either implicitly or explicitly, such as using a notation such as <INPUT>.

Sometimes the prompt will contain an example.  DO NOT provide rules that
only apply for that example.  Generalize the rules so that they will 
apply for other inputs.

Identify ALL the independent rules about input and output expressed in the 
system prompt in FILE.
For each rule, determine the following properties: 

- Is the rule about input, output, or the prior state of the conversation
- Is the rule conditional or unconditional
    - If the rule is conditional, what is the predicate that determines if the rule is followed
- Priority of following the rule (number from 1 to 5)
- Can the correctness of the rule be verified by running code
- If so, generate python code that will check if the rule was followed, 

Write out each of these rules and their properties in a section of 
a markdown file named rules.md.

Check if any of the rules are in conflict with each other.  If they are
add another section to the markdown file with a list of such conflicts.`

