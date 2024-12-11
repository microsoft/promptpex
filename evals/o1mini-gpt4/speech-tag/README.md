## speech-tag ([json](./evals\o1mini-gpt4\speech-tag/report.json))

- 8 rules
- 8 inverse rules
- 96 tests, 48 baseline tests

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


### [intent.txt](./intent.txt)

`````txt
Determine and return the part of speech tag for a specified word in a given sentence.
`````


### [input_spec.txt](./input_spec.txt)

`````txt
The input must consist of a sentence and a word contained within that sentence.
The sentence must be a grammatically correct English sentence.
The word must exactly match a word in the provided sentence.
Both the sentence and the word must be included in a single input string.
The input must not contain any additional information beyond the sentence and the target word.
`````


### [rules.txt](./rules.txt)

`````txt
1: The chatbot must return only a single part-of-speech tag that corresponds to the specified word within the provided sentence.
2: The chatbot must ensure that the returned part-of-speech tag is one of the predefined tags listed in the task description, which include CC for Coordinating conjunction, CD for Cardinal number, DT for Determiner, EX for Existential there, FW for Foreign word, IN for Preposition or subordinating conjunction, JJ for Adjective, JJR for Adjective comparative, JJS for Adjective superlative, LS for List item marker, MD for Modal, NN for Noun singular or mass, NNS for Noun plural, NNP for Proper noun singular, NNPS for Proper noun plural, PDT for Predeterminer, POS for Possessive ending, PRP for Personal pronoun, PRP$ for Possessive pronoun, RB for Adverb, RBR for Adverb comparative, RBS for Adverb superlative, RP for Particle, SYM for Symbol, TO for to, UH for Interjection, VB for Verb base form, VBD for Verb past tense, VBG for Verb gerund or present participle, VBN for Verb past participle, VBP for Verb non-3rd person singular present, VBZ for Verb 3rd person singular present, WDT for Wh-determiner, WP for Wh-pronoun, WP$ for Possessive wh-pronoun, and WRB for Wh-adverb.
3: If the specified word does not correspond to any of the predefined part-of-speech tags listed, the chatbot must return the tag "Unknown".
4: If the chatbot is unable to determine the part of speech for the specified word due to insufficient information or any other reason, it must return "CantAnswer".
5: The chatbot must ensure that its response contains solely the part-of-speech tag or the specified fallback responses ("Unknown" or "CantAnswer") without including any additional text, explanations, or formatting.
6: Each part-of-speech tag returned by the chatbot must exactly match one of the tags provided in the alphabetical list, including the correct casing and abbreviation.
7: The chatbot must not provide multiple tags, descriptions, or any form of extended response beyond the single required part-of-speech tag or the appropriate fallback response.
8: The chatbot must adhere strictly to returning only the part-of-speech tag relevant to the specified word within the given sentence, ensuring clarity and precision in its output.
`````


### [inverse_rules.txt](./inverse_rules.txt)

`````txt
9: The chatbot may return multiple part-of-speech tags that do not correspond to the specified word within the provided sentence.
10: The chatbot may return part-of-speech tags that are not included in the predefined list, regardless of the specified word.
11: If the specified word does not correspond to any of the predefined part-of-speech tags listed, the chatbot may return a tag other than "Unknown".
12: If the chatbot is able to determine the part of speech for the specified word despite insufficient information or other reasons, it must return a definitive tag instead of "CantAnswer".
13: The chatbot may include additional text, explanations, or formatting alongside the part-of-speech tag or fallback responses.
14: Each part-of-speech tag returned by the chatbot may not match one of the tags provided in the alphabetical list, and may have incorrect casing or abbreviation.
15: The chatbot may provide multiple tags, descriptions, or extended responses beyond the single required part-of-speech tag or the appropriate fallback response.
16: The chatbot may return part-of-speech tags irrelevant to the specified word within the given sentence, compromising clarity and precision in its output.
`````


### [tests.csv](./tests.csv)

