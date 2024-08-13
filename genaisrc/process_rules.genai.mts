script({
  title: "process-rules",
  description: "Extract insights from a collection of prompt rules.",
  model: "gpt-4-32k",
  maxTokens: 4000,
  files: [
    "ap-results/CONTRIBUTING/rules-0.csv",
    "ap-results/LinuxTerminal/rules-0.csv",
  ],
});

const rules = def("RULE", env.files, { endsWith: ".csv" });

$`The content of ${rules} contains a list of rule identitifer, and rule description using in LLM prompts, formatted as a CSV table.

# Task 1: Category extraction

- Analyze all the rules and extract 10 categories that are most frequently used in the rules.

Work step by step and explain your choices using your inner dialogue.

# Task 2: Categorize extraction

- For each rule, assign a category to it based on the 10 categories extracted in Task 1.

Work step by step and explain your choices using your inner dialogue.

# Task 3: Export results.

- Report the list of categories in a file "categories.csv"
- Report the list of rules and assigned categories in a file "rules-categorized.csv"


This is important.
`