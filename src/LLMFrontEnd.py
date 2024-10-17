import re
from re import I
from . import Dbg
import time, os
from dotenv import load_dotenv
from openai import AzureOpenAI, OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import frontmatter
from jinja2 import Template

load_dotenv()

PROMPTPEX_MODEL = os.getenv("PROMPTPEX_TEST_MODEL", "gpt-4-turbo")
PROMPTPEX_TEST_MODEL = os.getenv("PROMPTPEX_TEST_MODEL", "gpt-35-turbo")
PROMPTPEX_GITHUB_MODEL = os.getenv("PROMPTPEX_GITHUB_MODEL", "gpt-4o")
PROMPTPEX_GITHUB_TEST_MODEL = os.getenv("PROMPTPEX_GITHUB_TEST_MODEL", "gpt-35-turbo")
PROMPTPEX_LOCAL_BASE_URL = os.getenv("PROMPTPEX_LOCAL_BASE_URL", "http://localhost:8502/v1")
PROMPTPEX_LOCAL_API_KEY = os.getenv("PROMPTPEX_LOCAL_API_KEY", "none")  

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_VERSION = os.getenv("AZURE_OPENAI_VERSION", "2024-02-01")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_MARKETPLACE = False
if AZURE_OPENAI_ENDPOINT is not None:
    PROMPTPEX_MODEL_PROVIDER = "Azure OpenAI " + AZURE_OPENAI_ENDPOINT
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    if (AZURE_OPENAI_API_KEY is not None):
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=AZURE_OPENAI_VERSION,
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
    else:
        token_provider = get_bearer_token_provider(
           DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
        )
        client = AzureOpenAI(
            azure_ad_token_provider=token_provider,
            api_version=AZURE_OPENAI_VERSION,
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
elif GITHUB_TOKEN is not None:
    PROMPTPEX_MODEL_PROVIDER = "GitHub Marketplace Models"
    client = OpenAI(
        api_key=GITHUB_TOKEN,
        base_url="https://models.inference.ai.azure.com"
    )
    PROMPTPEX_MODEL = PROMPTPEX_GITHUB_MODEL
    PROMPTPEX_TEST_MODEL = PROMPTPEX_GITHUB_TEST_MODEL
    GITHUB_MARKETPLACE = True
else:
    print("LLM configuration missing")
    exit(1)

local_client = OpenAI(
    base_url = PROMPTPEX_LOCAL_BASE_URL,
    api_key= PROMPTPEX_LOCAL_API_KEY
)

def render_prompt(filename, **kwargs):
    # load the prompt file
    filepath = f"src/prompts/{filename}.prompty"
    prompt = frontmatter.load(filepath)
    # grabs the content
    content = prompt.content
    # remove system:, user: messages
    content = re.sub(r'^(system:|user:).*$', '', content, flags=re.MULTILINE)
    # apply jinja2
    template = Template(content)
    # Apply jinja2 to the prompt content
    rendered_prompt = template.render(kwargs)
    # return rendered prompt
    return rendered_prompt

class LLMFrontEnd:
    def get_bot_response(self, messages, model=PROMPTPEX_MODEL, temprature=1):
        attempts = 0
        while True:
            try:
                if GITHUB_MARKETPLACE or model.startswith('gpt'):
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
                else:
                    response = local_client.chat.completions.create(
                        model=model,
                        messages=messages,
                        max_tokens=500,
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
                if attempts > 100:
                    return ""
                time.sleep(0.5)

    def generate_rules_local_per_primitive(self, input_data):
        Dbg.debug(f"[LLM FrontEnd][generate_rules_local_per_primitive] generating rules for input: {input_data}")
        system_prompt = render_prompt("rules_local_per_primitive")
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": "Input: " + input_data}]
        output = self.get_bot_response(messages)
        Dbg.debug(f"[LLM FrontEnd][generate_rules_local_per_primitive] generated rules: {output}")
        return output

    def generate_rules_global(self, input_data, num_rules=0):
        Dbg.debug(f"[LLM FrontEnd][generate_rules_global] generating rules for input: {input_data}")
        system_prompt = render_prompt("rules_global", num_rules = 0, )
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": "System prompt: " + input_data}]
        output = self.get_bot_response(messages)
        Dbg.debug(f"[LLM FrontEnd][generate_rules_global] generated rules: {output}")
        return output

    def generate_generic_rules_global(self, input_data, num_rules=0, allow=["output"], deny=["input"], instructions="", assistant = ""):
        Dbg.debug(f"[LLM FrontEnd][generate_rules_global] generating rules for input: {input_data}")
        allow_str = ", ".join(allow)
        deny_str = ", ".join(deny)
        system_prompt = render_prompt("generic_rules_global", allow_str = allow_str, deny_str = deny_str, num_rules = num_rules, instructions = instructions)
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": "System prompt: " + input_data}]

        if (assistant != ""):
            messages.append({"role": "assistant", "content": assistant})

        output = self.get_bot_response(messages)
        Dbg.debug(f"[LLM FrontEnd][generate_rules_global] generated rules: {output}")
        return output

    def generate_input_spec(self, context):
        Dbg.debug(f"[LLM FrontEnd][generate_input_spec] generating input spec for context: {context}")
        system_prompt = render_prompt("input_spec")
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": "Chatbot description: " + context}]
        output = self.get_bot_response(messages)
        Dbg.debug(f"[LLM FrontEnd][generate_input_spec] generated input spec: {output}")
        if output is None:
            return ""
        output = output.replace("\n\n", "\n").strip()
        return output

    def inverse_rule(self, rule):
        Dbg.debug(f"[LLM FrontEnd][inverse_rule] generating inverse rule for rule: {rule}")
        system_prompt = "Given a list of rules provided by the user, generate another list of rules which contradicts the given rules semantically. Generate one inversed rule for each given rule in the given list. Come up with smart edge case scenarios. Please ensure that each generated rule is only in a single line. Output only the generated rules and nothing else"
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": rule}]
        output = self.get_bot_response(messages)
        Dbg.debug(f"[LLM FrontEnd][inverse_rule] generated inverse rule: {output}")
        if output is None:
            return ""
        output = output.replace("\n\n", "\n").strip()
        return output

    def generate_baseline_test(self, prompt, num=1):
        Dbg.debug(f"[LLM FrontEnd][generate_baseline_test] generating test")
        system_prompt = f"""
You are tasked with developing multiple test cases for an software, use the given description to infer its functional and input specification. You must create at max {num} distinct and diverse test cases. These test cases must be designed to validate whether the software's outputs correctly adhere to description. These tests must be well defined as per the description.

Start with first understanding what is a input for the software. Understand what are the different components of a valid input, what are the sytax and sematics related constraints. A good test must always be a valid input meeting the requirements mentioned in the given description.

Use the given description of the software to generate the test cases.

Guidelines for generating test cases:
- Use the description to understand the valid input formats, components of the input and scenarios for the software.
- If the test case have multiple components, try to use all the components in the test case and tag them with their name, like, component name: value
- Each test case must be crafted to rigorously assess whether the software's output meets the stipulated behavior based on the provided software description.
- Use valid and realistic input scenarios that fully comply with the given description.
- Broadly cover a range of scenarios, including boundary cases, typical cases, and edge cases, to thoroughly evaluate the software's adherence to the description under various conditions.
- Never generate similar or redundant test cases.
- Test cases must never have the output or the expected output, it must only contain the input.

Each test case should adhere to principles of good software testing practices, emphasizing coverage, specificity and independence. Critically assess potential weaknesses in the software's handling of inputs and focus on creating diverse test cases that effectively challenge the software's capabilities.

Separate each test case with a new line with "===" as the delimiter. It will help in identifying each test case separately. Do not wrap the output in any additional text like the index of test case or formatting like triple backticks or quotes. Only output the test cases directly separated by "===".
"""

        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Description of the software: {prompt}"}]
        output = self.get_bot_response(messages)
        Dbg.debug(f"[LLM FrontEnd][generate_baseline_test] generated test: {output}")
        if output is None:
            return ""
        output = output.split("===")
        return output

    def generate_test(self, rule, context=None, input_spec=None, num=1):
        Dbg.debug(f"[LLM FrontEnd][generate_test] generating test for rule: {rule} \n input spec: {input_spec}")
        system_prompt = f"""
You are tasked with developing multiple test cases for an software, given its functional and input specification and a list of rules as input. For each rule, you must create {num} test cases. These test cases must be designed to validate whether the software's outputs correctly adhere to a particular rule. These tests must be well defined based on the input specifications.

Start with first understanding what is a input for the software using the given input specification. Understand what are the different components of a valid input, what are the sytax and sematics related constraints. A good test must always be a valid input meeting the requirements from the given input specification.

Use the following input specification to understand valid inputs and generate good tests: {input_spec}

Use the following functional specification of the software to generate the test cases: {context}

Guidelines for generating test cases:
- Analyze the input specifications to understand the valid input formats, components of the input and scenarios for the software.
- If the test case have multiple components, try to use all the components in the test case and tag them with their name, like, component name: value
- Develop {num} test cases for each rule provided in the list.
- Each test case must be crafted to rigorously assess whether the software's output meets the stipulated rule based on the inputs that conform to the provided input specification.
- Use valid and realistic input scenarios that fully comply with the input specifications and are relevant to the rule being tested.
- Specify clearly in each test case the input given to the software and the expected output or behavior that demonstrates adherence to the rule.
- Broadly cover a range of scenarios, including boundary cases, typical cases, and edge cases, to thoroughly evaluate the software's adherence to the rule under various conditions.
- Never generate similar or redundant test cases

Each test case should adhere to principles of good software testing practices, emphasizing coverage, specificity and independence. Critically assess potential weaknesses in the software's handling of inputs based on the rule and focus on creating diverse test cases that effectively challenge the software's capabilities.

Format your response in a structured CSV format as follows:
- "Rule ID": Identifier for the rule being tested.
- "Test ID": Sequential identifier for each test case under a rule.
- "Test Input": Detailed input provided to the software.
- "Expected Output": Output or behavior expected from the software to affirm rule adherence.
- "Reasoning": Brief explanation of why this test case is relevant and contributes to robust testing of the rule. List the input specification that this test case does not follow.

Example CSV layout:
Rule ID, Test ID, Test Input, Expected Output, Reasoning
1, 1, "input based on rule 1 scenario 1", "expected outcome demonstrating rule adherence", "Explains the relevance and effectiveness of the test and how it follows the input specification"
1, 2, "input based on rule 1 scenario 2, examples", "expected response confirming rule", "Illustrates how inputs challenge the software and ensure compliance and how is a valid test case based on input specification"

Only output the test cases in the specified CSV format and nothing else. Please make sure that the CSV generated is well formed, only have five columns and each value in a these columns must only have commas inside quoted value else they will be counted as a new column. Do not wrap the output in any additional text or formatting like triple backticks or quotes.
"""

        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"List of Rules: {rule}"}]
        output = self.get_bot_response(messages)
        Dbg.debug(f"[LLM FrontEnd][generate_test] generated test: {output}")
        if output is None:
            return ""
        output = output.replace("\n\n", "\n").strip()
        return output

    def execute(self, system_prompt, input, model, temp):
        if "<INPUT>" in system_prompt:
            system_prompt = system_prompt.replace("<INPUT>", input)
            messages = [{"role": "user", "content": system_prompt}]
        else:
            messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": "Input: " + input}]
        output = self.get_bot_response(messages, model, temprature=temp)
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

    def check_violation_with_system_prompt_1(self, result, spec, system):
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

    def check_violation_batch_to_single(self, result, system, num_tests):
        result = result.split("__<<DELIMITIER>>__")
        system_prompt = f"""Your task is to very carefully and thoroughly evaluate the given output generated by a chatbot to find out if it does not comply with its description. Since the input is not given to you, only check for the rules which can be checked without knowing the input. The chatbot description that you must use as the basis for your evaluation are provided between the delimiters [DESC START] and [DESC END]. The description is as follows:

[DESC START]{system}[DESC END]

Here are the guidelines to follow for your evaluation process:

1. **Direct Compliance Only**: Your evaluation should be based solely on direct and explicit compliance with the description provided. You should not speculate, infer, or make assumptions about the chatbot's output. Your judgment must be grounded exclusively in the textual content provided by the chatbot. Do not check for anything which requires knowing the input.

2. **Binary Decision on Compliance**: You are required to make a binary decision based on your evaluation:
   - Return '0' if chatbot output complies with the description (except checks which requires knowing the input).
   - Return '1' if there is any non compliance with the chatbot description (except checks which requires knowing the input).

3. **Compliance Statement**: If you determine that the output comply with the description (except rules which requires knowing the input), you should explicitly state 'No violation' on a new line immediately following your '0' decision. Additionally, provide reasons why the output complies with the chatbot description, citing specific elements of the output.

4. **Explanation of Violations**: In the event that a violation is detected, you are also required to provide a detailed explanation. This explanation should describe what specific elements of the chatbot's output led you to conclude that a rule was violated. Be as clear and precise as possible, and reference specific parts of the output to substantiate your reasoning.

5. **Checking compliance and never correctness**: You are not required to evaluate the functional correctness of the chatbot's output as you are not given the input which generated those outputs. Your evaluation should focus solely on whether the output complies with the chatbot description, if it requires knowing the input, ignore that part of the description.

6. **Output guidelines**: For the chatbot's output given to you, only output the decision as 0 or 1 in the first line and in the next line describe the reason for the decision. If the decision is 0, describe why the output complies with the chatbot description. If the decision is 1, describe why the output does not comply with the chatbot description. Make sure that the description is brief, maximum 1-2 sentences. Do not output anything else.

Example outputs:
1
Mention the reason for violation.

0
No violation.

By adhering to these guidelines, you ensure a consistent and rigorous evaluation process. Be very rational and do not make up information. Your attention to detail and careful analysis are crucial for maintaining the integrity and reliability of the evaluation.
"""
        outputs = []
        for res in result:
            messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Chatbot output: {res}"}]
            output = self.get_bot_response(messages, temprature=0)
            Dbg.debug(f"[LLM FrontEnd][check_violation_sp_single] checked violation and got output: {output}")
            outputs.append(output)

        return "\n".join(outputs)

    def check_violation_with_system_prompt_batch(self, result, system, num_tests, batch_mode):
        if not batch_mode:
            return self.check_violation_batch_to_single(result, system, num_tests)

        result = result.replace("__<<DELIMITIER>>__", "\n\n")

        Dbg.debug(f"[LLM FrontEnd][check_violation_sp_batch] checking violation for result:\n {result}")
        system_prompt = f"""Your task is to very carefully and thoroughly evaluate the given list of {num_tests} outputs generated by a chatbot to find out if they do not comply its description. Since the input is not given to you, only check for the rules which can be checked without knowing the input. The chatbot description that you must use as the basis for your evaluation are provided between the delimiters [DESC START] and [DESC END]. The description is as follows:

[DESC START]{system}[DESC END]

Here are the guidelines to follow for your evaluation process:

1. **Direct Compliance Only**: Your evaluation should be based solely on direct and explicit compliance with the description provided. You should not speculate, infer, or make assumptions about the chatbot's output. Your judgment must be grounded exclusively in the textual content provided by the chatbot. Do not check for anything which requires knowing the input.

2. **Binary Decision on Compliance**: You are required to make a binary decision based on your evaluation:
   - Return '0' if chatbot output complies with the description (except checks which requires knowing the input).
   - Return '1' if there is any non compliance with the chatbot description (except checks which requires knowing the input).

3. **Compliance Statement**: If you determine that the output comply with the description (except rules which requires knowing the input), you should explicitly state 'No violation' on a new line immediately following your '0' decision. Additionally, provide reasons why the output complies with the chatbot description, citing specific elements of the output.

4. **Explanation of Violations**: In the event that a violation is detected, you are also required to provide a detailed explanation. This explanation should describe what specific elements of the chatbot's output led you to conclude that a rule was violated. Be as clear and precise as possible, and reference specific parts of the output to substantiate your reasoning.

5. **Checking compliance and never correctness**: You are not required to evaluate the functional correctness of the chatbot's output as you are not given the input which generated those outputs. Your evaluation should focus solely on whether the output complies with the chatbot description, if it requires knowing the input, ignore that part of the description.

6. **Output guidelines**: For each chatbot's output given to you, only output the decision as 0 or 1 in the first line and in the next line describe the reason for the decision. If the decision is 0, describe why the output complies with the chatbot description. If the decision is 1, describe why the output does not comply with the chatbot description. You must do it for all {num_tests} outputs from the given list of chatbot outputs. Your output must have decision and reason {num_tests} times, individually for each output from the given list. Make sure that the description is brief, maximum 1-2 sentences. Do not output anything else.

Example output for two outputs:
1
Mention the reason for violation.

0
No violation.

You will have to generate such output for all the {num_tests} outputs given to you.

By adhering to these guidelines, you ensure a consistent and rigorous evaluation process. Be very rational and do not make up information. Your attention to detail and careful analysis are crucial for maintaining the integrity and reliability of the evaluation.
Please ensure you generate the output for all the {num_tests} outputs given to you else redo the task until you generate the output for all the outputs.
"""
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Number of chatbot outputs: {num_tests}\nList Start:\n{result}\nList End"}]
        output = self.get_bot_response(messages, temprature=0)
        Dbg.debug(f"[LLM FrontEnd][check_violation_sp_batch] checked violation and got output: {output}")
        return output

    def get_fix_suggestions(self, prompt, failed_tests):
        Dbg.debug(f"[LLM FrontEnd][fix_prompt] fixing prompt with failed tests:\n {failed_tests}")

        system_prompt = """You are given a description of a task given to a person and instances of where this person made errors (question, answer and reason of incorrectness highlighting the error). This person is very smart so the reason of these failure must be in the instructions or the description of the task provided to this person. Your goal is to suggest improvements for the description of task / instructions so that the person can correctly answer all the questions. Your suggestion will be used to improve the task description for correcting the incorrect answers.

Follow these instructions for suggesting the fix:
1. Analyze the question, answer and the associated reason for each incorrect answer.
2. Since the person is very smart, you must connect the reason of failure to a rule or a constraint in the task description as the description is the only source of information for the person.
3. If the task description does not have a rule or a constraint related to the reason of incorrect, add a new rule or constraint to the task description. For example, if the reason of failure was the use of comma as delimiter in the answer but the task description did not specify the delimiter, then add a rule specifying the delimiter.
4. If the task description has a rule or a constraint already which is related to the incorrect answer, then analyze if falls in one of the following categories:
    - The rule or constraint is not clear or have ambiguity. In this case, make the rule or constraint more clear and specific.
    - The rule or constraint is not specific enough to handle this particular test (corner case). In this case, make the rule or constraint more specific while keeping it general enough to handle other cases.
    - The rule or constraint is not comprehensive enough to handle a particular test. In this case, make the rule or constraint more comprehensive.
    - The rule or constraint assumes context which is not provided in the task description. In this case, make the rule or constraint more general by adding the context to the task description.
    - The task description can correctly handle the test but the answer is still incorrect. In this case, increase the specificity or emphasis of the rule or constraint in the description hoping it will fix the failed test cases.

The incorrect answers can only be corrected by modifying the task description. Please feel to try and suggest other techniques to fix the incorrect answers. Analyze each incorrect answer and reason step by step for suggesting a fix trying to fix all the incorrect answers not just one.

The fix you must follow these guidelines:
1. Only add or remove a single sentence at a time to the task description to fix the incorrect answers.
2. Do not change the existing sentences in the task description unless necessary.
3. Do not add more examples to the task description especially to fix a particular incorrect answer.
4. Do not mention any specific question or answer in the task description as the task description must be general enough to handle all the questions.
5. Always address the question or test which will be given to the person as input.

Output the reasoning and analysis used in coming up with the suggestion, also output how did you follow the instruction and which of the above categories were involved in the incorrect answer and then output the suggestion without any delimiter like ```. Never output the fixed description, only output the suggestion.
"""
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Here is the task:\n" + prompt + "\nHere are the incorrect answers:\n" + failed_tests}]
        output = self.get_bot_response(messages)
        if output is None:
            return ""
        return output

    def fix_prompt(self, prompt, failed_tests):
        Dbg.debug(f"[LLM FrontEnd][fix_prompt] fixing prompt with failed tests:\n {failed_tests}")

        system_prompt = """You are given a description of a task given to a person and instances of where this person made errors (question, answer and reason of incorrectness highlighting the error). This person is very smart so the reason of these failure must be in the instructions or the description of the task provided to this person. Your goal is to improve the description of task / instructions so that the person can correctly answer all the questions.

Follow these instructions for generating the fix:
1. Analyze the question, answer and the associated reason for each incorrect answer.
2. Since the person is very smart, you must connect the reason of failure to a rule or a constraint in the task description as the description is the only source of information for the person.
3. If the task description does not have a rule or a constraint related to the reason of incorrect, add a new rule or constraint to the task description. For example, if the reason of failure was the use of comma as delimiter in the answer but the task description did not specify the delimiter, then add a rule specifying the delimiter.
4. If the task description has a rule or a constraint already which is related to the incorrect answer, then analyze if falls in one of the following categories:
    - The rule or constraint is not clear or have ambiguity. In this case, make the rule or constraint more clear and specific.
    - The rule or constraint is not specific enough to handle this particular test (corner case). In this case, make the rule or constraint more specific while keeping it general enough to handle other cases.
    - The rule or constraint is not comprehensive enough to handle a particular test. In this case, make the rule or constraint more comprehensive.
    - The rule or constraint assumes context which is not provided in the task description. In this case, make the rule or constraint more general by adding the context to the task description.
    - The task description can correctly handle the test but the answer is still incorrect. In this case, increase the specificity or emphasis of the rule or constraint in the description hoping it will fix the failed test cases.

The incorrect answers can only be corrected by modifying the task description. Please feel to try other techniques to fix the incorrect answers. Analyze each incorrect answer and reason step by step and generate a fix trying to fix all the incorrect answers not just one.

While generating the fix you must follow these guidelines:
1. Only add or remove a single sentence at a time to the task description to fix the incorrect answers.
2. Do not change the existing sentences in the task description unless necessary.
3. Do not add more examples to the task description especially to fix a particular incorrect answer.
4. Do not mention any specific question or answer in the task description as the task description must be general enough to handle all the questions.
5. Always address the question or test which will be given to the person as input.

First output the reasoning and analysis used in generating the fix, also output how did you follow the instruction and which of the above categories were involved in the incorrect answer and then output the fixed description. The fixed description must start with a heading "Fixed:" and then the fixed description without any other delimiter like ```.

Do not output anything after the fixed description.
"""
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Here is the task:\n" + prompt + "\nHere are the incorrect answers:\n" + failed_tests}]
        output = self.get_bot_response(messages)
        if output is None:
            return ""
        output = output.split("**Fixed Description:**")[-1].strip()
        output = output.split("Fixed Description:")[-1].strip()
        output = output.split("Fixed Description")[-1].strip()
        output = output.split("**Fixed:**")[-1].strip()
        output = output.split("**Fixed**")[-1].strip()
        output = output.split("Fixed:")[-1].strip()
        output = output.split("Fixed")[-1].strip()
        return output

    def get_fix_suggestions_without_rules(self, prompt, failed_tests, fixed_prompt, new_failed_tests, ImmutableRules):
        Dbg.debug(f"[LLM FrontEnd][fix_prompt_without_rules] fixing prompt without rules\n{ImmutableRules}\nwith failed tests:\n{failed_tests}\n")

        log = ""
        for idx in range(len(new_failed_tests)):
            log += f"Attempt {idx+1} to fix the original system prompt:\nGenerated Fix: {fixed_prompt[idx]}\nFailed test cases for the above fix:\n{new_failed_tests[idx]}\n\n"

        rejected = ""
        for rule in ImmutableRules:
            rejected += f"Rejected Fix: {rule}\n\n"

        system_prompt = """You are given a description of another chatbot with bugs along with a list of failed tests (input, output and reason of failure) highlighting those bugs. Your task is to fix these failed tests by modifying the given description. You are also provided with a list of modified descriptions where you earlier attempted to fix the failed tests but it did not work. Please avoid making similar mistakes in your new attempts and learn from the previous mistakes. Adapt your fixes to the failed tests and the chatbot description to ensure that the chatbot passes all the tests.

Follow these instructions for generating the fix:
1. Analyze the input, output and the associated reason for each failure.
2. You must connect the reason of failure to a rule or a constraint in the chatbot description.
3. If the chatbot description does not have a rule or a constraint related to the reason of failure, add a new rule or constraint to the chatbot description.
4. If the chatbot description has a rule or a constraint already which is related to the reason of failure, then analyze if falls in one of the following categories:
    - The rule or constraint is not clear or have ambiguity. In this case, make the rule or constraint more clear and specific.
    - The rule or constraint is not specific enough to handle this particular test (corner case). In this case, make the rule or constraint more specific while keeping it general enough to handle other cases.
    - The rule or constraint is not comprehensive enough to handle a particular test. In this case, make the rule or constraint more comprehensive.
    - The rule or constraint assumes context which is not provided in the chatbot description. In this case, make the rule or constraint more general by adding the context to the chatbot description.
    - The chatbot description can correctly handle the test but the output is incorrect. In this case, increase the specificity or emphasis of the rule or constraint in the description hoping it will fix the failed test cases.

The generated fix must follow these guidelines:
1. Only add or remove a single sentence at a time to the chatbot description to fix the failed tests.
2. Do not change the existing sentences in the chatbot description unless necessary.
3. Do not add more examples to the chatbot description especially to fix the failed tests.

Only output the fixed system prompt and nothing else.
"""

        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Here is the original system prompt:\n" + prompt + "\nHere are the fixing attempts starting from the original system prompt:\n" + log + "\nHere are the rejected fixes which passed all the tests but were rejected because they introduced unacceptable changes to the original system prompt:\n" + rejected}]

        output = self.get_bot_response(messages)
        return output

    def fix_prompt_without_rules(self, prompt, failed_tests, fixed_prompt, new_failed_tests, ImmutableRules):
        breakpoint()
        Dbg.debug(f"[LLM FrontEnd][fix_prompt_without_rules] fixing prompt without rules\n{ImmutableRules}\nwith failed tests:\n{failed_tests}\n")

        log = ""
        for idx in range(len(new_failed_tests)):
            log += f"Attempt {idx+1} to fix the original system prompt:\nGenerated Fix: {fixed_prompt[idx]}\nFailed test cases for the above fix:\n{new_failed_tests[idx]}\n\n"

        rejected = ""
        for rule in ImmutableRules:
            rejected += f"Rejected Fix: {rule}\n\n"

        system_prompt = """You are given a description of another chatbot with bugs along with a list of failed tests (input, output and reason of failure) highlighting those bugs. Your task is to fix these failed tests by modifying the given description. You are also provided with a list of modified descriptions where you earlier attempted to fix the failed tests but it did not work. Please avoid making similar mistakes in your new attempts and learn from the previous mistakes. Adapt your fixes to the failed tests and the chatbot description to ensure that the chatbot passes all the tests.

Follow these instructions for generating the fix:
1. Analyze the input, output and the associated reason for each failure.
2. You must connect the reason of failure to a rule or a constraint in the chatbot description.
3. If the chatbot description does not have a rule or a constraint related to the reason of failure, add a new rule or constraint to the chatbot description.
4. If the chatbot description has a rule or a constraint already which is related to the reason of failure, then analyze if falls in one of the following categories:
    - The rule or constraint is not clear or have ambiguity. In this case, make the rule or constraint more clear and specific.
    - The rule or constraint is not specific enough to handle this particular test (corner case). In this case, make the rule or constraint more specific while keeping it general enough to handle other cases.
    - The rule or constraint is not comprehensive enough to handle a particular test. In this case, make the rule or constraint more comprehensive.
    - The rule or constraint assumes context which is not provided in the chatbot description. In this case, make the rule or constraint more general by adding the context to the chatbot description.
    - The chatbot description can correctly handle the test but the output is incorrect. In this case, increase the specificity or emphasis of the rule or constraint in the description hoping it will fix the failed test cases.

The generated fix must follow these guidelines:
1. Only add or remove a single sentence at a time to the chatbot description to fix the failed tests.
2. Do not change the existing sentences in the chatbot description unless necessary.
3. Do not add more examples to the chatbot description especially to fix the failed tests.

Only output the fixed system prompt and nothing else.
"""

        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Here is the original system prompt:\n" + prompt + "\nHere are the fixing attempts starting from the original system prompt:\n" + log + "\nHere are the rejected fixes which passed all the tests but were rejected because they introduced unacceptable changes to the original system prompt:\n" + rejected}]

        output = self.get_bot_response(messages)
        return output

    def get_fix_suggestions_with_failures(self, prompt, failed_tests, fixed_prompt, new_failed_tests):
        Dbg.debug(f"[LLM FrontEnd][fix_prompt_with_failures] fixing prompt\n {prompt}\n with failed tests:\n {failed_tests}\n and new failed tests:\n {new_failed_tests}\n with fixed prompt:\n {fixed_prompt}")

        log = ""
        for idx in range(len(new_failed_tests)):
            log += f"Attempt {idx+1} to fix the original system prompt:\nGenerated Fix: {fixed_prompt[idx]}\nFailed test cases for the above fix:\n{new_failed_tests[idx]}\n\n"

        system_prompt = """You are given a description of a task given to a person and instances of where this person made errors (question, answer and reason of incorrectness highlighting the error). This person is very smart so the reason of these failure must be in the instructions or the description of the task provided to this person. Your goal is to suggest improvements to the description of task / instructions so that the person can correctly answer all the questions. In the past you have already tried to improve the description. You are also provided with the list of modified descriptions where you earlier attempted to fix the incorrect answers but it did not work. Please avoid making similar mistakes in your new attempts and learn from the previous mistakes. If something corrected answers in the previous attempts try to use it again. Adapt your suggestions to the incorrect answers and the task description to ensure that the person answers all the questions correctly.

Think how can the task description be improved to fix the incorrect answers. The person only reads the task description once and then answers the questions. Please consider this while suggesting the fix as it might help you to understand why the person is failing the questions.

Follow these instructions for suggesting the fix:
1. Analyze the question, answer and the associated reason for each incorrect answer.
2. Since the person is very smart, you must connect the reason of failure to a rule or a constraint in the task description as the description is the only source of information for the person.
3. If the task description does not have a rule or a constraint related to the reason of incorrect, add a new rule or constraint to the task description. For example, if the reason of failure was the use of comma as delimiter in the answer but the task description did not specify the delimiter, then add a rule specifying the delimiter.
4. If the task description has a rule or a constraint already which is related to the incorrect answer, then analyze if falls in one of the following categories:
    - The rule or constraint is not clear or have ambiguity. In this case, make the rule or constraint more clear and specific.
    - The rule or constraint is not specific enough to handle this particular test (corner case). In this case, make the rule or constraint more specific while keeping it general enough to handle other cases.
    - The rule or constraint is not comprehensive enough to handle a particular test. In this case, make the rule or constraint more comprehensive.
    - The rule or constraint assumes context which is not provided in the task description. In this case, make the rule or constraint more general by adding the context to the task description.
    - The task description can correctly handle the test but the answer is still incorrect. In this case, increase the specificity or emphasis of the rule or constraint in the description hoping it will fix the failed test cases.

The categories of incorrect answers and the possible fixing techniques which are provided above are not exhaustive. Feel free to infer from the data provided to you that why is the person now able to answer the questions correctly for the task described.

The incorrect answers can only be corrected by modifying the task description. Please feel to try other techniques to fix the incorrect answers. Analyze each incorrect answer and reason step by step and suggest improvements trying to fix all the incorrect answers not just one.

While suggesting the fix you must follow these guidelines:
1. Add or remove a single sentence and use the information from the previous attempts to fix the incorrect answers.
2. Do not change the existing sentences in the task description unless necessary.
3. Do not add more examples to the task description especially to fix a particular incorrect answer.
4. Do not mention any specific question or answer in the task description as the task description must be general enough to handle all the questions.
5. Always address the question or test which will be given to the person as input.
6. If one was the previous attempt was more effective in fixing the incorrect answers, try to use it as a base to generate the new fix.

Output the reasoning and analysis used in coming up with the suggestion, also output how did you follow the instruction and which of the above categories were involved in the incorrect answer and then output the suggestion without any delimiter like ```. Never output the fixed description, only output the suggestion.
"""
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Here is the original system prompt:\n" + prompt + "\nHere are the fixing attempts starting from the original system prompt:\n" + log}]
        output = self.get_bot_response(messages)
        if output is None:
            return ""
        output.replace("**", "")
        return output

    def fix_prompt_with_suggestions(self, sugestions, fixed_prompt):

        log = ""
        for idx in range(len(fixed_prompt)):
            if idx == 0:
                log += f"Original System Prompt: {fixed_prompt[idx]}\n\n"
            else:
                log += f"Attempted Fix {idx}: {fixed_prompt[idx]}\n\n"

        system_prompt = """A description of a task was given to a person and they were asked to answer questions based on that. The person gave a lot of wrong answers. Eventually, it was realized that the person was very smart but the description of the task was not good. Also, there were other limitations like the person could only read the task once before answering questions. Deep analysis were conducted some suggestions were made to fix the description but it has not worked so far. You are given a list of the previous descriptions which were tried and suggestions for fixing the description. Your goal is to improve the description of task / instructions so that the person can correctly answer all the questions by applying the suggestions. Please avoid making similar mistakes in your new attempt and learn from the previous mistakes.

While generating the fix by applying the suggestion you must follow these guidelines:
1. Use the information from the previous attempts and the suggestions to fix the incorrect answers.
2. Work on sentence level and not word level which means remove or add sentences instead of changing the words in the sentences. This way the generated fix will have local changes and will be easier to understand.
3. Do not change the existing sentences in the task description unless necessary.
4. Do not mention any specific question or answer in the task description as the task description must be general enough to handle all the questions.
5. Always address the question or test which will be given to the person as input.
7. Never generate similar or redundant fixes which were already tried in the previous attempts.
8. Become more aggressive in applying the suggestion if it is already present in the previous attempts.
9. If the suggestion mentions a clear fix, make sure to include that but do not restrict yourself to only that fix. You can add more fixes to the description based on your understanding.

Only output the generated fixed description after applying the suggestion and nothing else.
"""
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": log + f"Here are the suggestions for fixing the description:\n{sugestions}"}]
        output = self.get_bot_response(messages)
        if output is None:
            return ""
        return output

    def fix_prompt_with_failures(self, prompt, failed_tests, fixed_prompt, new_failed_tests):
        Dbg.debug(f"[LLM FrontEnd][fix_prompt_with_failures] fixing prompt\n {prompt}\n with failed tests:\n {failed_tests}\n and new failed tests:\n {new_failed_tests}\n with fixed prompt:\n {fixed_prompt}")

        log = ""
        for idx in range(len(new_failed_tests)):
            log += f"Attempt {idx+1} to fix the original system prompt:\nGenerated Fix: {fixed_prompt[idx]}\nFailed test cases for the above fix:\n{new_failed_tests[idx]}\n\n"

        system_prompt = """You are given a description of a task given to a person and instances of where this person made errors (question, answer and reason of incorrectness highlighting the error). This person is very smart so the reason of these failure must be in the instructions or the description of the task provided to this person. Your goal is to improve the description of task / instructions so that the person can correctly answer all the questions. In the past you have already tried to improve the description. You are also provided with the list of modified descriptions where you earlier attempted to fix the incorrect answers but it did not work. Please avoid making similar mistakes in your new attempts and learn from the previous mistakes. If something corrected answers in the previous attempts try to use it again. Adapt your fixes to the incorrect answers and the task description to ensure that the person answers all the questions correctly.

Think how can the task description be improved to fix the incorrect answers. The person only reads the task description once and then answers the questions. Please consider this while generating the fix as it might help you to understand why the person is failing the questions.

Follow these instructions for generating the fix:
1. Analyze the question, answer and the associated reason for each incorrect answer.
2. Since the person is very smart, you must connect the reason of failure to a rule or a constraint in the task description as the description is the only source of information for the person.
3. If the task description does not have a rule or a constraint related to the reason of incorrect, add a new rule or constraint to the task description. For example, if the reason of failure was the use of comma as delimiter in the answer but the task description did not specify the delimiter, then add a rule specifying the delimiter.
4. If the task description has a rule or a constraint already which is related to the incorrect answer, then analyze if falls in one of the following categories:
    - The rule or constraint is not clear or have ambiguity. In this case, make the rule or constraint more clear and specific.
    - The rule or constraint is not specific enough to handle this particular test (corner case). In this case, make the rule or constraint more specific while keeping it general enough to handle other cases.
    - The rule or constraint is not comprehensive enough to handle a particular test. In this case, make the rule or constraint more comprehensive.
    - The rule or constraint assumes context which is not provided in the task description. In this case, make the rule or constraint more general by adding the context to the task description.
    - The task description can correctly handle the test but the answer is still incorrect. In this case, increase the specificity or emphasis of the rule or constraint in the description hoping it will fix the failed test cases.

The categories of incorrect answers and the possible fixing techniques which are provided above are not exhaustive. Feel free to infer from the data provided to you that why is the person now able to answer the questions correctly for the task described.

The incorrect answers can only be corrected by modifying the task description. Please feel to try other techniques to fix the incorrect answers. Analyze each incorrect answer and reason step by step and generate a fix trying to fix all the incorrect answers not just one.

While generating the fix you must follow these guidelines:
1. Add or remove a single sentence and use the information from the previous attempts to fix the incorrect answers.
2. Do not change the existing sentences in the task description unless necessary.
3. Do not add more examples to the task description especially to fix a particular incorrect answer.
4. Do not mention any specific question or answer in the task description as the task description must be general enough to handle all the questions.
5. Always address the question or test which will be given to the person as input.
6. If one was the previous attempt was more effective in fixing the incorrect answers, try to use it as a base to generate the new fix.

First output the reasoning and analysis used in generating the fix, also output how did you follow the instruction and which of the above categories were involved in the incorrect answer and then output the fixed description. The fixed description must start with a heading "Fixed:" and then the fixed description without any other delimiter like ```.

Do not output anything after the fixed description.
"""
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Here is the original system prompt:\n" + prompt + "\nHere are the fixing attempts starting from the original system prompt:\n" + log}]
        output = self.get_bot_response(messages)
        if output is None:
            return ""
        output.replace("**", "")
        output = output.split("Fixed:")[-1].strip()
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
        if output is None:
            return ""
        return output.strip()

    def expected_output(self, prompt, test_case):
        Dbg.debug(f"[LLM FrontEnd][expected_output] generating expected output for test case:\n {test_case}")
        system_prompt = "You are given a test case which is a valid input for a chatbot. Your task is to generate the expected output for the given test case. Only output the expected output and nothing else. The following is the description of the chatbot:\n" + prompt
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Test case: {test_case}"}]
        output = self.get_bot_response(messages)
        Dbg.debug(f"[LLM FrontEnd][expected_output] generated expected output: {output}")
        return output

    def extract_intent(self, prompt):
        Dbg.debug(f"[LLM FrontEnd][extract_intent] extracting intent from prompt:\n {prompt}")
        system_prompt = """You are given a description of a chatbot's task. Your task is to extract the intent of the chatbot from the given description. The intent is the primary goal or purpose of the chatbot. It is the action that the chatbot is designed to perform based on the task description.

In the output, provide the extracted intent of the chatbot. Only output the extracted intent and nothing else. Do not include any additional information in the output.
"""

        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
        output = self.get_bot_response(messages)
        Dbg.debug(f"[LLM FrontEnd][extract_intent] extracted intent: {output}")
        return output

    def check_violation_with_input_spec(self, test, input_spec):
        Dbg.debug(f"[LLM FrontEnd][check_violation_with_input_spec] checking violation for test:\n {test}")
        system_prompt = f"""You are given exactly one input and an input specification for the software. Your task is to very carefully and thoroughly evaluate the given input to find out if it complies with the provided input specification in other words, if the given input is a valid input for the software.

Use the following input specification to evaluate the test case:
[SPEC START]
{input_spec}
[SPEC END]

Follow these guidelines:
Output 0 if the input complies with the input specification.
Output 1 if the input does not comply with the input specification.
Output the decision as 0 or 1 with a single line description of the reason for the decision. Do not output anything else.
"""
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Input: {test}"}]
        output = self.get_bot_response(messages)
        Dbg.debug(f"[LLM FrontEnd][check_violation_with_input_spec] checked violation and got output: {output}")
        return output

    def check_rule_grounded(self, rule, description):
        Dbg.debug(f"[LLM FrontEnd][check_rule_grounded] checking rule grounded for rule:\n {rule}")
        system_prompt = f"""You are given a rule and a description of a chatbot's task. Your task is to evaluate the rule to determine if it is grounded in the provided description. A rule is considered grounded if it is supported by the information provided in the task description.

Use the following description to evaluate the rule:
{description}

Output '0' if the rule is grounded in the description. Output '1' if the rule is not grounded in the description. Only output the decision as 0 or 1 and nothing else.
"""
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Rule: {rule}"}]
        output = self.get_bot_response(messages)
        return output

    def extract_failure_categories(self, reasons):
        Dbg.debug(f"[LLM FrontEnd][extract_failure_categories] extracting failure categories from reasons:\n {reasons}")
        system_prompt = """You are given a list of reasons why a chatbot failed to answer a question. Your task is to extract the failure categories from the given reasons. A failure category is a high-level classification of the reason why the chatbot failed to answer the question. It is a general category that describes the nature of the failure.
Output the number of the failure categories extracted from the given reasons. Only output the number of extracted failure categories and nothing else. Do not include any additional information in the output not even the categories.
"""
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": reasons}]
        output = self.get_bot_response(messages)
        Dbg.debug(f"[LLM FrontEnd][extract_failure_categories] extracted failure categories: {output}")
        return output
