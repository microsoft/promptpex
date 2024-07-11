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

You have three tasks.

Task 1: Your task is to identify All the named entities in the prompt.  These 
entities can either be defined in the prompt or refer to external entities.

Include in your list of entities:
    - The LLM itself, which is often referred to as "you" in the prompt. 
    - The user input that will be given to the prompt from the user.
    - The user who gives the prompt the input.
    - The output that the prompt will produce.
    - Any examples provided in the prompt.

Ignore the following entities:
    - External entities that refer to existing infrastructure such as programs, libraries,
    systems, etc.

For EVERY named entity in FILE: determine the following properties: 

- What is the entity name?
- Create unique meaningful symbolic name, like a variable name, for this entity.
- Is it a symbolic name (like a program variable x, y, z) or is it a
natural language term?
- Is the entity defined in the prompt or is it external?
    - If it is defined in the prompt, quote the exact text that defines
    the entity.
    - If is external, describe where and how the entity is defined externally.
- Is the entity referred to in the text by name?
    - For EVERY reference to the entity, quote the exact text that references it.
- What are the specificed properties of the entities.  
    - Make a list of EVERY properties and for each property,  quote the exact text that references it.

Be careful to distinguish text that describe what the entity is and
what properties the entity has.

Task 2: 
If there are references where the entity being referred to is ambiguous,
create a list with the following information:
- What the ambiguity is
- For every references where the entity being referred to is ambiguous,
quote the exact text of the ambiguous reference and explain why it is ambiguous.

Task 3:
Translate the original prompt into a new prompt where all the entities being referred to
are now being referred to by the unique meaningful symbolic name you created in 
Task 1.

Perform each of these tasks and put the output into a separate section 
of the document entities.md
`

