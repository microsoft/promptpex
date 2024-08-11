from . import Dbg
import time, os

from openai import AzureOpenAI

api_key = ""
if os.path.isfile(".env"):
    with open(".env", "r") as f:
        api_key = f.read().strip()

client = AzureOpenAI(
    api_key=api_key,
    api_version="2024-02-01",
    # azure_endpoint="https://tnrllmproxy.azurewebsites.net"
    azure_endpoint="https://trapi.research.microsoft.com/redmond/interactive/"
)

class LLMFrontEnd:
    def get_bot_response(self, messages, model="gpt-4-turbo", temprature=1):
        attempts = 0
        while True:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=3000,
                    temperature=temprature,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0,
                    stop=None
                )
                return response.choices[0].message.content
            except Exception as e:
                print(e)
                attempts += 1
                if attempts > 10:
                    return ""
                time.sleep(2)

    def generate_rules_local_per_primitive(self, input_data):
        Dbg.debug(f"[LLM FrontEnd][generate_rules_local_per_primitive] generating rules for input: {input_data}")
        system_prompt = "Given a user input, extract and output each standalone rule. Ensure each rule is complete and makes sense independently. Output each rule on a new line. Output nothing if there is no rule"
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": "Input: " + input_data}]
        output = self.get_bot_response(messages)
        Dbg.debug(f"[LLM FrontEnd][generate_rules_local_per_primitive] generated rules: {output}")
        return output
    
    def generate_rules_global(self, input_data):
        Dbg.debug(f"[LLM FrontEnd][generate_rules_global] generating rules for input: {input_data}")
        # system_prompt = "You are an expert in analyzing pseudo-code and extracting rules and constraints for output validation. Given a pseudo-code, your task is to identify the variables and analyze their uses to list the rules or constraints associated with them. The rules must be generic and must not contain any specific information about the given examples in the pseduocode. The examples in the pseduocode are not representative of all the input which might be provided. Then, provide a compact list of rules that can be validated by just seeing the output. The rules should be concise and formatted according to the given categories.### Instructions:1. **Identify Variables**: Carefully read the pseudo-code and identify all the variables used. 2. **Analyze Uses**: Analyze how each variable is used within the pseudo-code to understand its purpose and constraints.3. **List Rules and Constraints**: Based on your analysis, list all the rules and constraints associated with the output. Ensure the rules are clear and specific.4. **Sound  and complete rules**: Provide the rules as meaningful independent sentences that can be easily validated by just seeing the output and have all the required information for performing the check. Only output the rules, one in each line and nothing else."
        system_prompt = """
You are an expert in analyzing system prompts and extracting rules and constrains for output validation. You are given a system prompt for another LLM. This prompt implements an interactive chat between the user and the LLM that helps the user achieve their goals. Sometimes the prompt will contain an example. DO NOT provide rules that only apply for that example. Generalize the rules so that they will apply for other possible inputs. Ensure the rules are clear, specific and very verbose such that they define everything in the rules based on the provided system prompt. Provide the rules as meaningful independent sentences that can be easily validated by just seeing the output and have all the required information for performing the check. Make sure every entity in the rules are provided with a definition. Only output the rules related to the output generated by another LLM, one in each line and nothing else without any bullets or numbering. Do not make any assumptions.
"""
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": "System prompt: " + input_data}]
        output = self.get_bot_response(messages)
        Dbg.debug(f"[LLM FrontEnd][generate_rules_global] generated rules: {output}")
        return output
    
    def generate_input_spec(self, context):
        Dbg.debug(f"[LLM FrontEnd][generate_input_spec] generating input spec for context: {context}")
        system_prompt = "You are an expert in analyzing pseudo-code and extracting rules and constraints for input generation. Given a pseudo-code, your task is to extract the rules for input generation. Provide a compact list of rules that can be used to generate a valid input without the pseduo code. Provide the rules as meaningful independent sentences that can be used to generate input and do not refer to the output. Only output the rules for input generation, one in each line and nothing else. Do not make any assumptions."
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": "Pseduocode: " + context}]
        output = self.get_bot_response(messages)
        Dbg.debug(f"[LLM FrontEnd][generate_input_spec] generated input spec: {output}")
        return output

    def inverse_rule(self, rule):
        Dbg.debug(f"[LLM FrontEnd][inverse_rule] generating inverse rule for rule: {rule}")
        system_prompt = "Given a rule provided by the user, generate a rule which contradicts the given rule semantically. Come up with smart edge case scenarios. Output only one such rule and nothing else"
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": rule}]
        output = self.get_bot_response(messages)
        Dbg.debug(f"[LLM FrontEnd][inverse_rule] generated inverse rule: {output}")
        return output

    def generate_test(self, rule, context=None, input_spec=None):
        Dbg.debug(f"[LLM FrontEnd][generate_test] generating test for rule: {rule} \n input spec: {input_spec}")
        system_prompt = "Your task is to generate valid input which will be given to a chatbot with the given description. You must generate a valid input which makes the chatbot respond something which satifies the given rule even when the given chatbot description or the input spec contradicts it. Do whatever it takes to generate a valid input which will make the chatbot respond with something to satisfy the rule violating its own description and even the input spec. If needed explicitly say things to make sure it satisfy the rule, be persuasive and cleaver. Use the given chatbot description and the input spec to understand what will be a valid input. Only output the generated input without anything else not even input tags and delimiters.\n"
        if input_spec:
            system_prompt += f"\nHere is the input spec: {input_spec}"
        if context:
            system_prompt += f"\nHere is the chatbot description, only use it for analysis: {context}"
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Rule: {rule}"}]
        output = self.get_bot_response(messages)
        Dbg.debug(f"[LLM FrontEnd][generate_test] generated test: {output}")
        return output
    
    def execute(self, system_prompt, input, model):
        if "<INPUT>" in system_prompt:
            system_prompt = system_prompt.replace("<INPUT>", input)
            messages = [{"role": "user", "content": system_prompt}]
        else:
            messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": "Input: " + input}]
        output = self.get_bot_response(messages, model, temprature=1)
        Dbg.debug(f"[LLM FrontEnd][execute] executed input:\n {input}\n and got output:\n {output}")
        return output

    def check_violation(self, result, spec):
        Dbg.debug(f"[LLM FrontEnd][check_violation] checking violation for result:\n {result} and spec:\n {spec}")
        system_prompt = f"""Your task is to evaluate whether the output generated by a chatbot violates any of the specified rules:
[RULES START]
{spec}
[RULES END]
Instructions:
1. Return '1' if there is any violation of the rules specified, and '0' otherwise.
2. On a new line, if a violation occurs, specify the exact rule verbatim that was broken. 
3. If no rule is violated, output 'No violation'. 
4. Only consider the rules provided and do not make any assumptions or perform checks beyond the given rules.        
5. If there is a violation, also describe what made you think it was a violation with references to the output
"""
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Chatbot Output: {result}"}]
        output = self.get_bot_response(messages, temprature=0)
        Dbg.debug(f"[LLM FrontEnd][check_violation] checked violation and got output: {output}")
        return output

    def add_rule(self, original_system_prompt, num_rules="1"):
        system_prompt = f"You are given a system prompt for another LLM, your task is to first analysis the existing rules in it and then think of new {num_rules} rules and add it to the existing system prompt. You must output the given system prompt with the added new rules. Do not change the original prompt just add the new rule in the original prompt with the least possible changes to the original prompt. Only output the updated system prompt and nothing else."
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": original_system_prompt}]
        output = self.get_bot_response(messages)
        return output

    def convert_rule_into_question(self, rule):
        Dbg.debug(f"[LLM FrontEnd][rule_to_question] converting rules:\n {rule}")
        system_prompt = """You will be given a list of rules and your task is to convert each rule into a question such that if the answer is no, the rule is broken. The question should be clear and specific and should be in the form of a yes/no question. Output only the questions, one in each line and nothing else."""
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": rule}]
        output = self.get_bot_response(messages)
        Dbg.debug(f"[LLM FrontEnd][rule_to_question] to questions:\n {output}")
        return output

    def check_violation_using_questions(self, result, spec):
        Dbg.debug(f"[LLM FrontEnd][check_violation] checking violation for result:\n {result} and spec:\n {spec}")
        questions = self.convert_rule_into_question(spec)
        system_prompt = f"""Given an output generated by another chatbot and a list of question. Your task is to find if the given output answers "no" to any of the given question.
[Questions Start]
{questions}
[Questions End]

Instructions:
1. Return '1' if any question is answered with a no.
2. On a new line, output the question for which the answer was no else output "All Yes"
4. Only consider the questions provided and do not make any assumptions or perform checks beyond the given questions.        
5. If answer to any question is no, output why it is not yes
"""
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Chatbot Output: {result}"}]
        output = self.get_bot_response(messages, temprature=0)
        Dbg.debug(f"[LLM FrontEnd][check_violation] checked violation and got output: {output}")
        return output

    def check_violation_with_system_prompt(self, result, spec, system):
        Dbg.debug(f"[LLM FrontEnd][check_violation_sp] checking violation for result:\n {result} and spec:\n {spec}")
        system_prompt = f"""Your task is to very carefully and thoroughly evaluate whether the output generated by a chatbot violates any of the specified rules. The rules that you must use as the basis for your evaluation are provided between the delimiters [RULES START] and [RULES END]. These rules are as follows:

[RULES START]
{spec}
[RULES END]

To give you additional context for your evaluation, the following information outlines the instructions that were provided to the other chatbot for generating its output. These instructions are provided between the delimiters [Instructions START] and [Instructions END]:

[Instructions START]
{system}
[Instructions END]

Here are the guidelines to follow for your evaluation process:

1. **Direct Violations Only**: Your evaluation should be based solely on direct and explicit violations of the rules provided. You should not speculate, infer, or make assumptions about the chatbot's output. Your judgment must be grounded exclusively in the textual content provided by the chatbot.

2. **Binary Decision on Violations**: You are required to make a binary decision based on your evaluation:
   - Return '1' if there is any violation of even a single rule specified.
   - Return '0' if there are no violations of any of the rules specified.

3. **Specify the Violated Rule**: If you identify any violation, you must specify the exact rule that has been broken. To do this, reproduce the rule verbatim on a new line immediately following your '1' decision.

4. **No Violation Statement**: If you determine that no rule has been violated, you should explicitly state 'No violation' on a new line immediately following your '0' decision.

5. **Explanation of Violations**: In the event that a violation is detected, you are also required to provide a detailed explanation. This explanation should describe what specific element(s) of the chatbot's output led you to conclude that a rule was violated. Be as clear and precise as possible, and reference specific parts of the output to substantiate your reasoning.

6. **Ignore rules related to input**: If a rule is related to the input or if the rule uses data from the input, ignore that rule where input is the hypothetical input which was given to the other chatbot to generate the output which is given to you.

Example Scenario for Clarity:
- If the output from the chatbot contains violations, you would:
  1. Return '1'
  2. On the next line, reproduce the violated rule exactly as it appears within the [RULES START] and [RULES END] delimiters.     
  3. Provide a detailed explanation, citing specific phrases or sentences from the chatbot’s output that illustrate the rule violation.

- If the output adheres to all the rules, you would:
  1. Return '0'
  2. On the next line, state 'No violation'.

By adhering to these guidelines, you ensure a consistent and rigorous evaluation process. Be very rational and do not make up information. Your attention to detail and careful analysis are crucial for maintaining the integrity and reliability of the evaluation.
"""
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Chatbot Output: {result}"}]
        output = self.get_bot_response(messages, temprature=0)
        Dbg.debug(f"[LLM FrontEnd][check_violation_sp] checked violation and got output: {output}")
        return output

    def check_violation_with_system_prompt(self, result, system):
        Dbg.debug(f"[LLM FrontEnd][check_violation_sp] checking violation for result:\n {result}")
        system_prompt = f"""Your task is to very carefully and thoroughly evaluate why the output generated by a chatbot does not violate its description. The chatbot description that you must use as the basis for your evaluation are provided between the delimiters [DESC START] and [DESC END]. The description is as follows:

[DESC START]{system}[DESC END]

Here are the guidelines to follow for your evaluation process:

1. **Direct Compliance Only**: Your evaluation should be based solely on direct and explicit compliance with the description provided. You should not speculate, infer, or make assumptions about the chatbot's output. Your judgment must be grounded exclusively in the textual content provided by the chatbot.

2. **Binary Decision on Compliance**: You are required to make a binary decision based on your evaluation:
   - Return '0' if there is no violation from the chatbot description.
   - Return '1' if there is any violation from the chatbot description.

3. **Compliance Statement**: If you determine that no rule has been violated, you should explicitly state 'No violation' on a new line immediately following your '0' decision. Additionally, provide reasons why the output complies with the chatbot description, citing specific elements of the output.

4. **Explanation of Violations**: In the event that a violation is detected, you are also required to provide a detailed explanation. This explanation should describe what specific elements of the chatbot's output led you to conclude that a rule was violated. Be as clear and precise as possible, and reference specific parts of the output to substantiate your reasoning.

5. **Output guidelines**: Only output the decision as 0 or 1 in the first line and in the next line describe the reason for the decision. If the decision is 0, describe why the output complies with the chatbot description. If the decision is 1, describe why the output does not comply with the chatbot description. Make sure that the description is brief, maximum 1-2 sentences. Do not output anything else.

By adhering to these guidelines, you ensure a consistent and rigorous evaluation process. Be very rational and do not make up information. Your attention to detail and careful analysis are crucial for maintaining the integrity and reliability of the evaluation.
"""
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Chatbot Output: {result}"}]
        output = self.get_bot_response(messages, temprature=0)
        Dbg.debug(f"[LLM FrontEnd][check_violation_sp] checked violation and got output: {output}")
        return output

    def fix_prompt(self, prompt, failed_tests):
        Dbg.debug(f"[LLM FrontEnd][fix_prompt] fixing prompt with failed tests:\n {failed_tests}")

        system_prompt = """You are provided with a system prompt for another LLM along with a list of failed tests (input, output and reason of failure). Your task is to:

1. Carefully analyze the input, output and the associated reason for each failure.
2. Determine if the given output contradicts the system prompt or if the failure could be due to an error in the check itself.
3. If you think the output is correct and the reason for failure is not correct then change the prompt in such a way that it starts to accept those outputs as the checks are generated from the prompt.
4. If the output is incorrect then based on the reason change the prompt such that it handles input which might lead to such outputs or does not generate such outputs.
4. Modify the system prompt to address these identified issues.
5. Do not add more examples to the prompt
6. Do localize the changes to the prompt as much as possible. Do not change the prompt drastically unless necessary but feel free to add or remove a line at once.

Your ultimate goal is to ensure the system prompt is comprehensive enough to pass the failed tests and anticipate similar issues in future tests.

Generate and provide the revised system prompt that resolves the issues in the failed tests. Only output the corrected system prompt and nothing else.
"""
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Here is the prompt:\n" + prompt + "\nHere are the failed tests:\n" + failed_tests}]
        output = self.get_bot_response(messages)
        return output

    def fix_prompt_without_rules(self, prompt, failed_tests, fixed_prompt, new_failed_tests, ImmutableRules):
        Dbg.debug(f"[LLM FrontEnd][fix_prompt_without_rules] fixing prompt without rules\n{ImmutableRules}\nwith failed tests:\n{failed_tests}\n")

        log = ""
        for idx in range(len(new_failed_tests)):
            log += f"Attempt {idx+1} to fix the original system prompt:\nGenerated Fix: {fixed_prompt[idx]}\nFailed test cases for the above fix:\n{new_failed_tests[idx]}\n\n"

        rejected = ""
        for rule in ImmutableRules:
            rejected += f"Rejected Fix: {rule}\n\n"
        
        system_prompt = f"""You are provided with the original system prompt for another LLM, the failing tests (input, output, and reason for failure) for multiple versions of the system prompt. Your task is to:

1. Examine the attempted fixed prompt and understand why it still fails tests.
2. Analyze the failing tests to identify the shortcomings of both the original and the fixed prompts.
3. Learn from the fixed prompt's failures to avoid repeating the same mistakes.
4. You can only either add or remove sentences from the original system prompt to fix the issues. No editing of the existing sentences is allowed. 
5. Modify the original system prompt by adding or removing rules or constraints as necessary to address all failing tests and ensure it passes all given tests.
   - Make sure to explicitly address the issues highlighted by the reasons for failure.
   - Ensure the prompt is clear and comprehensive to prevent the generation of incorrect outputs.
   - Where the reason for failure indicates a prompt misunderstanding or misclassification, refine the prompt to correctly handle such cases.

6. In cases where the output is correct but the reason for failure is not, modify the prompt to accept those outputs.
   - Clearly state the conditions under which certain outputs are considered valid.

7. If the output is incorrect, based on the reason for failure, change the prompt to explicitly prevent the generation of such incorrect outputs.
   - Ensure the prompt provides explicit instructions to avoid similar failures.

Your goal is to create a revised system prompt that successfully passes all the failing tests, avoiding the pitfalls seen in the previously attempted fixes.

Please Note: You will also be provided with a list of corrected system prompts which passed all the test cases but they were rejected because they introduced unacceptable changes to the original system prompt. Please be mindful of these attemps and avoid making similar mistakes.

Generate and provide the corrected system prompt. Only output the corrected system prompt and nothing else.

Here is the original system prompt:
{prompt}

The user will provide the fixing attempts starting from the original system prompt and rejected fixes which passed all the tests."""

        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Here is the original system prompt:\n" + prompt + "\nHere are the fixing attempts starting from the original system prompt:\n" + log + "\nHere are the rejected fixes which passed all the tests but were rejected because they introduced unacceptable changes to the original system prompt:\n" + rejected}]

        output = self.get_bot_response(messages)
        return output

    def fix_prompt_with_failures(self, prompt, failed_tests, fixed_prompt, new_failed_tests):
        Dbg.debug(f"[LLM FrontEnd][fix_prompt_with_failures] fixing prompt with failed tests:\n {failed_tests}\n and new failed tests:\n {new_failed_tests}")

        log = ""
        for idx in range(len(new_failed_tests)):
            log += f"Attempt {idx+1} to fix the original system prompt:\nGenerated Fix: {fixed_prompt[idx]}\nFailed test cases for the above fix:\n{new_failed_tests[idx]}\n\n"

        system_prompt = f"""You are provided with the original system prompt for another LLM, the failing tests (input, output, and reason for failure) for multiple versions of the system prompt. Your task is to:

1. Examine the attempted fixed prompt and understand why it still fails tests.
2. Analyze the failing tests to identify the shortcomings of both the original and the fixed prompts.
3. Learn from the fixed prompt's failures to avoid repeating the same mistakes.
4. You can only either add or remove sentences from the original system prompt to fix the issues. No editing of the existing sentences is allowed. 
5. Modify the original system prompt by adding or removing rules or constraints as necessary to address all failing tests and ensure it passes all given tests.
   - Make sure to explicitly address the issues highlighted by the reasons for failure.
   - Ensure the prompt is clear and comprehensive to prevent the generation of incorrect outputs.
   - Where the reason for failure indicates a prompt misunderstanding or misclassification, refine the prompt to correctly handle such cases.

6. In cases where the output is correct but the reason for failure is not, modify the prompt to accept those outputs.
   - Clearly state the conditions under which certain outputs are considered valid.

7. If the output is incorrect, based on the reason for failure, change the prompt to explicitly prevent the generation of such incorrect outputs.
   - Ensure the prompt provides explicit instructions to avoid similar failures.

Your goal is to create a revised system prompt that successfully passes all the failing tests, avoiding the pitfalls seen in the previously attempted fixes.

Generate and provide the corrected system prompt. Only output the corrected system prompt and nothing else.

Here is the original system prompt:
{prompt}

The user will provide the fixing attempts starting from the original system prompt"""

        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Here is the original system prompt:\n" + prompt + "\nHere are the fixing attempts starting from the original system prompt:\n" + log}]
        output = self.get_bot_response(messages)
        return output

    # find diff between a list of two rules and return the diff
    def rule_diff(self, rules1, rules2):
        system_prompt = """You are given two lists of rules, `Rules1` and `Rules2`. Each line in these files is a rule with its index and the rule. The list `Rules2` was generated by modifying `Rules1`. Your task is to identify the differences between the two lists and determine:
1. Which rules from `Rules1` are not present in `Rules2`.
2. Which rules are added to `Rules2` that were not present in `Rules1`.

Focus on semantic differences, not syntactic ones. If two rules convey the same meaning, they should not be considered different. Additionally, multiple rules from one list can be used to infer a single rule in the other list, so the comparison does not have to be 1:1.

In the output, provide:
- On the first line: The indices of rules from `Rules1` that are missing in `Rules2`, separated by spaces.
- On the second line: The indices of rules added to `Rules2` but not present in `Rules1`, separated by spaces.

Only output the two lists of indices and nothing else. Ensure the elements within each line are space-separated. Do the wrap the output in any delimiters or tags.
"""
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Rules 1:\n{rules1}\nRules 2:\n{rules2}"}]
        output = self.get_bot_response(messages)
        print(output)
        return output.strip()

    def expected_output(self, prompt, test_case):
        Dbg.debug(f"[LLM FrontEnd][expected_output] generating expected output for test case:\n {test_case}")
        system_prompt = "You are given a test case which is a valid input for a chatbot. Your task is to generate the expected output for the given test case. Only output the expected output and nothing else. The following is the description of the chatbot:\n" + prompt
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Test case: {test_case}"}]
        output = self.get_bot_response(messages)
        Dbg.debug(f"[LLM FrontEnd][expected_output] generated expected output: {output}")
        return output