from os import path
from src import SemanticDiff, Utils, TestCaseGenerator, Module, LLMFrontEnd, StringFrontEnd, Module, AskLLMTestValidator
import pathlib, csv
import pandas as pd

import sys
def generate_code_for_rules():
    sp = """
Your task is to assess a series of rules and determine the most suitable method—whether it can be tested using traditional coding functions or an NLP-based tool—for each rule. You will then provide the name of the corresponding function, code snippet, or tool that can be used for validation.

**Instructions:**

1. Receive a long list of rules as input.
2. For each rule, decide if it can be tested using code (e.g., Python functions) or using an NLP-based tool (e.g., sentiment analysis, text embeddings).
3. Output the name of the function, code snippet, or tool that can be used to test or validate the rule.
4. If needed, make up complex operations that involve text embeddings or advanced NLP techniques.

**Examples:**

**Example 1:**

- **Rule:** Length of message is less than 50.
- **Validation Method:**
  - **Function:** `len`
  - **Snippet:** `len(msg) < 50`

**Example 2:**

- **Rule:** Output must be either "True" or "False."
- **Validation Method:**
  - **Function:** `find_in_list`
  - **Snippet:** `if(["True", "False"]).find(text)`

**Example 3:**

- **Rule:** Email must contain the substring "example.com."
- **Validation Method:**
  - **Function:** `substring`
  - **Snippet:** `"example.com" in email`

**Example 4:**

- **Rule:** The text should express a positive sentiment.
- **Validation Method:**
  - **NLP Tool:** `Sentiment Analysis`
  - **Tool:** `VADER` (Valence Aware Dictionary and Sentiment Reasoner)
  - **Snippet:**
    ```python
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

    analyzer = SentimentIntensityAnalyzer()
    sentiment_score = analyzer.polarity_scores(text)

    if sentiment_score['compound'] > 0.05:
        positive = True
    else:
        positive = False
    ```

**Example 5:**

- **Rule:** Text should be similar in meaning to "Hello, how are you?"
- **Validation Method:**
  - **NLP Tool:** Text Embeddings & Similarity
  - **Tool:** `BERT`
  - **Snippet:**
    ```python
    from sentence_transformers import SentenceTransformer, util

    model = SentenceTransformer('bert-base-nli-mean-tokens')
    embedding1 = model.encode("Hello, how are you?")
    embedding2 = model.encode(text)

    similarity = util.pytorch_cos_sim(embedding1, embedding2)[0][0]
    if similarity > 0.8:  # Assuming a threshold of 0.8 for similarity
        is_similar = True
    else:
        is_similar = False
    ```

By following these examples, evaluate and derive the most suitable method for each rule given to you. Generate complete code for checking the rules. Create a big single program which tests for these rules, this program should take the text as input and all the checks for the rules must be hardcoded, try to cover all the rules given to you and make sure that the program is able to check for all the rules. Combine all the rules and their corresponding validation methods into a single program. Combine these checkes such that you generate the shortest progarm for these rules with maximum reusability of code. Try to use the same functions with different arguments for different rules. Do not output anything other than the code. Do not write the test driver code. Do not write the main function.
"""
    input_file = pathlib.Path("rules-total.csv")
    output_file = pathlib.Path("rules-tools.txt")

    # open output file for appending
    with open(output_file, 'w') as f:
        pass
    # read 100 lines at a time and process them
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = f.readlines()
        data = []
        for row in reader:
            data.append(row)
            if len(data) == 200:
                data_str = "\n".join(data)
                result = LLMFrontEnd().execute(sp, data_str, "gpt-4-turbo", 1)
                if result is None:
                    result = "NULL\n"
                print(result)
                with open(output_file, 'a', encoding='utf-8') as f:
                    f.write(result)
                data = []

    result = LLMFrontEnd().execute(sp, "hi", "gpt-4-turbo", 1)
    print(result)