|testinput|expectedoutput|reasoning|
|-|-|-|
|She enjoys reading books, enjoys|VBZ|The word 'enjoys' is a verb in third person singular present, ensuring only one tag is returned\.|
|Bright sun shines in the sky, sun|NN|The word 'sun' is a singular noun, verifying the software returns a single correct tag\.|
|They quickly ran to catch the bus, ran|VBD|The word 'ran' is past tense verb, confirming single tag output\.|
|The old man walked slowly, walked|VBD|'walked' is a verb, and 'VBD' is among the predefined tags\.|
|Hello, world\! Hello|UH|'Hello' as interjection, mapped to predefined tag 'UH'\.|
|They have two cats, two|CD|'two' is a cardinal number, 'CD' is a predefined tag\.|
|This is a test with the word blorf, blorf|Unknown|'blorf' does not correspond to any predefined tag, expecting 'Unknown'\.|
|I love programming with xyzword, xyzword|Unknown|'xyzword' does not correspond to any predefined tag, expecting 'Unknown'\.|
|The code is 123abc, 123abc|Unknown|'123abc' cannot be tagged with the predefined tags, expecting 'Unknown'\.|
|She waits, waits|CantAnswer|Insufficient context to determine the part of speech for 'waits', expecting 'CantAnswer'\.|
|The word is unik, unik|CantAnswer|Ambiguous word 'unik', cannot determine part of speech, expecting 'CantAnswer'\.|
|They did something, something|CantAnswer|Word 'something' can be multiple parts of speech without context, expecting 'CantAnswer'\.|
|He runs every day, runs|VBZ|Only the tag 'VBZ' should be returned without extra text\.|
|A beautiful sunrise, sunrise|NN|Output should be 'NN' only without explanations or formatting\.|
|Is this possible, possible|JJ|Output should be 'JJ' solely without additional content\.|
|She quickly, quickly|RB|'RB' is exact match, correct casing and abbreviation\.|
|They will come, will|MD|'MD' is exact match from the predefined tags\.|
|I am happy, am|VBP|'VBP' matches predefined tag with correct casing\.|
|Jump high, jump|VB|Only 'VB' should be returned without additional tags or descriptions\.|
|Quickly did, quickly|RB|Only 'RB' is expected with no extra information\.|
|Green leaves, green|JJ|Response should be single 'JJ', no multiple tags or explanations\.|
|The cat sleeps, sleeps|VBZ|'VBZ' accurately tag the verb 'sleeps'\.|
|Bright stars shine, stars|NNS|'NNS' tag correctly for plural noun 'stars'\.|
|She is beautiful, beautiful|JJ|'JJ' correctly tags adjective 'beautiful'\.|
|She sings beautifully, sings|VBZ|'VBZ' is the only tag returned, ensuring no multiple or incorrect tags are provided\.|
|The children play outside, play|VBP|Only 'VBP' tag for 'play' is returned, preventing multiple or irrelevant tags\.|
|Dogs bark loudly, bark|VBP|Ensures only 'VBP' is returned for 'bark', no multiple or unrelated tags\.|
|She walks gracefully, walks|VBZ|'VBZ' tag is returned, avoiding incorrect tags\.|
|They are happy, are|VBP|'VBP' is predefined, preventing undefined tags\.|
|Quietly she left, left|VBD|'VBD' is predefined, confirms only predefined tags are used\.|
|This is a mystery word, blorf|Unknown|'blorf' does not correspond to any predefined tag, expecting 'Unknown' only\.|
|Undefined word usage: xqz, xqz|Unknown|'xqz' is not in predefined tags, should return 'Unknown'\.|
|Random characters: 123abc, 123abc|Unknown|'123abc' cannot be tagged, expecting 'Unknown' as per rule\.|
|She dances gracefully, dances|VBZ|'VBZ' tag is returned, not 'CantAnswer' as it can be determined\.|
|The quick fox, fox|NN|'NN' is returned, ensuring 'CantAnswer' is not used when POS can be determined\.|
|He is happy, happy|JJ|'JJ' tag is returned, confirming a definitive tag instead of 'CantAnswer'\.|
|Run every morning, run|VB|Only 'VB' tag is returned without extra explanations or formatting\.|
|Beautiful flowers, beautiful|JJ|Only 'JJ' is outputted, no additional text or descriptions\.|
|Wait here, wait|VB|Ensures only 'VB' is returned without extra information\.|
|She plays piano, plays|VBZ|Correct 'VBZ' tag is returned, avoiding incorrect tags\.|
|They are happy, are|VBP|'VBP' is correctly cased and abbreviated, preventing errors\.|
|A big house, big|JJ|'JJ' tag is returned with proper casing and abbreviation\.|
|He sings beautifully, sings|VBZ|Only 'VBZ' is returned without multiple tags or descriptions\.|
|Joyfully she runs, runs|VBZ|Ensures only 'VBZ' tag is outputted, no extra information\.|
|Bright lights shine, shine|VBZ|Only 'VBZ' is returned, no additional tags or explanations\.|
|The dog barks loudly, barks|VBZ|Only 'VBZ' related to 'barks' is returned, no irrelevant tags\.|
|She sings a song, sings|VBZ|Only 'VBZ' for 'sings' is returned, maintaining precision\.|
|He writes letters, writes|VBZ|Ensures only 'VBZ' tag for 'writes' is provided, no irrelevant tags\.|

