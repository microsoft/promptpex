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
    print(f"prompt {filename}")

    # load the prompt file
    filepath = f"src/prompts/{filename}.prompty"
    prompt = frontmatter.load(filepath)
    # grabs the content
    content = prompt.content
    # remove system:, user: messages
    # Split the content into system and user sections
    system_section = re.search(r'^system:\n(.*?)\nuser:\n', content, flags=re.DOTALL | re.MULTILINE).group(1).strip() # type: ignore
    user_section = re.search(r'\nuser:\n(.*)', content, flags=re.DOTALL | re.MULTILINE).group(1).strip() # type: ignore
    # Apply jinja2 to the prompt content
    system_prompt = Template(system_section).render(kwargs)
    user_prompt = Template(user_section).render(kwargs)
    # return oai messages
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt }]
    return messages

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
        messages = render_prompt("rules_local_per_primitive", input_data = input_data)
        output = self.get_bot_response(messages)
        Dbg.debug(f"[LLM FrontEnd][generate_rules_local_per_primitive] generated rules: {output}")
        return output

    def generate_rules_global(self, input_data, num_rules=0):
        Dbg.debug(f"[LLM FrontEnd][generate_rules_global] generating rules for input: {input_data}")
        messages = render_prompt("rules_global", num_rules = 0,input_data = input_data )
        output = self.get_bot_response(messages)
        Dbg.debug(f"[LLM FrontEnd][generate_rules_global] generated rules: {output}")
        return output

    def generate_generic_rules_global(self, input_data, num_rules=0, allow=["output"], deny=["input"], instructions="", assistant = ""):
        Dbg.debug(f"[LLM FrontEnd][generate_rules_global] generating rules for input: {input_data}")
        allow_str = ", ".join(allow)
        deny_str = ", ".join(deny)
        messages = render_prompt("generic_rules_global", allow_str = allow_str, deny_str = deny_str, num_rules = num_rules, instructions = instructions, input_data = input_data)
        if (assistant != ""):
            messages.append({"role": "assistant", "content": assistant})
        output = self.get_bot_response(messages)
        Dbg.debug(f"[LLM FrontEnd][generate_rules_global] generated rules: {output}")
        return output

    def generate_input_spec(self, context):
        Dbg.debug(f"[LLM FrontEnd][generate_input_spec] generating input spec for context: {context}")
        messages = render_prompt("input_spec", context = context )
        output = self.get_bot_response(messages)
        Dbg.debug(f"[LLM FrontEnd][generate_input_spec] generated input spec: {output}")
        if output is None:
            return ""
        output = output.replace("\n\n", "\n").strip()
        return output

    def inverse_rule(self, rule):
        Dbg.debug(f"[LLM FrontEnd][inverse_rule] generating inverse rule for rule: {rule}")
        messages = render_prompt("inverse_rule", rule= rule)
        output = self.get_bot_response(messages)
        Dbg.debug(f"[LLM FrontEnd][inverse_rule] generated inverse rule: {output}")
        if output is None:
            return ""
        output = output.replace("\n\n", "\n").strip()
        return output

    def generate_baseline_test(self, prompt, num=1):
        Dbg.debug(f"[LLM FrontEnd][generate_baseline_test] generating test")
        messages = render_prompt("baseline_test", prompt=prompt)
        output = self.get_bot_response(messages)
        Dbg.debug(f"[LLM FrontEnd][generate_baseline_test] generated test: {output}")
        if output is None:
            return ""
        output = output.split("===")
        return output

    def generate_test(self, rule, context=None, input_spec=None, num=1):
        Dbg.debug(f"[LLM FrontEnd][generate_test] generating test for rule: {rule} \n input spec: {input_spec}")
        messages = render_prompt("test", num = num, input_spec = input_spec, context = context, rule=rule)
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
        messages = render_prompt("check_violation", result=result, spec=spec)
        output = self.get_bot_response(messages, temprature=0)
        Dbg.debug(f"[LLM FrontEnd][check_violation] checked violation and got output: {output}")
        return output

    def add_rule(self, original_system_prompt, num_rules="1"):
        messages = render_prompt("add_rule", original_system_prompt=original_system_prompt, num_rules=num_rules)
        output = self.get_bot_response(messages)
        return output

    def convert_rule_into_question(self, rule):
        Dbg.debug(f"[LLM FrontEnd][rule_to_question] converting rules:\n {rule}")
        messages = render_prompt("convert_rule_into_question", rule=rule)
        output = self.get_bot_response(messages)
        Dbg.debug(f"[LLM FrontEnd][rule_to_question] to questions:\n {output}")
        return output

    def check_violation_using_questions(self, result, spec):
        Dbg.debug(f"[LLM FrontEnd][check_violation] checking violation for result:\n {result} and spec:\n {spec}")
        questions = self.convert_rule_into_question(spec)
        messages = render_prompt("check_violation_using_questions", result=result, questions=questions)
        output = self.get_bot_response(messages, temprature=0)
        Dbg.debug(f"[LLM FrontEnd][check_violation] checked violation and got output: {output}")
        return output

    def check_violation_with_system_prompt_1(self, result, spec, system):
        Dbg.debug(f"[LLM FrontEnd][check_violation_sp] checking violation for result:\n {result} and spec:\n {spec}")
        messages = render_prompt("check_violation_with_system_prompt_1", result=result, spec=spec, system=system)
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
        outputs = []
        for res in result:
            messages = render_prompt("check_violation_sp_single", system=system, res=res)
            output = self.get_bot_response(messages, temprature=0)
            Dbg.debug(f"[LLM FrontEnd][check_violation_sp_single] checked violation and got output: {output}")
            outputs.append(output)

        return "\n".join(outputs)

    def check_violation_with_system_prompt_batch(self, result, system, num_tests, batch_mode):
        if not batch_mode:
            return self.check_violation_batch_to_single(result, system, num_tests)

        result = result.replace("__<<DELIMITIER>>__", "\n\n")

        Dbg.debug(f"[LLM FrontEnd][check_violation_sp_batch] checking violation for result:\n {result}")
        messages = render_prompt("check_violation_sp_batch", system=system, result=result, num_tests=num_tests)
        output = self.get_bot_response(messages, temprature=0)
        Dbg.debug(f"[LLM FrontEnd][check_violation_sp_batch] checked violation and got output: {output}")
        return output

    def get_fix_suggestions(self, prompt, failed_tests):
        Dbg.debug(f"[LLM FrontEnd][fix_prompt] fixing prompt with failed tests:\n {failed_tests}")

        messages = render_prompt("fix_suggestions", prompt=prompt, failed_tests=failed_tests)
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

        messages = render_prompt(
            "fix_prompt_without_rules",
            prompt=prompt,
            log=log,
            rejected=rejected
        )

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
        messages = render_prompt("rule_diff", rules1 = rules1, rules2 = rules2)
        output = self.get_bot_response(messages)
        if output is None:
            return ""
        return output.strip()

    def expected_output(self, prompt, test_case):
        Dbg.debug(f"[LLM FrontEnd][expected_output] generating expected output for test case:\n {test_case}")
        messages = render_prompt("expected_output", prompt = prompt, test_case = test_case)
        output = self.get_bot_response(messages)
        Dbg.debug(f"[LLM FrontEnd][expected_output] generated expected output: {output}")
        return output

    def extract_intent(self, prompt):
        Dbg.debug(f"[LLM FrontEnd][extract_intent] extracting intent from prompt:\n {prompt}")
        messages = render_prompt("extract_intent", prompt = prompt)
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
        messages = render_prompt("check_rule_grounded", rule = rule, description = description)
        output = self.get_bot_response(messages)
        return output

    def extract_failure_categories(self, reasons):
        Dbg.debug(f"[LLM FrontEnd][extract_failure_categories] extracting failure categories from reasons:\n {reasons}")
        messages = render_prompt("extract_failure_categories", reasons = reasons)
        output = self.get_bot_response(messages)
        Dbg.debug(f"[LLM FrontEnd][extract_failure_categories] extracted failure categories: {output}")
        return output
