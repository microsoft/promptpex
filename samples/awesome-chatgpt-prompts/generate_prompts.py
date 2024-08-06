import pandas as pd

with open("prompts.csv", "r", encoding="utf-8") as f:
    prompts = pd.read_csv(f)
    # iterate over the rows
    for index, row in prompts.iterrows():
        # convert into camel case
        name = row["act"].replace(" ", "").replace("/", "")
        with open(f"{name}.txt", "w", encoding="utf-8") as file:
            file.write(row["prompt"])