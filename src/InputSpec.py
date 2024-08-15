from . import LLMFrontEnd
import csv

class InputSpec:
    def __init__(self, prompt):
        self.prompt = prompt
        self.spec = self.extract_input_spec(prompt)
        self.path = None

    def __str__(self):
        if self.spec is None:
            return ""
        return "\n".join(str(line) for line in self.spec)

    def __repr__(self):
        return str(self)

    def extract_input_spec(self, context):
        spec = LLMFrontEnd().generate_input_spec(context)
        if spec is None:
            return []
        return spec.split("\n")

    def get_input_spec(self):
        return self.__str__()

    def export_csv(self, path):
        self.path = path
        with open(path, "w", encoding="utf-8", errors="ignore", newline='') as f:
            csv_write = csv.writer(f)
            csv_write.writerow(["input spec"])
            for line in self.spec:
                csv_write.writerow([line])

    def import_csv(self, path = None):
        if path is None:
            path = self.path
        
        assert path is not None, "Path is not specified"
        self.path = path
        self.spec = []
        with open(path, "r", encoding="utf-8", errors="ignore", newline='') as f:
            csv_read = csv.reader(f)
            next(csv_read)
            for row in csv_read:
                self.spec.append(row[0])
        return self.spec