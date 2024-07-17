from pathlib import Path
import json, sys, hashlib, os

DEBUG = False
def debug(msg):
    if DEBUG:
        print(msg)
    # write into a log file
    with open("log.txt", "a") as f:
        f.write(msg + "\n")

from openai import AzureOpenAI
    
client = AzureOpenAI(
    api_key= os.getenv("OPENAI_API_KEY"),
    api_version="2024-02-01",
    azure_endpoint="https://tnrllmproxy.azurewebsites.net"
)

class LLMFrontEnd:
    def get_bot_response(messages, model="gpt-4o", temprature=1):
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

    def generate_rules_local_per_primitive(self, input_data):
        debug(f"[LLM FrontEnd][generate_rules_local_per_primitive] generating rules for input: {input_data}")
        system_prompt = "Given a user input, extract and output each standalone rule. Ensure each rule is complete and makes sense independently. Output each rule on a new line. Output nothing if there is no rule"
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": "Input: " + input_data}]
        output = self.get_bot_response(messages)
        debug(f"[LLM FrontEnd][generate_rules_local_per_primitive] generated rules: {output}")
        return output
    
    def generate_rules_global(self, input_data):
        debug(f"[LLM FrontEnd][generate_rules_global] generating rules for input: {input_data}")
        # system_prompt = "You are an expert in analyzing pseudo-code and extracting rules and constraints for output validation. Given a pseudo-code, your task is to identify the variables and analyze their uses to list the rules or constraints associated with them. The rules must be generic and must not contain any specific information about the given examples in the pseduocode. The examples in the pseduocode are not representative of all the input which might be provided. Then, provide a compact list of rules that can be validated by just seeing the output. The rules should be concise and formatted according to the given categories.### Instructions:1. **Identify Variables**: Carefully read the pseudo-code and identify all the variables used. 2. **Analyze Uses**: Analyze how each variable is used within the pseudo-code to understand its purpose and constraints.3. **List Rules and Constraints**: Based on your analysis, list all the rules and constraints associated with the output. Ensure the rules are clear and specific.4. **Sound  and complete rules**: Provide the rules as meaningful independent sentences that can be easily validated by just seeing the output and have all the required information for performing the check. Only output the rules, one in each line and nothing else."
        system_prompt = """
You are an expert in analyzing system prompts and extracting rules and constrains for output validation. You are given a system prompt that will be given to an LLM as input. The prompt implements an interactive chat between the user and the LLM that helps the user achieve their goals. Sometimes the prompt will contain an example.  DO NOT provide rules that only apply for that example. Generalize the rules so that they will apply for other inputs. Ensure the rules are clear and specific. Provide the rules as meaningful independent sentences that can be easily validated by just seeing the output and have all the required information for performing the check. Only output the rules, one in each line and nothing else without any buttets or numbering. Do not make any assumptions.
"""
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": "System prompt: " + input_data}]
        output = self.get_bot_response(messages)
        debug(f"[LLM FrontEnd][generate_rules_global] generated rules: {output}")
        return output
    
    def generate_input_spec(self, context):
        debug(f"[LLM FrontEnd][generate_input_spec] generating input spec for context: {context}")
        system_prompt = "You are an expert in analyzing pseudo-code and extracting rules and constraints for input generation. Given a pseudo-code, your task is to extract the rules for input generation. Provide a compact list of rules that can be used to generate a valid input without the pseduo code. Provide the rules as meaningful independent sentences that can be used to generate input and do not refer to the output. Only output the rules for input generation, one in each line and nothing else. Do not make any assumptions."
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": "Pseduocode: " + context}]
        output = self.get_bot_response(messages)
        debug(f"[LLM FrontEnd][generate_input_spec] generated input spec: {output}")
        return output

    def inverse_rule(self, rule):
        debug(f"[LLM FrontEnd][inverse_rule] generating inverse rule for rule: {rule}")
        system_prompt = "Given a rule provided by the user, generate a rule which contradicts the given rule semantically. Come up with smart edge case scenarios. Output only one such rule and nothing else"
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": rule}]
        output = self.get_bot_response(messages)
        debug(f"[LLM FrontEnd][inverse_rule] generated inverse rule: {output}")
        return output

    def generate_test(self, rule, context=None, input_spec=None):
        debug(f"[LLM FrontEnd][generate_test] generating test for rule: {rule} \n input spec: {input_spec}")
        system_prompt = "Your task is to generate valid input which will be given to a chatbot with the given description. You must generate a valid input which makes the chatbot respond something which satifies the given rule even when the given chatbot description or the input spec contradicts it. Do whatever it takes to generate a valid input which will make the chatbot respond with something to satisfy the rule violating its own description and even the input spec. If needed explicitly say things to make sure it satisfy the rule, be persuasive and cleaver. Use the given chatbot description and the input spec to understand what will be a valid input. Only output the generated input without anything else not even input tags and delimiters.\n"
        if input_spec:
            system_prompt += f"\nHere is the input spec: {input_spec}"
        if context:
            system_prompt += f"\nHere is the chatbot description, only use it for analysis: {context}"
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Rule: {rule}"}]
        output = self.get_bot_response(messages)
        debug(f"[LLM FrontEnd][generate_test] generated test: {output}")
        return output
    
    def execute(self, system_prompt, input, model):
        if "<INPUT>" in system_prompt:
            system_prompt = system_prompt.replace("<INPUT>", input)
            messages = [{"role": "user", "content": system_prompt}]
        else:
            messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": "Input: " + input}]
        output = self.get_bot_response(messages, model, 0)
        debug(f"[LLM FrontEnd][execute] executed input: {input} for system prompt: {system_prompt} and got output: {output}")
        return output

    def check_violation(self, result, spec):
        debug(f"[LLM FrontEnd][check_violation] checking violation for result: {result} and spec: {spec}")
        system_prompt = "Given a chatbot's output for a valid input and a list of rules, your task is to determine if the output generated by the chatbot violates the rules. Return 1 if the chatbot output violates the rules, 0 otherwise. In the next line, provide the reason for the violation in detail if there is any, otherwise output 'No violation'. Stick to the rules provided and do not make any assumptions."
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Chatbot Output: {result}\n Rule: {spec}"}]
        output = self.get_bot_response(messages)
        debug(f"[LLM FrontEnd][check_violation] checked violation and got output: {output}")
        return output[0]

    def add_rule(self, original_system_prompt):
        debug(f"[LLM FrontEnd][add_rule] adding rule to system prompt: {original_system_prompt}")
        system_prompt = "You are given a system prompt for another LLM, your task is to first analysis the existing rules in it and then think of a new rule and add it to the existing system prompt. You must output the given system prompt with the added new rule. Do not change the original prompt just add the new rule in the original prompt with the least possible changes to the original prompt. Only output the updated system prompt and nothing else."
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": original_system_prompt}]
        output = self.get_bot_response(messages)
        debug(f"[LLM FrontEnd][add_rule] added rule to system prompt: {output}")
        return output