### [test_evals.csv](./test_evals.csv)

|rule|model|input|coverage|validity|
|-|-|-|-|-|
|The chatbot must return only a single part\-of\-speech tag that corresponds to the specified word within the provided sentence\.|gpt\-4o\-2024\-08\-06|She enjoys reading books, enjoys|VBZ|ok|
|The chatbot must return only a single part\-of\-speech tag that corresponds to the specified word within the provided sentence\.|gpt\-4o\-2024\-08\-06|Bright sun shines in the sky, sun|NN|ok|
|The chatbot must return only a single part\-of\-speech tag that corresponds to the specified word within the provided sentence\.|gpt\-4o\-2024\-08\-06|They quickly ran to catch the bus, ran|VBD|ok|
|The chatbot must ensure that the returned part\-of\-speech tag is one of the predefined tags listed in the task description, which include CC for Coordinating conjunction, CD for Cardinal number, DT for Determiner, EX for Existential there, FW for Foreign word, IN for Preposition or subordinating conjunction, JJ for Adjective, JJR for Adjective comparative, JJS for Adjective superlative, LS for List item marker, MD for Modal, NN for Noun singular or mass, NNS for Noun plural, NNP for Proper noun singular, NNPS for Proper noun plural, PDT for Predeterminer, POS for Possessive ending, PRP for Personal pronoun, PRP$ for Possessive pronoun, RB for Adverb, RBR for Adverb comparative, RBS for Adverb superlative, RP for Particle, SYM for Symbol, TO for to, UH for Interjection, VB for Verb base form, VBD for Verb past tense, VBG for Verb gerund or present participle, VBN for Verb past participle, VBP for Verb non\-3rd person singular present, VBZ for Verb 3rd person singular present, WDT for Wh\-determiner, WP for Wh\-pronoun, WP$ for Possessive wh\-pronoun, and WRB for Wh\-adverb\.|gpt\-4o\-2024\-08\-06|The old man walked slowly, walked|VBD|ok|
|The chatbot must ensure that the returned part\-of\-speech tag is one of the predefined tags listed in the task description, which include CC for Coordinating conjunction, CD for Cardinal number, DT for Determiner, EX for Existential there, FW for Foreign word, IN for Preposition or subordinating conjunction, JJ for Adjective, JJR for Adjective comparative, JJS for Adjective superlative, LS for List item marker, MD for Modal, NN for Noun singular or mass, NNS for Noun plural, NNP for Proper noun singular, NNPS for Proper noun plural, PDT for Predeterminer, POS for Possessive ending, PRP for Personal pronoun, PRP$ for Possessive pronoun, RB for Adverb, RBR for Adverb comparative, RBS for Adverb superlative, RP for Particle, SYM for Symbol, TO for to, UH for Interjection, VB for Verb base form, VBD for Verb past tense, VBG for Verb gerund or present participle, VBN for Verb past participle, VBP for Verb non\-3rd person singular present, VBZ for Verb 3rd person singular present, WDT for Wh\-determiner, WP for Wh\-pronoun, WP$ for Possessive wh\-pronoun, and WRB for Wh\-adverb\.|gpt\-4o\-2024\-08\-06|Hello, world\! Hello|UH|ok|
|The chatbot must ensure that the returned part\-of\-speech tag is one of the predefined tags listed in the task description, which include CC for Coordinating conjunction, CD for Cardinal number, DT for Determiner, EX for Existential there, FW for Foreign word, IN for Preposition or subordinating conjunction, JJ for Adjective, JJR for Adjective comparative, JJS for Adjective superlative, LS for List item marker, MD for Modal, NN for Noun singular or mass, NNS for Noun plural, NNP for Proper noun singular, NNPS for Proper noun plural, PDT for Predeterminer, POS for Possessive ending, PRP for Personal pronoun, PRP$ for Possessive pronoun, RB for Adverb, RBR for Adverb comparative, RBS for Adverb superlative, RP for Particle, SYM for Symbol, TO for to, UH for Interjection, VB for Verb base form, VBD for Verb past tense, VBG for Verb gerund or present participle, VBN for Verb past participle, VBP for Verb non\-3rd person singular present, VBZ for Verb 3rd person singular present, WDT for Wh\-determiner, WP for Wh\-pronoun, WP$ for Possessive wh\-pronoun, and WRB for Wh\-adverb\.|gpt\-4o\-2024\-08\-06|They have two cats, two|CD|err|
|If the specified word does not correspond to any of the predefined part\-of\-speech tags listed, the chatbot must return the tag "Unknown"\.|gpt\-4o\-2024\-08\-06|This is a test with the word blorf, blorf|Unknown|ok|
|If the specified word does not correspond to any of the predefined part\-of\-speech tags listed, the chatbot must return the tag "Unknown"\.|gpt\-4o\-2024\-08\-06|I love programming with xyzword, xyzword|Unknown|ok|
|If the specified word does not correspond to any of the predefined part\-of\-speech tags listed, the chatbot must return the tag "Unknown"\.|gpt\-4o\-2024\-08\-06|The code is 123abc, 123abc|NN|err|
|If the chatbot is unable to determine the part of speech for the specified word due to insufficient information or any other reason, it must return "CantAnswer"\.|gpt\-4o\-2024\-08\-06|She waits, waits|VBZ|err|
|If the chatbot is unable to determine the part of speech for the specified word due to insufficient information or any other reason, it must return "CantAnswer"\.|gpt\-4o\-2024\-08\-06|The word is unik, unik|Unknown|err|
|If the chatbot is unable to determine the part of speech for the specified word due to insufficient information or any other reason, it must return "CantAnswer"\.|gpt\-4o\-2024\-08\-06|They did something, something|PRP|err|
|The chatbot must ensure that its response contains solely the part\-of\-speech tag or the specified fallback responses \("Unknown" or "CantAnswer"\) without including any additional text, explanations, or formatting\.|gpt\-4o\-2024\-08\-06|He runs every day, runs|VBZ|ok|
|The chatbot must ensure that its response contains solely the part\-of\-speech tag or the specified fallback responses \("Unknown" or "CantAnswer"\) without including any additional text, explanations, or formatting\.|gpt\-4o\-2024\-08\-06|A beautiful sunrise, sunrise|NN|ok|
|The chatbot must ensure that its response contains solely the part\-of\-speech tag or the specified fallback responses \("Unknown" or "CantAnswer"\) without including any additional text, explanations, or formatting\.|gpt\-4o\-2024\-08\-06|Is this possible, possible|JJ|ok|
|Each part\-of\-speech tag returned by the chatbot must exactly match one of the tags provided in the alphabetical list, including the correct casing and abbreviation\.|gpt\-4o\-2024\-08\-06|She quickly, quickly|RB|err|
|Each part\-of\-speech tag returned by the chatbot must exactly match one of the tags provided in the alphabetical list, including the correct casing and abbreviation\.|gpt\-4o\-2024\-08\-06|They will come, will|MD|ok|
|Each part\-of\-speech tag returned by the chatbot must exactly match one of the tags provided in the alphabetical list, including the correct casing and abbreviation\.|gpt\-4o\-2024\-08\-06|I am happy, am|VBP|ok|
|The chatbot must not provide multiple tags, descriptions, or any form of extended response beyond the single required part\-of\-speech tag or the appropriate fallback response\.|gpt\-4o\-2024\-08\-06|Jump high, jump|VB|err|
|The chatbot must not provide multiple tags, descriptions, or any form of extended response beyond the single required part\-of\-speech tag or the appropriate fallback response\.|gpt\-4o\-2024\-08\-06|Quickly did, quickly|RB|err|
|The chatbot must not provide multiple tags, descriptions, or any form of extended response beyond the single required part\-of\-speech tag or the appropriate fallback response\.|gpt\-4o\-2024\-08\-06|Green leaves, green|JJ|err|
|The chatbot must adhere strictly to returning only the part\-of\-speech tag relevant to the specified word within the given sentence, ensuring clarity and precision in its output\.|gpt\-4o\-2024\-08\-06|The cat sleeps, sleeps|VBZ|err|
|The chatbot must adhere strictly to returning only the part\-of\-speech tag relevant to the specified word within the given sentence, ensuring clarity and precision in its output\.|gpt\-4o\-2024\-08\-06|Bright stars shine, stars|NNS|ok|
|The chatbot must adhere strictly to returning only the part\-of\-speech tag relevant to the specified word within the given sentence, ensuring clarity and precision in its output\.|gpt\-4o\-2024\-08\-06|She is beautiful, beautiful|JJ|err|
|The chatbot may return multiple part\-of\-speech tags that do not correspond to the specified word within the provided sentence\.|gpt\-4o\-2024\-08\-06|She sings beautifully, sings|VBZ|ok|
|The chatbot may return multiple part\-of\-speech tags that do not correspond to the specified word within the provided sentence\.|gpt\-4o\-2024\-08\-06|The children play outside, play|VB|ok|
|The chatbot may return multiple part\-of\-speech tags that do not correspond to the specified word within the provided sentence\.|gpt\-4o\-2024\-08\-06|Dogs bark loudly, bark|VB|ok|
|The chatbot may return part\-of\-speech tags that are not included in the predefined list, regardless of the specified word\.|gpt\-4o\-2024\-08\-06|She walks gracefully, walks|VBZ|ok|
|The chatbot may return part\-of\-speech tags that are not included in the predefined list, regardless of the specified word\.|gpt\-4o\-2024\-08\-06|They are happy, are|VBP|ok|
|The chatbot may return part\-of\-speech tags that are not included in the predefined list, regardless of the specified word\.|gpt\-4o\-2024\-08\-06|Quietly she left, left|VBD|ok|
|If the specified word does not correspond to any of the predefined part\-of\-speech tags listed, the chatbot may return a tag other than "Unknown"\.|gpt\-4o\-2024\-08\-06|This is a mystery word, blorf|Unknown|err|
|If the specified word does not correspond to any of the predefined part\-of\-speech tags listed, the chatbot may return a tag other than "Unknown"\.|gpt\-4o\-2024\-08\-06|Undefined word usage: xqz, xqz|Unknown|err|
|If the specified word does not correspond to any of the predefined part\-of\-speech tags listed, the chatbot may return a tag other than "Unknown"\.|gpt\-4o\-2024\-08\-06|Random characters: 123abc, 123abc|Unknown|err|
|If the chatbot is able to determine the part of speech for the specified word despite insufficient information or other reasons, it must return a definitive tag instead of "CantAnswer"\.|gpt\-4o\-2024\-08\-06|She dances gracefully, dances|VBZ|ok|
|If the chatbot is able to determine the part of speech for the specified word despite insufficient information or other reasons, it must return a definitive tag instead of "CantAnswer"\.|gpt\-4o\-2024\-08\-06|The quick fox, fox|NN|err|
|If the chatbot is able to determine the part of speech for the specified word despite insufficient information or other reasons, it must return a definitive tag instead of "CantAnswer"\.|gpt\-4o\-2024\-08\-06|He is happy, happy|CantAnswer|ok|
|The chatbot may include additional text, explanations, or formatting alongside the part\-of\-speech tag or fallback responses\.|gpt\-4o\-2024\-08\-06|Run every morning, run|VB|ok|
|The chatbot may include additional text, explanations, or formatting alongside the part\-of\-speech tag or fallback responses\.|gpt\-4o\-2024\-08\-06|Beautiful flowers, beautiful|JJ|err|
|The chatbot may include additional text, explanations, or formatting alongside the part\-of\-speech tag or fallback responses\.|gpt\-4o\-2024\-08\-06|Wait here, wait|VB|ok|
|Each part\-of\-speech tag returned by the chatbot may not match one of the tags provided in the alphabetical list, and may have incorrect casing or abbreviation\.|gpt\-4o\-2024\-08\-06|She plays piano, plays|VBZ|ok|
|The chatbot may return part\-of\-speech tags that are not included in the predefined list, regardless of the specified word\.|gpt\-4o\-2024\-08\-06|They are happy, are|VBP|ok|
|Each part\-of\-speech tag returned by the chatbot may not match one of the tags provided in the alphabetical list, and may have incorrect casing or abbreviation\.|gpt\-4o\-2024\-08\-06|A big house, big|JJ|ok|
|The chatbot may provide multiple tags, descriptions, or extended responses beyond the single required part\-of\-speech tag or the appropriate fallback response\.|gpt\-4o\-2024\-08\-06|He sings beautifully, sings|VBZ|ok|
|The chatbot may provide multiple tags, descriptions, or extended responses beyond the single required part\-of\-speech tag or the appropriate fallback response\.|gpt\-4o\-2024\-08\-06|Joyfully she runs, runs|RB|err|
|The chatbot may provide multiple tags, descriptions, or extended responses beyond the single required part\-of\-speech tag or the appropriate fallback response\.|gpt\-4o\-2024\-08\-06|Bright lights shine, shine|VB|ok|
|The chatbot may return part\-of\-speech tags irrelevant to the specified word within the given sentence, compromising clarity and precision in its output\.|gpt\-4o\-2024\-08\-06|The dog barks loudly, barks|VBZ|ok|
|The chatbot may return part\-of\-speech tags irrelevant to the specified word within the given sentence, compromising clarity and precision in its output\.|gpt\-4o\-2024\-08\-06|She sings a song, sings|VBZ|ok|
|The chatbot may return part\-of\-speech tags irrelevant to the specified word within the given sentence, compromising clarity and precision in its output\.|gpt\-4o\-2024\-08\-06|He writes letters, writes|VBZ|ok|