def generate_api_for_rules():
    sp = """
Your task is to review a list of code snippets provided for different rules and perform the following:

1. Extract common generic functions from the domain-specific code.
2. Convert these existing functions into more generic functions that can be used across various contexts.
3. Generate a list of API endpoints for these generalized functions, which can be used as a library.

**Instructions:**

1. Receive a long list of domain-specific code snippets.
2. Identify common patterns and operations in these snippets.
3. Extract and convert these operations into generic functions.
4. Generate a list of API endpoints for these generic functions.

**Example Input Codes:**

```python
# Example 1: Length check for message
def check_msg_length(msg, length_threshold):
    return len(msg) < length_threshold

# Example 2: Validate if output is True or False
def validate_output(output):
    return output in ["True", "False"]

# Example 3: Check if email contains specific domain
def check_email_domain(email, domain):
    return domain in email

# Example 4: Sentiment analysis using VADER
def analyze_sentiment(text):
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    analyzer = SentimentIntensityAnalyzer()
    sentiment_score = analyzer.polarity_scores(text)
    return sentiment_score['compound'] > 0.05

# Example 5: Similarity check using BERT
def check_similarity(text1, text2, threshold=0.8):
    from sentence_transformers import SentenceTransformer, util
    model = SentenceTransformer('bert-base-nli-mean-tokens')
    embedding1 = model.encode(text1)
    embedding2 = model.encode(text2)
    similarity = util.pytorch_cos_sim(embedding1, embedding2)[0][0]
    return similarity > threshold
```

**Example Output:**

**Generic Functions:**

```python
def is_length_within_limit(text, limit):
    return len(text) < limit

def is_in_list(item, valid_items):
    return item in valid_items

def contains_substring(container, substring):
    return substring in container

def analyze_sentiment_vader(text):
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    analyzer = SentimentIntensityAnalyzer()
    sentiment_score = analyzer.polarity_scores(text)
    return sentiment_score['compound']

def compute_cosine_similarity(text1, text2, model_name='bert-base-nli-mean-tokens'):
    from sentence_transformers import SentenceTransformer, util
    model = SentenceTransformer(model_name)
    embedding1 = model.encode(text1)
    embedding2 = model.encode(text2)
    similarity = util.pytorch_cos_sim(embedding1, embedding2)[0][0]
    return similarity
```

**API Endpoints:**

1. `POST /api/is_length_within_limit` - Parameters: `{ "text": "string", "limit": "number" }`
2. `POST /api/is_in_list` - Parameters: `{ "item": "string", "valid_items": ["string"] }`
3. `POST /api/contains_substring` - Parameters: `{ "container": "string", "substring": "string" }`
4. `POST /api/analyze_sentiment_vader` - Parameters: `{ "text": "string" }`
5. `POST /api/compute_cosine_similarity` - Parameters: `{ "text1": "string", "text2": "string", "model_name": "string" }`

Even if the rules was to check the lenth of commit message or any other text, the output must be the same as they can use the same API function. The API function must not be specific to a use case, they can only be generic functions which look for common properties.

Only output the list of APIs
"""
    rule_code = pathlib.Path("rules-tools.txt")
    output_file = pathlib.Path("rules-api.txt")

    # open output file for appending
    with open(output_file, 'w') as f:
        pass

    # read 100 lines at a time and process them
    with open(rule_code, 'r', encoding='utf-8') as f:
        reader = f.readlines()
        data = []
        for row in reader:
            data.append(row)
            if len(data) == 200:
                data_str = "\n".join(data)
                result = LLMFrontEnd().execute(sp, data_str, "gpt-4o", 1)
                if result is None:
                    result = "NULL\n"
                print(result)
                with open(output_file, 'a', encoding='utf-8') as f:
                    f.write(result)
                data = []

if __name__ == "__main__":
    generate_code_for_rules()
    generate_api_for_rules()

    sp = """You are given a list of API endpoints. Your task is to convert these domain specific API endpoints into more generic API endpoints which can be used across various contexts. You have to output the list of generic API endpoints which can be used across various contexts. For each input API endpoint output how the existing APIs can be switched with the generic one and then output the list of generic API endpoints. Please process all the API endpoints given as input."""

    input_file = pathlib.Path("rules-api.txt")
    output_file = pathlib.Path("rules-generic-api.txt")

    # open output file for appending
    with open(output_file, 'w') as f:
        pass

    # read 100 lines at a time and process them
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = f.readlines()
        data = "\n".join(reader)
        result = LLMFrontEnd().execute(sp, data, "gpt-4-turbo", 1)
        if result is None:
            result = "NULL\n"
        print(result)
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write(result)