---
title: Saving and Restoring PromptPex Sessions
sidebar:
    order: 21.7
---

The state of a PromptPex session can be saved and restored. This allows a user to generate tests in one session and review them, expand them, or evaluate them in another session.  When the `out` parameter is set specifying the ouput directory, the session state is automatically saved to that directory in the file `promptpex_context.json`. The session state includes the prompt under test, the test collection, and the evaluation results.

To restore a session, set the `loadContext` parameter to `true` and specify the path to the context file you want loaded with the parameter `loadContextFile`.

Note that session state does not include the PromptPex options, so whatever options you specify when restoring the session, such as `modelsUnderTest` will override that options from the saved session.  This allows the same tests to be evaluated using different models or options.

An example sequence of commands to save and restore a session might be the following.  We first generate tests and save the session state to the directory `test1`:

```bash
promptpex --prompt "Rate summary from 1 to 10" --effort "min" --out ./test1
```
We then expand the tests using the `testExpansion` option and save the session state to the directory `test-expand`, which now has the expanded tests:
```bash
promptpex --prompt "dummy" --out "./test-expand" --vars "testExpansions=1" --vars "evals=false"  --vars "loadContext=true" --vars "loadContextFile=evals/test1/promptpex_context.json"
```

Note that we specify a dummy prompt here because the prompt has already been saved in the context file.

Finally, we can evaluate the expanded tests using a different model, such as `gpt-4o`, and save the session state to the directory `test-eval`:
```bash
promptpex --prompt "dummy" --out "./test-eval" --vars "evals=true" --vars "out=test-eval" --vars "loadContext=true" --vars "loadContextFile=evals/test-expand/promptpex_context.json" --modelsUnderTest "gpt-4o"
```