### [baseline_tests.txt](./baseline_tests.txt)

`````txt
sentence: "She sells seashells by the seashore." word: "sells"
===
sentence: "I have 2 cats and 3 dogs." word: "2"
===
sentence: "The quick brown fox jumps over the lazy dog." word: "The"
===
sentence: "There is a solution to every problem." word: "There"
===
sentence: "Bonjour, comment allez-vous?" word: "Bonjour"
===
sentence: "She walked through the park." word: "through"
===
sentence: "The big elephant never forgets." word: "big"
===
sentence: "She is better than me." word: "better"
===
sentence: "This is the best day ever." word: "best"
===
sentence: "1. First item on the list." word: "1."
===
sentence: "Can you help me?" word: "Can"
===
sentence: "He is a strong leader." word: "leader"
===
sentence: "They have three apples." word: "three"
===
sentence: "John is coming to the party." word: "John"
===
sentence: "The children are playing with toys." word: "children"
===
sentence: "She owns a beautiful house." word: "a"
===
sentence: "He doesn't like spinach." word: "doesn't"
===
sentence: "Wow! That was amazing." word: "Wow!"
===
sentence: "It's raining heavily outside." word: "heavily"
===
sentence: "He arrived after the meeting." word: "after"
===
sentence: "She gave him a gift." word: "gave"
===
sentence: "Please enter 'admin' to continue." word: "'admin'"
===
sentence: "To be or not to be." word: "To"
===
sentence: "What is your name?" word: "What"
===
sentence: "Whose book is this?" word: "Whose"
===
sentence: "I quickly ran to the store." word: "quickly"
===
sentence: "He plans to visit tomorrow." word: "tomorrow"
===
sentence: "She gave her book to me." word: "to"
===
sentence: "He is an amazing athlete." word: "amazing"
===
sentence: "She has X-ray vision." word: "X-ray"
===
sentence: "He shrugged and walked away." word: "shrugged"
===
sentence: "The price is $100." word: "$100"
===
sentence: "Hello there!" word: "Hello"
===
sentence: "They are singing beautifully." word: "beautifully"
===
sentence: "I cannot believe it." word: "cannot"
===
sentence: "Are you coming tonight?" word: "Are"
===
sentence: "She writes with a pen." word: "pen"
===
sentence: "This is John's book." word: "John's"
===
sentence: "He is studying for exams." word: "studying"
===
sentence: "She is going to the market." word: "is"
===
sentence: "We will meet at noon." word: "noon"
===
sentence: "I think, therefore I am." word: "therefore"
===
sentence: "It's been a long day." word: "been"
===
sentence: "They are going to win." word: "win"
===
sentence: "He never lies." word: "never"
===
sentence: "She laughed out loud." word: "out"
===
sentence: "The sun rises in the east." word: "east"
===
sentence: "UnknownWord appears here." word: "UnknownWord"
`````
