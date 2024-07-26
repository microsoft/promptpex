from . import Dbg
import time

from openai import AzureOpenAI
client = AzureOpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    api_version="2024-02-01",
    azure_endpoint="https://trapi.research.microsoft.com/redmond/interactive/"
)

class LLMFrontEnd:
    def get_bot_response(self, messages, model="gpt-4o", temprature=1):
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
You are an expert in analyzing system prompts and extracting rules and constrains for output validation. You are given a system prompt that will be given to an LLM as input. The prompt implements an interactive chat between the user and the LLM that helps the user achieve their goals. Sometimes the prompt will contain an example.  DO NOT provide rules that only apply for that example. Generalize the rules so that they will apply for other inputs. Ensure the rules are clear, specific and very verbose such that they define everything in the rules based on the provided system prompt. Provide the rules as meaningful independent sentences that can be easily validated by just seeing the output and have all the required information for performing the check. Only output the rules, one in each line and nothing else without any bullets or numbering. Do not make any assumptions.
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
        output = self.get_bot_response(messages, model, temprature=0)
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
        return output[0]

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
        return output[0]

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
        return output[0]

    def check_violation_with_system_prompt(self, result, system):
        Dbg.debug(f"[LLM FrontEnd][check_violation_sp] checking violation for result:\n {result}")
        system_prompt = f"""Your task is to very carefully and thoroughly evaluate whether the output generated by a chatbot violates its description. The chatbot description that you must use as the basis for your evaluation are provided between the delimiters [DESC START] and [DESC END]. The description is as follows:

[DESC START]
{system}
[DESC END]

Here are the guidelines to follow for your evaluation process:

1. **Direct Violations Only**: Your evaluation should be based solely on direct and explicit violations of the description provided. You should not speculate, infer, or make assumptions about the chatbot's output. Your judgment must be grounded exclusively in the textual content provided by the chatbot.

2. **Binary Decision on Violations**: You are required to make a binary decision based on your evaluation:
   - Return '1' if there is any violation from the chatbot description.
   - Return '0' if there are no violations from the chatbot description.

4. **No Violation Statement**: If you determine that no rule has been violated, you should explicitly state 'No violation' on a new line immediately following your '0' decision.

5. **Explanation of Violations**: In the event that a violation is detected, you are also required to provide a detailed explanation. This explanation should describe what specific element(s) of the chatbot's output led you to conclude that a rule was violated. Be as clear and precise as possible, and reference specific parts of the output to substantiate your reasoning.

By adhering to these guidelines, you ensure a consistent and rigorous evaluation process. Be very rational and do not make up information. Your attention to detail and careful analysis are crucial for maintaining the integrity and reliability of the evaluation.
"""
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Chatbot Output: {result}"}]
        output = self.get_bot_response(messages, temprature=0)
        Dbg.debug(f"[LLM FrontEnd][check_violation_sp] checked violation and got output: {output}")
        return output[0]