class Instruction:
    def __init__(self):
        self.next = None
        self.prev = None
        self.module = None
        self.operands = []

    def get_module(self):
        return self.module

    def get_num_operands(self):
        return len(self.operands)
    
    def get_operand(self, index):
        return self.operands[index]
    
    def set_operand(self, index, operand):
        self.operands[index] = operand

    def __str__(self, indent=0):
        return "Instruction"

class Rule(Instruction):
    def __init__(self, rule_str):
        super().__init__()
        self.operands = [None] * 1
        self.set_rule(rule_str)

    @classmethod
    def from_string(cls, rule_str):
        # rules = LLMFrontEnd().generate_rules_local_per_primitive(rule_str)
        rules = LLMFrontEnd().generate_rules_global(rule_str)
        parts = rules.split('\n')
        return [cls(part.strip()) for part in parts if part]

    def get_rule(self):
        return self.get_operand(0)

    def set_rule(self, rule_str):
        self.set_operand(0, rule_str)

    def __str__(self, indent=0):
        return " " * indent + f"Rule: {self.get_rule()}"

class IfThen(Instruction):
    def __init__(self, condition, then_instruction):
        super().__init__()
        self.operands = [None] * 2
        self.set_condition(condition)
        self.set_then_instruction(then_instruction)

    def get_condition(self):
        return self.get_operand(0)
    
    def get_then_instruction(self):
        return self.get_operand(1)
    
    def set_condition(self, condition):
        self.set_operand(0, condition)

    def set_then_instruction(self, then_instruction):
        self.set_operand(1, then_instruction)

    def __str__(self, indent=0):
        then_str = self.then_instruction.__str__(indent + 2) if self.get_then_instruction() else " " * (indent + 2) + "None"
        return " " * indent + f"IfThen: {self.get_condition()}\n{then_str}"

