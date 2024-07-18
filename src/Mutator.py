from . import LLMFrontEnd

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