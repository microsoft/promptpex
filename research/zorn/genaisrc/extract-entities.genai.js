script({
    title: "extract-entites",
    description: "Identify entity definitions and uses in a prompt",
    model: "gpt-4o",
    maxTokens: 4000,
})

def("FILE", env.files)

$`You are an expert software developer who has experience writing 
both code and LLM prompts. FILE contains a system prompt that will be given to an LLM as input.  
The prompt implements an interactive chat between the user and the LLM 
that helps the user achieve their goals.

The prompt refers to additional inputs that are specified by the LLM user
either implicitly or explicitly, such as using a notation such as <INPUT>.

Sometimes the prompt will contain an example.  Use these examples to 
better understand how the prompt relates to the input and output.

Your task is to identify All the named entities in the prompt.  These 
entities can either be defined in the prompt or refer to external entities.

For each named entity in FILE: determine the following properties: 

- What is the entity name?
- Is it a symbolic name (like a program variable x, y, z) or is it a
natural language term?
- Is the entity defined in the prompt or is it external?
    - If it is defined in the prompt, quote the exact text that defines
    the entity.
    - If is external, describe where and how the entity is defined externally.
- Is the entity referred to in the text by name?
    - For EVERY reference to the entity, quote the exact text that references it.

Write out each of these entities and their properties in a section of 
a markdown file named entities.md.

If there are entities used and not defined, list them.
If there are references where the entity being referred to is ambiguous, 
for EVERY such reference, quote the exact text of the ambiguous reference`

