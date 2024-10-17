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
    # Check if the current directory ends with 'eval' and adjust the path accordingly
    current_directory = os.getcwd()
    if current_directory.endswith('eval') or current_directory.endswith('app'):
        filepath = f"../{filepath}"
    print(f"messages for {filepath}:")
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

    print("```")
    print(messages)
    print("```")
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
        messages = render_prompt(
            "check_violation_with_system_prompt",
            system=system,
            result=result
        )
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
        messages = render_prompt("fix_prompt", prompt=prompt, failed_tests=failed_tests)
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

        messages = render_prompt(
            "fix_suggestions_without_rules",
            prompt=prompt,
            log=log,
            rejected=rejected
        )

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

        messages = render_prompt(
            "fix_suggestions_with_failures",
            prompt=prompt,
            log=log
        )
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

        messages = render_prompt("fix_prompt_with_suggestions", log=log, sugestions=sugestions)
        output = self.get_bot_response(messages)
        if output is None:
            return ""
        return output

    def fix_prompt_with_failures(self, prompt, failed_tests, fixed_prompt, new_failed_tests):
        Dbg.debug(f"[LLM FrontEnd][fix_prompt_with_failures] fixing prompt\n {prompt}\n with failed tests:\n {failed_tests}\n and new failed tests:\n {new_failed_tests}\n with fixed prompt:\n {fixed_prompt}")

        log = ""
        for idx in range(len(new_failed_tests)):
            log += f"Attempt {idx+1} to fix the original system prompt:\nGenerated Fix: {fixed_prompt[idx]}\nFailed test cases for the above fix:\n{new_failed_tests[idx]}\n\n"

        messages = render_prompt("fix_prompt_with_failures", prompt=prompt, log=log)
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
        messages = render_prompt("check_violation_with_input_spec", input_spec=input_spec, test=test)
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
