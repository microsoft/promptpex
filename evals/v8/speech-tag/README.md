## speech-tag ([json](./evals\v8\speech-tag/report.json))

- 4 rules
- 4 inverse rules
- 48 tests, 24 baseline tests
- 192 test results, 144/192 (75%) oks, 48/192 (25%) errs

### Overview

<details><summary>Glossary</summary>
    
- Prompt Under Test (PUT) - like Program Under Test; the prompt
- Model Under Test (MUT) - Model which we are testing against with specific temperature, etc example: gpt-4o-mini
- Model Used by PromptPex (MPP) - gpt-4o

- Input Specification (IS) - Extracting input constraints of PUT using MPP
- Output Rules (OR) - Extracting output constraints of PUT using MPP
- Output Rules Groundedness (ORG) - Checks if OR is grounded in PUT using MPP

- Prompt Under Test Intent (PUTI) - Extracting the exact task from PUT using MMP

- PromptPex Tests (PPT) - Test cases generated for PUT with MPP using IS and OR
- Baseline Tests (BT) - Zero shot test cases generated for PUT with MPP

- Test Input Compliance (TIC) - Checking if PPT and BT meets the constraints in IS using MPP
- Test Coverage (TC) - Result generated for PPT and BT on PUTI + OR with MPP

- Test Output (TO) - Result generated for PPT and BT on PUT with each MUT
- Test Output Compliance (TOC) - Checking if TO meets the constraints in PUT using MPP

</details>


### [test_results.csv](./test_results.csv)

|model|tests|tests compliant|baseline compliant|tests positive|tests positive compliant|tests negative|tests negative compliant|baseline|tests valid|tests valid compliant|
|-|-|-|-|-|-|-|-|-|-|-|
|gpt\-4o\-mini|24|100%|100%|12|12|12|12|24|20|20|
|gemma2:9b|24|100%|100%|12|12|12|12|24|20|20|
|qwen2\.5:3b|24|96%|92%|12|11|12|12|24|20|19|
|llama3\.2:1b|24|8%|4%|12|0|12|2|24|20|2|

### [speech-tag.prompty](./speech-tag.prompty)

`````md
---
name: Speech Tag
description: Determine the part of speech for a given word
source: "modified from 'SAMMO: A general-purpose framework for prompt optimization'"
url: https://www.microsoft.com/en-us/research/uploads/prod/2024/04/Prompts-As-Programs_A-Structure-Aware-Approach.pdf
inputs:
    sentenceword:
        type: string
sample:
    sentenceword: "The quick brown fox jumps over the lazy dog.; jumps"
---
system:
In this task, you will be presented with a sentence and a word contained
in that sentence. You have to determine the part of speech for a given word
and return just the tag for the word's part of speech. 

Return only the part of speech tag.  If the word cannot be tagged with
the listed tags, return Unknown.  If you are unable to tag the word, return
CantAnswer.

Here is the
Alphabetical list of part-of-speech tags used in this task: CC: Coordinating conjunction, CD: Cardinal number, DT:
Determiner, EX: Existential there, FW: Foreign word, IN: Preposition or subordinating conjunction, JJ: Adjective, JJR:
Adjective, comparative, JJS: Adjective, superlative, LS: List item marker, MD: Modal, NN: Noun, singular or mass, NNS: Noun,
plural, NNP: Proper noun, singular, NNPS: Proper noun, plural, PDT: Predeterminer, POS: Possessive ending, PRP: Personal
pronoun, PRP$: Possessive pronoun, RB: Adverb, RBR: Adverb, comparative, RBS: Adverb, superlative, RP: Particle, SYM: Symbol,
TO: to, UH: Interjection, VB: Verb, base form, VBD: Verb, past tense, VBG: Verb, gerund or present participle, VBN: Verb,
past participle, VBP: Verb, non-3rd person singular present, VBZ: Verb, 3rd person singular present, WDT: Wh-determiner, WP:
Wh-pronoun, WP$: Possessive wh-pronoun, WRB: Wh-adverb
user:
{{sentenceword}}
`````


### [test_results.csv](./test_results.csv)

