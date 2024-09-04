from numpy import fix
from . import LLMFrontEnd

class Mutator:
    def __init__(self, system_prompt):
        self.original_system_prompt = system_prompt
        self.system_prompt = system_prompt

    # Not used
    def add_rule(self, num):
        self.system_prompt = LLMFrontEnd().add_rule(self.system_prompt, num)

    def add_rules(self, num):
        self.add_rule(str(num))

    def fix_prompt(self, failed_tests, fixed_prompt, new_failed_tests, ImmutableRules):
        if len(fixed_prompt) == 0:
            return LLMFrontEnd().fix_prompt(self.system_prompt, failed_tests)
        else:
            if len(ImmutableRules) != 0:
                return LLMFrontEnd().fix_prompt_without_rules(self.system_prompt, failed_tests, fixed_prompt, new_failed_tests, ImmutableRules)
            else:
                return LLMFrontEnd().fix_prompt_with_failures(self.system_prompt, failed_tests, fixed_prompt, new_failed_tests)

    def get_fix_suggestions(self, failed_tests, fixed_prompt, new_failed_tests, ImmutableRules):
        if len(fixed_prompt) == 0:
            return LLMFrontEnd().get_fix_suggestions(self.system_prompt, failed_tests)
        else:
            if len(ImmutableRules) != 0:
                return LLMFrontEnd().get_fix_suggestions_without_rules(self.system_prompt, failed_tests, fixed_prompt, new_failed_tests, ImmutableRules)
            else:
                return LLMFrontEnd().get_fix_suggestions_with_failures(self.system_prompt, failed_tests, fixed_prompt, new_failed_tests)

    def fix_prompt_with_suggestions(self, suggestions, attempts):
        return LLMFrontEnd().fix_prompt_with_suggestions(suggestions, attempts)

    def fix_prompt_after_extracting_suggestions(self, failed_tests, fixed_prompt, new_failed_tests, ImmutableRules):
        suggestions = self.get_fix_suggestions(failed_tests, fixed_prompt, new_failed_tests, ImmutableRules)
        return self.fix_prompt_with_suggestions(suggestions, new_failed_tests)

    def get_prompt(self):
        return self.system_prompt