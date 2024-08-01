from . import LLMFrontEnd

class Mutator:
    def __init__(self, system_prompt):
        self.original_system_prompt = system_prompt
        self.system_prompt = system_prompt

    def add_rule(self, num):
        self.system_prompt = LLMFrontEnd().add_rule(self.system_prompt, num)

    def add_rules(self, num):
        self.add_rule(str(num))

    def fix_prompt(self, failed_tests, fixed_prompt, new_failed_tests, ImmutableRules):
        if self.system_prompt == fixed_prompt:
            return LLMFrontEnd().fix_prompt(self.system_prompt, failed_tests)
        else:
            if new_failed_tests == "":
                return LLMFrontEnd().fix_prompt_without_rules(self.system_prompt, failed_tests, fixed_prompt[-1], ImmutableRules)
            else:
                return LLMFrontEnd().fix_prompt_with_failures(self.system_prompt, failed_tests, fixed_prompt[-1], new_failed_tests[-1])

    def get_prompt(self):
        return self.system_prompt