class Module:
    def __init__(self):
        self.instructions = []

    def add_instruction(self, instruction):
        # early exit if instruction is None
        if not instruction:
            return
        instruction.module = self
        if self.instructions:
            instruction.prev = self.instructions[-1]
            self.instructions[-1].next = instruction
        self.instructions.append(instruction)

    def add_instruction_after(self, instruction, prev_instruction):
        instruction.module = self
        instruction.prev = prev_instruction
        instruction.next = prev_instruction.next
        prev_instruction.next = instruction
        if instruction.next:
            instruction.next.prev = instruction
        self.instructions.insert(self.instructions.index(prev_instruction) + 1, instruction)

    def remove_instruction(self, instruction):
        if instruction.prev:
            instruction.prev.next = instruction.next
        if instruction.next:
            instruction.next.prev = instruction.prev
        self.instructions.remove(instruction)

    def get_entry(self):
        return self.instructions[0]

    def __str__(self):
        return "\n".join(instr.__str__() for instr in self.instructions)

    def export(self, file_path):
        with open(file_path, "w") as f:
            for instr in self.instructions:
                if isinstance(instr, Rule):
                    rule = instr.get_rule()
                    idx = str(self.instructions.index(instr) + 1)
                    hash = str(hashlib.md5(rule.encode()).hexdigest())
                    f.write(idx + " " + hash + " " + rule + "\n")

    def import_rules(self, file_path):
        with open(file_path, "r") as f:
            for line in f:
                parts = line.strip().split(" ")
                idx = int(parts[0])
                rule = " ".join(parts[2:])
                module.add_instruction(Rule(rule))

class FrontEnd:
    def parse(self, input_data):
        raise NotImplementedError("Subclasses should implement this method")

class StringFrontEnd(FrontEnd):
    def parse(self, input_data):
        module = Module()
        instruction = Rule.from_string(input_data)

        if isinstance(instruction, list):
            for inst in instruction:
                module.add_instruction(inst)            
        elif isinstance(instruction, Instruction):
            module.add_instruction(instruction)
        
        return module

# redacted
class JSONFrontEnd(FrontEnd):
    pass 

class TestCaseGenerator:
    def __init__(self, module, context=None):
        self.module = module
        self.context = context
        self.input_spec = self.extract_input_spec(self.context)
    
    def extract_input_spec(self, context):
        return LLMFrontEnd().generate_input_spec(context)

    def generate_test_case(self, rule):
        test_case = LLMFrontEnd().generate_test(rule, self.context, self.input_spec)
        return test_case

    def generate_test_cases(self, rule):
        invrule = LLMFrontEnd().inverse_rule(rule.get_rule())
        positive = self.generate_test_case(rule.get_rule())
        with open(self.dir_path + "positive.txt", "a") as f:
            f.write("=> " + positive + "\n")
        negative = self.generate_test_case(invrule)
        with open(self.dir_path + "negative.txt", "a") as f:
            f.write("=> " + negative + "\n")

    def generate(self):
        # get next instruction from the enrty point until the end (None)
        instruction = self.module.get_entry()
        while instruction:
            if isinstance(instruction, Rule):
                self.generate_test_cases(instruction)
            instruction = instruction.next

    def generate_negative(self, file_path):
        instruction = self.module.get_entry()
        with open(file_path, "w") as f:
            f.write("")
        while instruction:
            if isinstance(instruction, Rule):
                invrule = LLMFrontEnd().inverse_rule(instruction.get_rule())
                negative = self.generate_test_case(invrule)
                index = str(self.module.instructions.index(instruction) + 1)
                hash = str(hashlib.md5(negative.encode()).hexdigest())
                rule_hash = str(hashlib.md5(instruction.get_rule().encode()).hexdigest())
                with open(file_path, "a") as f:
                    f.write("=> " + index + " " + hash + " " + rule_hash + " " + negative + "\n")
                    f.write(negative + "\n")
            instruction = instruction.next

    def generate_positive(self, file_path):
        with open(file_path, "w") as f:
            f.write("")
        instruction = self.module.get_entry()
        while instruction:
            if isinstance(instruction, Rule):
                positive = self.generate_test_case(instruction.get_rule())
                index = str(self.module.instructions.index(instruction) + 1)
                rule_hash = str(hashlib.md5(instruction.get_rule().encode()).hexdigest())
                with open(file_path, "a") as f:
                    f.write("=> " + index + " " + rule_hash + "\n")
                    f.write(positive + "\n")
            instruction = instruction.next