|model|rule|input|output|compliance|
|-|-|-|-|-|
|gpt\-4o\-mini|The output must be a single part of speech tag that represents the given word's role in the sentence according to the specified list of tags\.|sentence: The quick brown fox jumps over the lazy dog\., word: fox|NN|ok|
|gpt\-4o\-mini|The output must be a single part of speech tag that represents the given word's role in the sentence according to the specified list of tags\.|sentence: She sells seashells by the seashore\., word: by|IN|ok|
|gpt\-4o\-mini|The output must be a single part of speech tag that represents the given word's role in the sentence according to the specified list of tags\.|sentence: Wow, that's amazing\!, word: Wow|UH|ok|
|gpt\-4o\-mini|If the given word cannot be accurately tagged using the provided list of part\-of\-speech tags, the output must be the word "Unknown"\.|sentence: The xylophone zxylophone harmonizes\., word: zxylophone|Unknown|ok|
|gpt\-4o\-mini|If the given word cannot be accurately tagged using the provided list of part\-of\-speech tags, the output must be the word "Unknown"\.|sentence: He ate the mysterious food item\., word: food|NN|ok|
|gpt\-4o\-mini|If the given word cannot be accurately tagged using the provided list of part\-of\-speech tags, the output must be the word "Unknown"\.|sentence: As he qwertyuiop in the room\., word: qwertyuiop|Unknown|ok|
|gpt\-4o\-mini|If it is impossible to determine a part of speech for the given word, the output must be the word "CantAnswer"\.|sentence: She spoke eloquently although about nothing in particular\., word: although|IN|ok|
|gpt\-4o\-mini|If it is impossible to determine a part of speech for the given word, the output must be the word "CantAnswer"\.|sentence: Despite the conditions, they succeeded\., word: conditions|NNS|ok|
|gpt\-4o\-mini|If it is impossible to determine a part of speech for the given word, the output must be the word "CantAnswer"\.|sentence: The truth was uncertain, shenative\., word: shenative|Unknown|ok|
|gpt\-4o\-mini|The output must not contain any additional text, punctuation, or formatting besides the part of speech tag or the words "Unknown" or "CantAnswer"\.|sentence: He quickly ran to the store\., word: quickly|RB|ok|
|gpt\-4o\-mini|The output must not contain any additional text, punctuation, or formatting besides the part of speech tag or the words "Unknown" or "CantAnswer"\.|sentence: This is the best ever\!, word: best|JJ|ok|
|gpt\-4o\-mini|The output must not contain any additional text, punctuation, or formatting besides the part of speech tag or the words "Unknown" or "CantAnswer"\.|sentence: Do you have a pen?, word: you|PRP|ok|
|gpt\-4o\-mini|The output must be multiple parts of speech tags representing different potential roles for the given word according to any possible tags\.|sentence: She booked the show\., word: booked|VBD|ok|
|gpt\-4o\-mini|The output must be multiple parts of speech tags representing different potential roles for the given word according to any possible tags\.|sentence: Play the notes\., word: Play|VB|ok|
|gpt\-4o\-mini|The output must be multiple parts of speech tags representing different potential roles for the given word according to any possible tags\.|sentence: The run was tiresome\., word: run|NN|ok|
|gpt\-4o\-mini|If the given word can be tagged using any known part\-of\-speech tags, the output must not include the word "Unknown"\.|sentence: She sings beautifully\., word: sings|VB|ok|
|gpt\-4o\-mini|If the given word can be tagged using any known part\-of\-speech tags, the output must not include the word "Unknown"\.|sentence: It shines brightly\., word: shines|VB|ok|
|gpt\-4o\-mini|If the given word can be tagged using any known part\-of\-speech tags, the output must not include the word "Unknown"\.|sentence: Light travels fast\., word: travels|VBZ|ok|
|gpt\-4o\-mini|If it is possible to determine a part of speech for the given word, the output must be entirely blank or contain an error message\.|sentence: The cat sleeps peacefully\., word: cat|NN|ok|
|gpt\-4o\-mini|If it is possible to determine a part of speech for the given word, the output must be entirely blank or contain an error message\.|sentence: She understood the question\., word: understood|VBD|ok|
|gpt\-4o\-mini|If it is possible to determine a part of speech for the given word, the output must be entirely blank or contain an error message\.|sentence: He will write a letter\., word: write|VB|ok|
|gpt\-4o\-mini|The output must contain additional text, punctuation, or formatting besides the part of speech tag or the words "Unknown" or "CantAnswer"\.|sentence: There is a book on the table\., word: book|NN|ok|
|gpt\-4o\-mini|The output must contain additional text, punctuation, or formatting besides the part of speech tag or the words "Unknown" or "CantAnswer"\.|sentence: A quick brown fox?, word: quick|JJ|ok|
|gpt\-4o\-mini|The output must contain additional text, punctuation, or formatting besides the part of speech tag or the words "Unknown" or "CantAnswer"\.|sentence: Where did she go?, word: Where|WRB|ok|
|gpt\-4o\-mini||sentence: The cat sat on the mat\. word: cat|NN|ok|
|gpt\-4o\-mini||sentence: She quickly finished her homework\. word: quickly|RB|ok|
|gpt\-4o\-mini||sentence: We will visit Paris next summer\. word: Paris|NNP|ok|
|gpt\-4o\-mini||sentence: They haven't arrived at the station yet\. word: arrived|VBN|ok|
|gpt\-4o\-mini||sentence: Tom and Jerry are famous cartoon characters\. word: and|CC|ok|
|gpt\-4o\-mini||sentence: She is going to the gym\. word: is|VB|ok|
|gpt\-4o\-mini||sentence: There were many reasons for the success\. word: There|EX|ok|
|gpt\-4o\-mini||sentence: That is the biggest cake I have ever seen\. word: biggest|JJ|ok|
|gpt\-4o\-mini||sentence: I can do it alone\. word: can|MD|ok|
|gpt\-4o\-mini||sentence: Please hand me the red book\. word: book|NN|ok|
|gpt\-4o\-mini||sentence: The baby's toy was missing\. word: baby's|POS|ok|
|gpt\-4o\-mini||sentence: Ouch, that hurts\! word: Ouch|UH|ok|
|gpt\-4o\-mini||sentence: If he studies hard, he might pass the test\. word: If|IN|ok|
|gpt\-4o\-mini||sentence: There are 12 eggs in the basket\. word: 12|CD|ok|
|gpt\-4o\-mini||sentence: Whoever answers correctly gets a prize\. word: Whoever|PRP|ok|
|gpt\-4o\-mini||sentence: Happy people are more productive\. word: Happy|JJ|ok|
|gpt\-4o\-mini||sentence: The wheels on the bus go round and round\. word: on|IN|ok|
|gpt\-4o\-mini||sentence: Jane barely passed the exam this time\. word: barely|RB|ok|
|gpt\-4o\-mini||sentence: Alas, the show is over\. word: Alas|UH|ok|
|gpt\-4o\-mini||sentence: Would you like tea or coffee? word: or|CC|ok|
|gpt\-4o\-mini||sentence: Some students forgot their umbrellas\. word: their|PRP$|ok|
|gpt\-4o\-mini||sentence: The golden trophy was awarded to the winner\. word: golden|JJ|ok|
|gpt\-4o\-mini||sentence: I might have taken the wrong turn\. word: might|MD|ok|
|gpt\-4o\-mini||sentence: Certainly, that is the correct answer\. word: Certainly|RB|ok|
|gemma2:9b|The output must be a single part of speech tag that represents the given word's role in the sentence according to the specified list of tags\.|sentence: The quick brown fox jumps over the lazy dog\., word: fox|NN|ok|
|gemma2:9b|The output must be a single part of speech tag that represents the given word's role in the sentence according to the specified list of tags\.|sentence: She sells seashells by the seashore\., word: by|IN|ok|
|gemma2:9b|The output must be a single part of speech tag that represents the given word's role in the sentence according to the specified list of tags\.|sentence: Wow, that's amazing\!, word: Wow|UH|ok|
|gemma2:9b|If the given word cannot be accurately tagged using the provided list of part\-of\-speech tags, the output must be the word "Unknown"\.|sentence: The xylophone zxylophone harmonizes\., word: zxylophone|NN|ok|
|gemma2:9b|If the given word cannot be accurately tagged using the provided list of part\-of\-speech tags, the output must be the word "Unknown"\.|sentence: He ate the mysterious food item\., word: food|NN|ok|
|gemma2:9b|If the given word cannot be accurately tagged using the provided list of part\-of\-speech tags, the output must be the word "Unknown"\.|sentence: As he qwertyuiop in the room\., word: qwertyuiop|FW|ok|
|gemma2:9b|If it is impossible to determine a part of speech for the given word, the output must be the word "CantAnswer"\.|sentence: She spoke eloquently although about nothing in particular\., word: although|IN|ok|
|gemma2:9b|If it is impossible to determine a part of speech for the given word, the output must be the word "CantAnswer"\.|sentence: Despite the conditions, they succeeded\., word: conditions|NN|ok|
|gemma2:9b|If it is impossible to determine a part of speech for the given word, the output must be the word "CantAnswer"\.|sentence: The truth was uncertain, shenative\., word: shenative|Unknown|ok|
|gemma2:9b|The output must not contain any additional text, punctuation, or formatting besides the part of speech tag or the words "Unknown" or "CantAnswer"\.|sentence: He quickly ran to the store\., word: quickly|RB|ok|
|gemma2:9b|The output must not contain any additional text, punctuation, or formatting besides the part of speech tag or the words "Unknown" or "CantAnswer"\.|sentence: This is the best ever\!, word: best|JJS|ok|
|gemma2:9b|The output must not contain any additional text, punctuation, or formatting besides the part of speech tag or the words "Unknown" or "CantAnswer"\.|sentence: Do you have a pen?, word: you|PRP|ok|
|gemma2:9b|The output must be multiple parts of speech tags representing different potential roles for the given word according to any possible tags\.|sentence: She booked the show\., word: booked|VBD|ok|
|gemma2:9b|The output must be multiple parts of speech tags representing different potential roles for the given word according to any possible tags\.|sentence: Play the notes\., word: Play|VB|ok|
|gemma2:9b|The output must be multiple parts of speech tags representing different potential roles for the given word according to any possible tags\.|sentence: The run was tiresome\., word: run|NN|ok|
|gemma2:9b|If the given word can be tagged using any known part\-of\-speech tags, the output must not include the word "Unknown"\.|sentence: She sings beautifully\., word: sings|VBZ|ok|
|gemma2:9b|If the given word can be tagged using any known part\-of\-speech tags, the output must not include the word "Unknown"\.|sentence: It shines brightly\., word: shines|VBZ|ok|
|gemma2:9b|If the given word can be tagged using any known part\-of\-speech tags, the output must not include the word "Unknown"\.|sentence: Light travels fast\., word: travels|VBZ|ok|
|gemma2:9b|If it is possible to determine a part of speech for the given word, the output must be entirely blank or contain an error message\.|sentence: The cat sleeps peacefully\., word: cat|NN|ok|
|gemma2:9b|If it is possible to determine a part of speech for the given word, the output must be entirely blank or contain an error message\.|sentence: She understood the question\., word: understood|VBD|ok|
|gemma2:9b|If it is possible to determine a part of speech for the given word, the output must be entirely blank or contain an error message\.|sentence: He will write a letter\., word: write|VB|ok|
|gemma2:9b|The output must contain additional text, punctuation, or formatting besides the part of speech tag or the words "Unknown" or "CantAnswer"\.|sentence: There is a book on the table\., word: book|NN|ok|
|gemma2:9b|The output must contain additional text, punctuation, or formatting besides the part of speech tag or the words "Unknown" or "CantAnswer"\.|sentence: A quick brown fox?, word: quick|JJ|ok|
|gemma2:9b|The output must contain additional text, punctuation, or formatting besides the part of speech tag or the words "Unknown" or "CantAnswer"\.|sentence: Where did she go?, word: Where|WDT|ok|
|gemma2:9b||sentence: The cat sat on the mat\. word: cat|NN|ok|
|gemma2:9b||sentence: She quickly finished her homework\. word: quickly|RB|ok|
|gemma2:9b||sentence: We will visit Paris next summer\. word: Paris|NNP|ok|
|gemma2:9b||sentence: They haven't arrived at the station yet\. word: arrived|VBD|ok|
|gemma2:9b||sentence: Tom and Jerry are famous cartoon characters\. word: and|CC|ok|
|gemma2:9b||sentence: She is going to the gym\. word: is|VBZ|ok|
|gemma2:9b||sentence: There were many reasons for the success\. word: There|EX|ok|
|gemma2:9b||sentence: That is the biggest cake I have ever seen\. word: biggest|JJS|ok|
|gemma2:9b||sentence: I can do it alone\. word: can|MD|ok|
|gemma2:9b||sentence: Please hand me the red book\. word: book|NN|ok|
|gemma2:9b||sentence: The baby's toy was missing\. word: baby's|POS|ok|
|gemma2:9b||sentence: Ouch, that hurts\! word: Ouch|UH|ok|
|gemma2:9b||sentence: If he studies hard, he might pass the test\. word: If|IN|ok|
|gemma2:9b||sentence: There are 12 eggs in the basket\. word: 12|CD|ok|
|gemma2:9b||sentence: Whoever answers correctly gets a prize\. word: Whoever|WDT|ok|
|gemma2:9b||sentence: Happy people are more productive\. word: Happy|JJ|ok|
|gemma2:9b||sentence: The wheels on the bus go round and round\. word: on|IN|ok|
|gemma2:9b||sentence: Jane barely passed the exam this time\. word: barely|RB|ok|
|gemma2:9b||sentence: Alas, the show is over\. word: Alas|UH|ok|
|gemma2:9b||sentence: Would you like tea or coffee? word: or|CC|ok|
|gemma2:9b||sentence: Some students forgot their umbrellas\. word: their|PRP$|ok|
|gemma2:9b||sentence: The golden trophy was awarded to the winner\. word: golden|JJ|ok|
|gemma2:9b||sentence: I might have taken the wrong turn\. word: might|MD|ok|
|gemma2:9b||sentence: Certainly, that is the correct answer\. word: Certainly|UH|ok|
|qwen2\.5:3b|The output must be a single part of speech tag that represents the given word's role in the sentence according to the specified list of tags\.|sentence: The quick brown fox jumps over the lazy dog\., word: fox|NN|ok|
|qwen2\.5:3b|The output must be a single part of speech tag that represents the given word's role in the sentence according to the specified list of tags\.|sentence: She sells seashells by the seashore\., word: by|IN|ok|
|qwen2\.5:3b|The output must be a single part of speech tag that represents the given word's role in the sentence according to the specified list of tags\.|sentence: Wow, that's amazing\!, word: Wow|WRB|ok|
|qwen2\.5:3b|If the given word cannot be accurately tagged using the provided list of part\-of\-speech tags, the output must be the word "Unknown"\.|sentence: The xylophone zxylophone harmonizes\., word: zxylophone|Unknown|ok|
|qwen2\.5:3b|If the given word cannot be accurately tagged using the provided list of part\-of\-speech tags, the output must be the word "Unknown"\.|sentence: He ate the mysterious food item\., word: food|NN|ok|
|qwen2\.5:3b|If the given word cannot be accurately tagged using the provided list of part\-of\-speech tags, the output must be the word "Unknown"\.|sentence: As he qwertyuiop in the room\., word: qwertyuiop|Unknown|ok|
|qwen2\.5:3b|If it is impossible to determine a part of speech for the given word, the output must be the word "CantAnswer"\.|sentence: She spoke eloquently although about nothing in particular\., word: although|IN|ok|
|qwen2\.5:3b|If it is impossible to determine a part of speech for the given word, the output must be the word "CantAnswer"\.|sentence: Despite the conditions, they succeeded\., word: conditions|NN|ok|
|qwen2\.5:3b|If it is impossible to determine a part of speech for the given word, the output must be the word "CantAnswer"\.|sentence: The truth was uncertain, shenative\., word: shenative|Unknown|ok|
|qwen2\.5:3b|The output must not contain any additional text, punctuation, or formatting besides the part of speech tag or the words "Unknown" or "CantAnswer"\.|sentence: He quickly ran to the store\., word: quickly|VB️|err|
|qwen2\.5:3b|The output must not contain any additional text, punctuation, or formatting besides the part of speech tag or the words "Unknown" or "CantAnswer"\.|sentence: This is the best ever\!, word: best|JJ|ok|
|qwen2\.5:3b|The output must not contain any additional text, punctuation, or formatting besides the part of speech tag or the words "Unknown" or "CantAnswer"\.|sentence: Do you have a pen?, word: you|WP|ok|
|qwen2\.5:3b|The output must be multiple parts of speech tags representing different potential roles for the given word according to any possible tags\.|sentence: She booked the show\., word: booked|VBZ|ok|
|qwen2\.5:3b|The output must be multiple parts of speech tags representing different potential roles for the given word according to any possible tags\.|sentence: Play the notes\., word: Play|VB|ok|
|qwen2\.5:3b|The output must be multiple parts of speech tags representing different potential roles for the given word according to any possible tags\.|sentence: The run was tiresome\., word: run|NN|ok|
|qwen2\.5:3b|If the given word can be tagged using any known part\-of\-speech tags, the output must not include the word "Unknown"\.|sentence: She sings beautifully\., word: sings|VBZ|ok|
|qwen2\.5:3b|If the given word can be tagged using any known part\-of\-speech tags, the output must not include the word "Unknown"\.|sentence: It shines brightly\., word: shines|VBZ|ok|
|qwen2\.5:3b|If the given word can be tagged using any known part\-of\-speech tags, the output must not include the word "Unknown"\.|sentence: Light travels fast\., word: travels|VB|ok|
|qwen2\.5:3b|If it is possible to determine a part of speech for the given word, the output must be entirely blank or contain an error message\.|sentence: The cat sleeps peacefully\., word: cat|NN|ok|
|qwen2\.5:3b|If it is possible to determine a part of speech for the given word, the output must be entirely blank or contain an error message\.|sentence: She understood the question\., word: understood|VB|ok|
|qwen2\.5:3b|If it is possible to determine a part of speech for the given word, the output must be entirely blank or contain an error message\.|sentence: He will write a letter\., word: write|VB|ok|
|qwen2\.5:3b|The output must contain additional text, punctuation, or formatting besides the part of speech tag or the words "Unknown" or "CantAnswer"\.|sentence: There is a book on the table\., word: book|NN|ok|
|qwen2\.5:3b|The output must contain additional text, punctuation, or formatting besides the part of speech tag or the words "Unknown" or "CantAnswer"\.|sentence: A quick brown fox?, word: quick|JJ|ok|
|qwen2\.5:3b|The output must contain additional text, punctuation, or formatting besides the part of speech tag or the words "Unknown" or "CantAnswer"\.|sentence: Where did she go?, word: Where|WP|ok|
|qwen2\.5:3b||sentence: The cat sat on the mat\. word: cat|NN|ok|
|qwen2\.5:3b||sentence: She quickly finished her homework\. word: quickly|VB兮|err|
|qwen2\.5:3b||sentence: We will visit Paris next summer\. word: Paris|NN|ok|
|qwen2\.5:3b||sentence: They haven't arrived at the station yet\. word: arrived|VBZ|ok|
|qwen2\.5:3b||sentence: Tom and Jerry are famous cartoon characters\. word: and|CC|ok|
|qwen2\.5:3b||sentence: She is going to the gym\. word: is|VB|ok|
|qwen2\.5:3b||sentence: There were many reasons for the success\. word: There|TO|ok|
|qwen2\.5:3b||sentence: That is the biggest cake I have ever seen\. word: biggest|JJR|ok|
|qwen2\.5:3b||sentence: I can do it alone\. word: can|VB|ok|
|qwen2\.5:3b||sentence: Please hand me the red book\. word: book|NN|ok|
|qwen2\.5:3b||sentence: The baby's toy was missing\. word: baby's|NNP|ok|
|qwen2\.5:3b||sentence: Ouch, that hurts\! word: Ouch|UH|ok|
|qwen2\.5:3b||sentence: If he studies hard, he might pass the test\. word: If|CantAnswer|ok|
|qwen2\.5:3b||sentence: There are 12 eggs in the basket\. word: 12|CD|ok|
|qwen2\.5:3b||sentence: Whoever answers correctly gets a prize\. word: Whoever|WP|ok|
|qwen2\.5:3b||sentence: Happy people are more productive\. word: Happy|JJ|ok|
|qwen2\.5:3b||sentence: The wheels on the bus go round and round\. word: on|IN|ok|
|qwen2\.5:3b||sentence: Jane barely passed the exam this time\. word: barely|VB️DG|err|
|qwen2\.5:3b||sentence: Alas, the show is over\. word: Alas|RB|ok|
|qwen2\.5:3b||sentence: Would you like tea or coffee? word: or|CC|ok|
|qwen2\.5:3b||sentence: Some students forgot their umbrellas\. word: their|their<br>PRP|ok|
|qwen2\.5:3b||sentence: The golden trophy was awarded to the winner\. word: golden|JJ|ok|
|qwen2\.5:3b||sentence: I might have taken the wrong turn\. word: might|VBZ|ok|
|qwen2\.5:3b||sentence: Certainly, that is the correct answer\. word: Certainly|FW|ok|
|llama3\.2:1b|The output must be a single part of speech tag that represents the given word's role in the sentence according to the specified list of tags\.|sentence: The quick brown fox jumps over the lazy dog\., word: fox|CC: adjective<br>JJ: adjective<br>JJS: adjective|err|
|llama3\.2:1b|The output must be a single part of speech tag that represents the given word's role in the sentence according to the specified list of tags\.|sentence: She sells seashells by the seashore\., word: by|Sentence: Unknown<br>Word: by|err|
|llama3\.2:1b|The output must be a single part of speech tag that represents the given word's role in the sentence according to the specified list of tags\.|sentence: Wow, that's amazing\!, word: Wow|WP: Wh\-pronoun<br>WC: Conjunction \(used to connect the two occurrences of 'Wow'\) <br>WU: Interjection \(exclamation\)|err|
|llama3\.2:1b|If the given word cannot be accurately tagged using the provided list of part\-of\-speech tags, the output must be the word "Unknown"\.|sentence: The xylophone zxylophone harmonizes\., word: zxylophone|Part of speech tag for the given word 'zxylophone': CD \(Cardinal number\) <br>The part of speech tags should form a cohesive and grammatically correct sentence\. In this case, the given words have different meanings, so forming a complete sentence with the same parts of speech is not possible\.<br><br>Therefore, I return: CantAnswer|err|
|llama3\.2:1b|If the given word cannot be accurately tagged using the provided list of part\-of\-speech tags, the output must be the word "Unknown"\.|sentence: He ate the mysterious food item\., word: food|For the given sentence and word "food", both verbs "ate" can be tagged as VBD \(Past tense, 3rd person singular present\)\.<br><br>So, the part of speech tag for the word "food" is VB\.|err|
|llama3\.2:1b|If the given word cannot be accurately tagged using the provided list of part\-of\-speech tags, the output must be the word "Unknown"\.|sentence: As he qwertyuiop in the room\., word: qwertyuiop|\*\*Part\-of\-Speech Tags:\*\*<br><br>\* sentence: IN, SYM<br>\* word: qwertyuiop|err|
|llama3\.2:1b|If it is impossible to determine a part of speech for the given word, the output must be the word "CantAnswer"\.|sentence: She spoke eloquently although about nothing in particular\., word: although|Part of Speech Tag:<br><br>\* She: CC<br>\* spoke: VBZ<br>\* eloquently: RB<br>\* although: RRB|err|
|llama3\.2:1b|If it is impossible to determine a part of speech for the given word, the output must be the word "CantAnswer"\.|sentence: Despite the conditions, they succeeded\., word: conditions|Sentence \- NNP \(Proper Noun\)<br>Word   \- conditions <br><br>Both words can be tagged as NNS \(Noun, plural\), so I will return NNS\.|err|
|llama3\.2:1b|If it is impossible to determine a part of speech for the given word, the output must be the word "CantAnswer"\.|sentence: The truth was uncertain, shenative\., word: shenative|Here are the parts of speech for each word:<br><br>\* The: DT \(Determiner\)<br>\* truth: NN \(Noun\)|err|
|llama3\.2:1b|The output must not contain any additional text, punctuation, or formatting besides the part of speech tag or the words "Unknown" or "CantAnswer"\.|sentence: He quickly ran to the store\., word: quickly|Word: quickly <br> POS: VerB \(Verb\)|err|
|llama3\.2:1b|The output must not contain any additional text, punctuation, or formatting besides the part of speech tag or the words "Unknown" or "CantAnswer"\.|sentence: This is the best ever\!, word: best|PART OF SPOC: JJ <br>tagged: best|err|
|llama3\.2:1b|The output must not contain any additional text, punctuation, or formatting besides the part of speech tag or the words "Unknown" or "CantAnswer"\.|sentence: Do you have a pen?, word: you|For the given words:<br><br>\- The word "you" is an INF: Adverb I would tag it as ADJ: Adjective\. So, for the first sentence, I would return ADJ as part of 'ADP: Adverb' but cannot as ADJ is not a proper tag, however  AS adj would be too ambiguous\.<br>\- The word "you" is an INF: Adverb in both sentences\. <br><br>However since we're asked to just provide the tag for each word's part of speech without using their full form, I will return:<br><br>ADJ<br>INF|err|
|llama3\.2:1b|The output must be multiple parts of speech tags representing different potential roles for the given word according to any possible tags\.|sentence: She booked the show\., word: booked|Word: CC: Booking, JJS: Booked, EX: She|err|
|llama3\.2:1b|The output must be multiple parts of speech tags representing different potential roles for the given word according to any possible tags\.|sentence: Play the notes\., word: Play|Part\-of\-speech tag for "Play" is NN\.<br> Part\-of\-speech tag for "notes" is JJR\.|err|
|llama3\.2:1b|The output must be multiple parts of speech tags representing different potential roles for the given word according to any possible tags\.|sentence: The run was tiresome\., word: run|Word: Run<br> Tag: JJ|err|
|llama3\.2:1b|If the given word can be tagged using any known part\-of\-speech tags, the output must not include the word "Unknown"\.|sentence: She sings beautifully\., word: sings|Word: JJR \(Jobbing adjective\)<br><br> Sentence: She sings beautifully\., word: beautiful <br> Sentence: She sings wonderfully\., word: beautifully\.<br> Word: NN \(Proper noun\)|err|
|llama3\.2:1b|If the given word can be tagged using any known part\-of\-speech tags, the output must not include the word "Unknown"\.|sentence: It shines brightly\., word: shines|The tag for the word "shines" in both sentences is NN\.|ok|
|llama3\.2:1b|If the given word can be tagged using any known part\-of\-speech tags, the output must not include the word "Unknown"\.|sentence: Light travels fast\., word: travels|word: travels \( JJR, JJS\)<br>word: travels \( DT, IN\) <br> CantAnswer <br><br>Note: The word 'travels' can also be tagged as MS: Adverb or RB: ADVERB depending on its grammatical position\. However, in the provided list of tag options, I have only listed JJR/JJS for "travels" since it is an adjective\. If you want to include 'adverbial', I will put "ADVERB" under travel instead\.|err|
|llama3\.2:1b|If it is possible to determine a part of speech for the given word, the output must be entirely blank or contain an error message\.|sentence: The cat sleeps peacefully\., word: cat|Word: cat<br>Tag: NNP|ok|
|llama3\.2:1b|If it is possible to determine a part of speech for the given word, the output must be entirely blank or contain an error message\.|sentence: She understood the question\., word: understood|\_tag\_: DT<br><br>\_word\_: understood\_|err|
|llama3\.2:1b|If it is possible to determine a part of speech for the given word, the output must be entirely blank or contain an error message\.|sentence: He will write a letter\., word: write|\* For the first sentence: The word "write" is an : JJ\.<br>\* For the second sentence \(same sentence as above\): The word "write" is an : JJ\.|err|
|llama3\.2:1b|The output must contain additional text, punctuation, or formatting besides the part of speech tag or the words "Unknown" or "CantAnswer"\.|sentence: There is a book on the table\., word: book|Word: CC: Coordinating conjunction \(conjunction\), JJ: Adjective<br><br>Sentence: It is raining outside\. <br>Word: CD: Cardinal number, NN: Noun, singular or mass|err|
|llama3\.2:1b|The output must contain additional text, punctuation, or formatting besides the part of speech tag or the words "Unknown" or "CantAnswer"\.|sentence: A quick brown fox?, word: quick|CC: Coordinating conjunction<br>Tag: ? \(unknown\)|err|
|llama3\.2:1b|The output must contain additional text, punctuation, or formatting besides the part of speech tag or the words "Unknown" or "CantAnswer"\.|sentence: Where did she go?, word: Where|CC: Coordinating conjunction<br>Since the sentence is identical \(same structure and words\) and both instances of "where" are connected, it's a case of homographs\. Coordinating conjunctions join non\- coordinating clauses to a main clause\.<br><br>CantAnswer<br>Both words cannot be tagged with a specific part\-of\-speech tag due to their identical use in different positions\. Symbol|err|
|llama3\.2:1b||sentence: The cat sat on the mat\. word: cat|Word: DD: Determiner \(Determiner\)<br> <br>Sentence tags:<br>\- DT: Determiner \(Det\) \-Determiner<br>\- JJ: Adjective \(Adj\) Adjective<br>\- NNP: Proper noun \(NNP\) , singular, NP: Noun \(NP\)|err|
|llama3\.2:1b||sentence: She quickly finished her homework\. word: quickly|For the given sentence and word "quickly":<br><br>\* The tag is PD \(Pronouns doesn't fit, thus returning PD\)\.<br> To be precise, a more suitable answer would be PL tags for the present participle\.|err|
|llama3\.2:1b||sentence: We will visit Paris next summer\. word: Paris|Tagging the sentences:<br>\- sentence 1: We \(IN\) will \(FW\) visit \(JJR\) Paris \(NN\) next \(DD\) summer \(NN\)\. So, the tagged version is: IN FW JJR NN DD<br>\- sentence 2: We \(IN\) will \(FW\) visit \(JJR\) Paris \(NN\) next \(DD\) summer \(NN\)\. So, the tagged version is: IN FW JJR NN DD|err|
|llama3\.2:1b||sentence: They haven't arrived at the station yet\. word: arrived|JJ <br>JJR: <br>JJS|err|
|llama3\.2:1b||sentence: Tom and Jerry are famous cartoon characters\. word: and|For the first sentence, tag: ADP \(Adposition\) <br>For the second sentence, tag: CC \(Coordinating conjunction\)|err|
|llama3\.2:1b||sentence: She is going to the gym\. word: is|Word: is <br>Tag: RC \(Relational, no grammatical function\)<br><br>Word: is<br>Tag: CC \(Coordinating conjunction\)|err|
|llama3\.2:1b||sentence: There were many reasons for the success\. word: There|\* For: DT \(Determiner\)<br>\* There:<br>     \* This: NNP \(Proper noun, plural, NNPS\)<br>     \* When: FW \(Foreign word\)<br><br>\* Reasons: JJR \(Adjective, comparative, JJS \(Adjective, superlative\)|err|
|llama3\.2:1b||sentence: That is the biggest cake I have ever seen\. word: biggest|Part\-of\-speech tag for "word": NN <br><br>Part\-of\-speech tag for "word": NNS|err|
|llama3\.2:1b||sentence: I can do it alone\. word: can|Word: can<br>\- DD: Determiner \(I\)<br>\- NN: Noun \(can\)|err|
|llama3\.2:1b||sentence: Please hand me the red book\. word: book|Part\-of\-speech tag for "book" is NN \(Noun\)\.|err|
|llama3\.2:1b||sentence: The baby's toy was missing\. word: baby's|Word: baby's<br>Tags: NNS \(2\)|err|
|llama3\.2:1b||sentence: Ouch, that hurts\! word: Ouch|Sentence: Ouch, that hurts\!<br>Word: Ouch<br>Tag: VB<br><br>Sentence: Ouch, that hurts\!<br>Word: Ouch<br>Tag: VB|err|
|llama3\.2:1b||sentence: If he studies hard, he might pass the test\. word: If|CC: Subordinating conjunction|err|
|llama3\.2:1b||sentence: There are 12 eggs in the basket\. word: 12|\*   TT: Titic \(tag for 'Titantic'\)<br>\*   CC: Cor \(correlated\)<br>\*   CT: Toc \(to the cost\)<br>\*   UH: Uhuh \(Interjection\)|err|
|llama3\.2:1b||sentence: Whoever answers correctly gets a prize\. word: Whoever|\* In the sentence "Whoever answers correctly gets a prize," the tagged word is "whoever\."<br><br>Tagged as:Possessive ending|err|
|llama3\.2:1b||sentence: Happy people are more productive\. word: Happy|Here are the parts of speech for each word:<br><br>\- Happy: NN \(NOUN, singular\)<br>\- Happy: JJ \(ADJECTIVE\)|err|
|llama3\.2:1b||sentence: The wheels on the bus go round and round\. word: on|word: on<br>tag: Nouns|err|
|llama3\.2:1b||sentence: Jane barely passed the exam this time\. word: barely|\*\*Part of Speech Tag:\*\*<br>Nouns \(barely\)|err|
|llama3\.2:1b||sentence: Alas, the show is over\. word: Alas|For the given sentence:<br><br>\* The first instance of "Alas" is a noun\.<br>\* The second instance of "Alas" appears to be an interjection \(UH\)\. <br><br>So, I'd return NN and UH as the part of speech tags\.|err|
|llama3\.2:1b||sentence: Would you like tea or coffee? word: or|\* POS: IN<br>\* LS: NNS: \(Note: There are two identical sentences\. The first contains the determiner "or", and the second sentence is identical to the first, thus leaving only the determined part of speech\.\) <br><br>Corrected response:<br>\* IN|err|
|llama3\.2:1b||sentence: Some students forgot their umbrellas\. word: their|The tag for the word "their" in this sentence is PRP$\.|ok|
|llama3\.2:1b||sentence: The golden trophy was awarded to the winner\. word: golden|\* The tag for the word "golden" is NN \(Noun\)\.<br>\* The tag for the word "golden" is PD \(Pronoun\)\.|err|
|llama3\.2:1b||sentence: I might have taken the wrong turn\. word: might|Tag for the word "might": DD: Determiner|err|
|llama3\.2:1b||sentence: Certainly, that is the correct answer\. word: Certainly|DT: Determiner<br>DT: Determiner<br>WW: Wh\-word \(returning "Wh\-"\)|err|

### [intent.txt](./intent.txt)

`````txt
Determine the part of speech for a given word and return just the tag for the word's part of speech.
`````


### [input_spec.txt](./input_spec.txt)

`````txt
The input is a combination of a sentence and a word contained within that sentence.  
The sentence must be a coherent sequence of words forming a declarative, interrogative, imperative, or exclamatory statement.  
The word must be a single, identifiable term from the given sentence.  
The sentence must contain the word which needs to be tagged for its part of speech.  
The input must not contain any special characters or numbers unrelated to typical sentence structure.  
The input must not be an empty string or contain only whitespace.  
The word must be a valid word in the language of the sentence and cannot be a random sequence of characters.  
The input word should be straightforward and not require disambiguation within the context of the sentence provided.  
`````


### [rules.txt](./rules.txt)

`````txt
1: The output must be a single part of speech tag that represents the given word's role in the sentence according to the specified list of tags. 
2: If the given word cannot be accurately tagged using the provided list of part-of-speech tags, the output must be the word "Unknown".
3: If it is impossible to determine a part of speech for the given word, the output must be the word "CantAnswer".
4: The output must not contain any additional text, punctuation, or formatting besides the part of speech tag or the words "Unknown" or "CantAnswer".
`````


### [inverse_rules.txt](./inverse_rules.txt)

`````txt
5: The output must be multiple parts of speech tags representing different potential roles for the given word according to any possible tags.  
6: If the given word can be tagged using any known part-of-speech tags, the output must not include the word "Unknown".  
7: If it is possible to determine a part of speech for the given word, the output must be entirely blank or contain an error message.  
8: The output must contain additional text, punctuation, or formatting besides the part of speech tag or the words "Unknown" or "CantAnswer".
`````


### [tests.csv](./tests.csv)

|testinput|expectedoutput|reasoning|
|-|-|-|
|sentence: The quick brown fox jumps over the lazy dog\., word: fox|NN|The word 'fox' should be tagged as a singular noun as per the list\.|
|sentence: She sells seashells by the seashore\., word: by|IN|The word 'by' functions as a preposition and should be tagged with the corresponding part\-of\-speech tag\.|
|sentence: Wow, that's amazing\!, word: Wow|UH|The word 'Wow' is an interjection and should be tagged accordingly, testing correct single tag output\.|
|sentence: The xylophone zxylophone harmonizes\., word: zxylophone|Unknown|The word 'zxylophone' is not standard and should be tagged as 'Unknown' due to absence of a relevant tag\.|
|sentence: He ate the mysterious food item\., word: food|NN|The test confirms correct tagging as a singular noun, not 'Unknown', due to presence of a valid tag\.|
|sentence: As he qwertyuiop in the room\., word: qwertyuiop|Unknown|The random sequence 'qwertyuiop' does not form a meaningful word, prompting 'Unknown'\.|
|sentence: She spoke eloquently although about nothing in particular\., word: although|CantAnswer|The word 'although' is complex here, making it impossible to determine a clear part of speech, leading to 'CantAnswer'\.|
|sentence: Despite the conditions, they succeeded\., word: conditions|CantAnswer|Multiple interpretations could arise for ‘conditions’, but here testing leads to 'CantAnswer'\.|
|sentence: The truth was uncertain, shenative\., word: shenative|CantAnswer|Using a non\-existent word 'shenative', further tags cannot resolve, resulting in 'CantAnswer'\.|
|sentence: He quickly ran to the store\., word: quickly|RB|Ensures output is solely tag 'RB' with no extra formatting or punctuation\.|
|sentence: This is the best ever\!, word: best|JJS|Validates output is simply 'JJS', testing against unallowed formatting additions\.|
|sentence: Do you have a pen?, word: you|PRP|Output is just 'PRP', checking adherence to the no additional text rule\.|
|sentence: She booked the show\., word: booked|VB VBD VBN|Different roles as 'VB', 'VBD', and 'VBN' are possible, testing for multiple roles\.|
|sentence: Play the notes\., word: Play|VB VBP|Multiple interpretations; the word 'Play' can be 'VB' or 'VBP'\.|
|sentence: The run was tiresome\., word: run|NN VB|Tests correct dual potential roles and tags for the word 'run'\.|
|sentence: She sings beautifully\., word: sings|VBZ|Expected a single valid part of speech tag, ensures 'Unknown' is not falsely used\.|
|sentence: It shines brightly\., word: shines|VBZ|The correct tag 'VBZ' should be used, ensuring 'Unknown' isn't inaccurately applied\.|
|sentence: Light travels fast\., word: travels|VBZ|Verifies proper usage of 'VBZ', guarding against wrongful 'Unknown'\.|
|sentence: The cat sleeps peacefully\., word: cat|NN|Verifies the presence of a part\-of\-speech tag, ensuring outputs are not blank\.|
|sentence: She understood the question\., word: understood|VBD|Tests that an appropriate label like 'VBD' is returned, showing no blank or erroneous output\.|
|sentence: He will write a letter\., word: write|VB|Confirms correct 'VB', eschewing blank or error output, showing rule implication\.|
|sentence: There is a book on the table\., word: book|NN \(identified by software\)|Tests that unwanted text \(annotative or punctuative\) violates the rule\.|
|sentence: A quick brown fox?, word: quick|JJ \- as tagged by tool|Residue text like '\- as tagged by tool' tests adherence by their unwanted presence\.|
|sentence: Where did she go?, word: Where|WRB which is whereatel tags|Examines inclusion of extraneous descriptors which contravene the stipulated rule\.|

### [test_evals.csv](./test_evals.csv)

|rule|model|input|coverage|validity|
|-|-|-|-|-|
|The output must be a single part of speech tag that represents the given word's role in the sentence according to the specified list of tags\.|gpt\-4o\-2024\-08\-06|sentence: The quick brown fox jumps over the lazy dog\., word: fox|err|ok|
|The output must be a single part of speech tag that represents the given word's role in the sentence according to the specified list of tags\.|gpt\-4o\-2024\-08\-06|sentence: She sells seashells by the seashore\., word: by|err|ok|
|The output must be a single part of speech tag that represents the given word's role in the sentence according to the specified list of tags\.|gpt\-4o\-2024\-08\-06|sentence: Wow, that's amazing\!, word: Wow|err|ok|
|If the given word cannot be accurately tagged using the provided list of part\-of\-speech tags, the output must be the word "Unknown"\.|gpt\-4o\-2024\-08\-06|sentence: The xylophone zxylophone harmonizes\., word: zxylophone|ok|err|
|If the given word cannot be accurately tagged using the provided list of part\-of\-speech tags, the output must be the word "Unknown"\.|gpt\-4o\-2024\-08\-06|sentence: He ate the mysterious food item\., word: food|err|ok|
|If the given word cannot be accurately tagged using the provided list of part\-of\-speech tags, the output must be the word "Unknown"\.|gpt\-4o\-2024\-08\-06|sentence: As he qwertyuiop in the room\., word: qwertyuiop|ok|err|
|If it is impossible to determine a part of speech for the given word, the output must be the word "CantAnswer"\.|gpt\-4o\-2024\-08\-06|sentence: She spoke eloquently although about nothing in particular\., word: although|err|ok|
|If it is impossible to determine a part of speech for the given word, the output must be the word "CantAnswer"\.|gpt\-4o\-2024\-08\-06|sentence: Despite the conditions, they succeeded\., word: conditions|err|ok|
|If it is impossible to determine a part of speech for the given word, the output must be the word "CantAnswer"\.|gpt\-4o\-2024\-08\-06|sentence: The truth was uncertain, shenative\., word: shenative|ok|err|
|The output must not contain any additional text, punctuation, or formatting besides the part of speech tag or the words "Unknown" or "CantAnswer"\.|gpt\-4o\-2024\-08\-06|sentence: He quickly ran to the store\., word: quickly|ok|ok|
|The output must not contain any additional text, punctuation, or formatting besides the part of speech tag or the words "Unknown" or "CantAnswer"\.|gpt\-4o\-2024\-08\-06|sentence: This is the best ever\!, word: best|err|ok|
|The output must not contain any additional text, punctuation, or formatting besides the part of speech tag or the words "Unknown" or "CantAnswer"\.|gpt\-4o\-2024\-08\-06|sentence: Do you have a pen?, word: you|err|ok|
|The output must be multiple parts of speech tags representing different potential roles for the given word according to any possible tags\.|gpt\-4o\-2024\-08\-06|sentence: She booked the show\., word: booked|err|ok|
|The output must be multiple parts of speech tags representing different potential roles for the given word according to any possible tags\.|gpt\-4o\-2024\-08\-06|sentence: Play the notes\., word: Play|ok|ok|
|The output must be multiple parts of speech tags representing different potential roles for the given word according to any possible tags\.|gpt\-4o\-2024\-08\-06|sentence: The run was tiresome\., word: run|err|ok|
|If the given word can be tagged using any known part\-of\-speech tags, the output must not include the word "Unknown"\.|gpt\-4o\-2024\-08\-06|sentence: She sings beautifully\., word: sings|ok|ok|
|If the given word can be tagged using any known part\-of\-speech tags, the output must not include the word "Unknown"\.|gpt\-4o\-2024\-08\-06|sentence: It shines brightly\., word: shines|ok|ok|
|If the given word can be tagged using any known part\-of\-speech tags, the output must not include the word "Unknown"\.|gpt\-4o\-2024\-08\-06|sentence: Light travels fast\., word: travels|ok|ok|
|If it is possible to determine a part of speech for the given word, the output must be entirely blank or contain an error message\.|gpt\-4o\-2024\-08\-06|sentence: The cat sleeps peacefully\., word: cat|err|ok|
|If it is possible to determine a part of speech for the given word, the output must be entirely blank or contain an error message\.|gpt\-4o\-2024\-08\-06|sentence: She understood the question\., word: understood|err|ok|
|If it is possible to determine a part of speech for the given word, the output must be entirely blank or contain an error message\.|gpt\-4o\-2024\-08\-06|sentence: He will write a letter\., word: write|ok|ok|
|The output must contain additional text, punctuation, or formatting besides the part of speech tag or the words "Unknown" or "CantAnswer"\.|gpt\-4o\-2024\-08\-06|sentence: There is a book on the table\., word: book|err|ok|
|The output must contain additional text, punctuation, or formatting besides the part of speech tag or the words "Unknown" or "CantAnswer"\.|gpt\-4o\-2024\-08\-06|sentence: A quick brown fox?, word: quick|ok|err|
|The output must contain additional text, punctuation, or formatting besides the part of speech tag or the words "Unknown" or "CantAnswer"\.|gpt\-4o\-2024\-08\-06|sentence: Where did she go?, word: Where|err|ok|

### [baseline_tests.txt](./baseline_tests.txt)

`````txt
sentence: The cat sat on the mat. word: cat
===
sentence: She quickly finished her homework. word: quickly
===
sentence: We will visit Paris next summer. word: Paris
===
sentence: They haven't arrived at the station yet. word: arrived
===
sentence: Tom and Jerry are famous cartoon characters. word: and
===
sentence: She is going to the gym. word: is
===
sentence: There were many reasons for the success. word: There
===
sentence: That is the biggest cake I have ever seen. word: biggest
===
sentence: I can do it alone. word: can
===
sentence: Please hand me the red book. word: book
===
sentence: The baby's toy was missing. word: baby's
===
sentence: Ouch, that hurts! word: Ouch
===
sentence: If he studies hard, he might pass the test. word: If
===
sentence: There are 12 eggs in the basket. word: 12
===
sentence: Whoever answers correctly gets a prize. word: Whoever
===
sentence: Happy people are more productive. word: Happy
===
sentence: The wheels on the bus go round and round. word: on
===
sentence: Jane barely passed the exam this time. word: barely
===
sentence: Alas, the show is over. word: Alas
===
sentence: Would you like tea or coffee? word: or
===
sentence: Some students forgot their umbrellas. word: their
===
sentence: The golden trophy was awarded to the winner. word: golden
===
sentence: I might have taken the wrong turn. word: might
===
sentence: Certainly, that is the correct answer. word: Certainly
`````
