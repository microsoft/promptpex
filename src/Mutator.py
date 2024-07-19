from . import LLMFrontEnd

class Mutator:
    def __init__(self, system_prompt):
        self.original_system_prompt = system_prompt
        self.system_prompt = system_prompt

    def add_rule(self, num):
        self.system_prompt = LLMFrontEnd().add_rule(self.system_prompt, num)

    def add_rules(self, num):
        self.add_rule(str(num))

    def get_prompt(self):
        return self.system_prompt