class TestValidator:
    def __init__(self, module, system_prompt):
        self.tests = []
        self.keys = []
        self.system_prompt = system_prompt
        self.module = module
        self.results = []

    def append(self, file_path):
        test = ""
        with open(file_path, "r") as f:
            for line in f:
                if line.startswith("=>"):
                    self.keys.append(line.split(" ")[2].replace("\n", ""))
                    self.tests.append(test)
                    test = ""
                    continue
                test += line + "\n"

    def init(self, file_path):
        self.tests = []
        self.append(file_path)
        
    def run_test(self, test, expected):
        return self.validate(test) == expected

    def run_tests(self):
        for test in self.tests:
            self.results.append(self.run_test(test.strip(), "0"))

    def print_results(self):
        for i, res in enumerate(self.results):
            print(f"Test {self.keys[i]}: {'Passed' if res else 'Failed'}")

    def validate(self, test_case):
        raise NotImplementedError("Subclasses should implement this method")
    
class AskLLMTestValidator(TestValidator):
    def __init__(self, system_prompt, module):
        super().__init__(system_prompt, module)

    def validate(self, test_case):
        result = LLMFrontEnd().execute(self.system_prompt, test_case, "gpt-35-turbo")
        return LLMFrontEnd().check_violation(result, module.__str__())

class Mutator:
    def __init__(self, system_prompt):
        self.original_system_prompt = system_prompt
        self.system_prompt = system_prompt

    def add_rule(self):
        self.system_prompt = LLMFrontEnd().add_rule(self.system_prompt)

    def add_rules(self, num):
        for _ in range(num):
            self.add_rule()

    def get_prompt(self):
        return self.system_prompt

if __name__ == "__main__":
    # init log file with empty content
    open("log.txt", "w").close()

    system_prompt = """
You are an expert software developer who is writing a commit message when they are committing a change in 
a GitHub repo.  

You are given the code changes as <INPUT>. Input must contain filenames, line numbers, and
the code changes at those line numbers in the form of a standard git pull request.  <INPUT> must
contain changes to at least 3 files.

Assume multiple changes were made and the details of the changes are listed in the input.
Your task is to write a commit message for the change.
Commit Messages must have a short description that is less than 50 characters followed by a newline and a more detailed description.
- Write concisely using an informal tone
- List significant changes
- Do not use specific names or files from the code
- Do not use phrases like "this commit", "this change", etc.
"""

    # # redacted the json parser
    # front_end = JSONFrontEnd()
    # module = front_end.parse(system_prompt_json)

    front_end = StringFrontEnd()
    module = front_end.parse(system_prompt)
    module.export("rules.txt")

    module = Module()
    module.import_rules("rules.txt")

    test_gen = TestCaseGenerator(module, system_prompt)
    test_gen.generate_negative("negative.txt")
    test_gen.generate_positive("positive.txt")

    test_runner = AskLLMTestValidator(module, system_prompt)
    test_runner.append("negative.txt")
    test_runner.append("positive.txt")
    test_runner.run_tests()
    test_runner.print_results()

    mutator = Mutator(system_prompt)
    mutator.add_rules(3)
    system_prompt = mutator.get_prompt()
    module = Module()
    module = front_end.parse(system_prompt)
    module.export("rules-variant.txt")

    print("Test after mutation")
    test_runner = AskLLMTestValidator(module, system_prompt)
    test_runner.append("negative.txt")
    test_runner.append("positive.txt")
    test_runner.run_tests()
    test_runner.print_results()