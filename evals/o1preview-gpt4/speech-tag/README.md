## speech-tag ([json](./evals\o1preview-gpt4\speech-tag/report.json))

- 9 rules
- 9 inverse rules
- 112 tests, 58 baseline tests

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
Determine the part of speech tag for a given word in a sentence and return only the tag.
`````


### [input_spec.txt](./input_spec.txt)

`````txt
The input consists of a sentence and a word from that sentence.
The sentence can be of any length.
The sentence can contain any combination of words, numbers, symbols, or foreign words.
The word must be a word present in the sentence.
The word can be any word, regardless of its characteristics.
`````


### [rules.txt](./rules.txt)

`````txt
1: The output must be exactly one of the provided part-of-speech tags, "Unknown", or "CantAnswer", and must not include any additional text.
2: A "part-of-speech tag" is a specific abbreviation representing the grammatical role of a word in a sentence, as defined in the provided list.
3: If the given word in the context of the provided sentence corresponds to one of the part-of-speech categories from the list, the output must be the exact tag associated with that category.
4: If the given word cannot be assigned any of the provided part-of-speech tags in the context of the provided sentence, the output must be exactly "Unknown" without any additional characters or text.
5: If it is impossible to determine the part-of-speech tag for the given word in the context of the provided sentence, the output must be exactly "CantAnswer" without any additional characters or text.
6: The output must be case-sensitive and match exactly the capitalization of the tags or specified words as provided.
7: The output must not contain any leading or trailing whitespace or blank lines.
8: The output must not include any explanations, definitions, examples, or additional information beyond the required tag or specified word.
9: The list of available part-of-speech tags is as follows: CC: Coordinating conjunction, CD: Cardinal number, DT: Determiner, EX: Existential there, FW: Foreign word, IN: Preposition or subordinating conjunction, JJ: Adjective, JJR: Adjective, comparative, JJS: Adjective, superlative, LS: List item marker, MD: Modal, NN: Noun, singular or mass, NNS: Noun, plural, NNP: Proper noun, singular, NNPS: Proper noun, plural, PDT: Predeterminer, POS: Possessive ending, PRP: Personal pronoun, PRP$: Possessive pronoun, RB: Adverb, RBR: Adverb, comparative, RBS: Adverb, superlative, RP: Particle, SYM: Symbol, TO: to, UH: Interjection, VB: Verb, base form, VBD: Verb, past tense, VBG: Verb, gerund or present participle, VBN: Verb, past participle, VBP: Verb, non-3rd person singular present, VBZ: Verb, 3rd person singular present, WDT: Wh-determiner, WP: Wh-pronoun, WP$: Possessive wh-pronoun, WRB: Wh-adverb.
`````


### [inverse_rules.txt](./inverse_rules.txt)

`````txt
10: The output may include additional text and does not need to be exactly one of the provided part-of-speech tags, "Unknown", or "CantAnswer".
11: A "part-of-speech tag" is not restricted to the specific abbreviations defined in the provided list.
12: Even if the given word corresponds to one of the part-of-speech categories from the list, the output does not need to be the exact tag associated with that category.
13: If the given word cannot be assigned any of the provided part-of-speech tags, the output does not need to be exactly "Unknown".
14: If it is impossible to determine the part-of-speech tag, the output does not need to be exactly "CantAnswer".
15: The output does not need to be case-sensitive or match exactly the capitalization of the tags or specified words as provided.
16: The output may contain leading or trailing whitespace or blank lines.
17: The output may include explanations, definitions, examples, or additional information beyond the required tag or specified word.
18: The list of available part-of-speech tags is not limited to those provided and may include additional tags.
`````


### [tests.csv](./tests.csv)

|testinput|expectedoutput|reasoning|
|-|-|-|
|Sentence: 'She runs every morning\.' Word: 'runs'|VBZ|The word 'runs' is a third\-person singular present verb, tagged as 'VBZ'\. This test ensures the software outputs only the tag without additional text, adhering to Rule 1\.|
|Sentence: 'They have many 'qwerty' devices\.' Word: 'qwerty'|Unknown|The word 'qwerty' doesn't correspond to any provided POS tag; the software should output 'Unknown' exactly, per Rule 1\.|
|Sentence: 'He mentioned 'xyzzy' in the conversation\.' Word: 'xyzzy'|CantAnswer|It's impossible to assign a POS tag to 'xyzzy'; the expected output is 'CantAnswer'\. This tests that the software outputs only 'CantAnswer' without additional text, following Rule 1\.|
|Sentence: 'He is an intelligent person\.' Word: 'intelligent'|JJ|The word 'intelligent' is an adjective, tagged as 'JJ'\. This ensures that only specified tags are accepted, per Rule 2\.|
|Sentence: 'They went to multiple concerts\.' Word: 'concerts'|NNS|The word 'concerts' is a plural noun, tagged as 'NNS'\. This test confirms the software uses tags from the provided list, adhering to Rule 2\.|
|Sentence: 'London is a bustling city\.' Word: 'London'|NNP|The word 'London' is a proper noun, singular, tagged as 'NNP'\. This ensures only specified tags are used, following Rule 2\.|
|Sentence: 'He is happier today\.' Word: 'happier'|JJR|The word 'happier' is a comparative adjective, tagged as 'JJR'\. This tests that the correct tag is used, adhering to Rule 3\.|
|Sentence: 'They are playing in the park\.' Word: 'playing'|VBG|The word 'playing' is a present participle verb, tagged as 'VBG'\. This ensures the exact tag is used, following Rule 3\.|
|Sentence: 'Please lend me your book\.' Word: 'your'|PRP$|The word 'your' is a possessive pronoun, tagged as 'PRP$'\. This tests that the exact associated tag is returned, adhering to Rule 3\.|
|Sentence: 'The quick brown fox jumps over the lazy dog blork\.' Word: 'blork'|Unknown|The word 'blork' cannot be assigned any provided POS tag; the software should output 'Unknown' exactly, per Rule 4\.|
|Sentence: 'She used 'asdfgh' in her essay\.' Word: 'asdfgh'|Unknown|The word 'asdfgh' doesn't match any POS tag; this ensures the software outputs 'Unknown', following Rule 4\.|
|Sentence: 'He found the artifact 'Qwertz' in the ruins\.' Word: 'Qwertz'|Unknown|The word 'Qwertz' cannot be tagged with any provided POS tag; the expected output is 'Unknown', adhering to Rule 4\.|
|Sentence: 'The old man the boat\.' Word: 'man'|CantAnswer|In this sentence, 'man' could be a verb or noun; it's impossible to determine the POS without more context, so 'CantAnswer' is expected, per Rule 5\.|
|Sentence: 'Time flies like an arrow; fruit flies like a banana\.' Word: 'flies'|CantAnswer|The word 'flies' is ambiguous between noun and verb; the software should output 'CantAnswer', following Rule 5\.|
|Sentence: 'She saw her duck\.' Word: 'duck'|CantAnswer|The word 'duck' can be a noun or verb here; it's impossible to determine without additional context, so 'CantAnswer' is expected, per Rule 5\.|
|Sentence: 'He will go to the market\.' Word: 'He'|PRP|The word 'He' is a pronoun, tagged as 'PRP'\. This tests that the output is case\-sensitive, adhering to Rule 6\.|
|Sentence: 'She had many dreams\.' Word: 'had'|VBD|The word 'had' is a past tense verb, tagged as 'VBD'\. This ensures the output matches the capitalization exactly, following Rule 6\.|
|Sentence: 'I love to read\.' Word: 'to'|TO|The word 'to' is tagged as 'TO'\. This test ensures the output is case\-sensitive and matches exactly, adhering to Rule 6\.|
|Sentence: 'They are running fast\.' Word: 'running'|VBG|The word 'running' is tagged as 'VBG'\. This test checks there's no leading/trailing whitespace in the output, following Rule 7\.|
|Sentence: 'She is a teacher\.' Word: 'teacher'|NN|The word 'teacher' is tagged as 'NN'\. This ensures the output has no extra spaces, adhering to Rule 7\.|
|Sentence: 'Can you help me?' Word: 'me'|PRP|The word 'me' is tagged as 'PRP'\. This tests that the output doesn't contain blank lines or spaces, following Rule 7\.|
|Sentence: 'They happily agreed\.' Word: 'happily'|RB|The word 'happily' is an adverb, tagged as 'RB'\. This ensures no additional information is included in the output, adhering to Rule 8\.|
|Sentence: 'That is an unusual sight\.' Word: 'unusual'|JJ|The word 'unusual' is an adjective, tagged as 'JJ'\. This test checks that only the tag is output, following Rule 8\.|
|Sentence: 'She might come later\.' Word: 'might'|MD|The word 'might' is a modal verb, tagged as 'MD'\. This ensures no explanations are included, adhering to Rule 8\.|
|Sentence: 'He bought a new car\.' Word: 'car'|NN|The word 'car' is tagged as 'NN', which is in the provided list\. This confirms only specified tags are used, following Rule 9\.|
|Sentence: 'She is reading a book\.' Word: 'reading'|VBG|The word 'reading' is tagged as 'VBG'\. This ensures the use of tags from the list, adhering to Rule 9\.|
|Sentence: 'He said 'Bonjour' to them\.' Word: 'Bonjour'|FW|The word 'Bonjour' is a foreign word, tagged as 'FW'\. This confirms only the provided tags are used, following Rule 9\.|
|Sentence: 'They won easily\.' Word: 'won'|VBD|The software should output 'VBD' without additional text, ensuring it doesn't include extra output despite Rule 10 stating it may\.|
|Sentence: 'He will arrive soon\.' Word: 'arrive'|VB|The software should output 'VB' only, not including extra text, confirming it doesn't follow Rule 10\.|
|Sentence: 'Wow\! That was amazing\!' Word: 'Wow'|UH|The software should output 'UH' without extra text, ensuring it doesn't adhere to Rule 10\.|
|Sentence: 'He discussed the plan\.' Word: 'discussed'|VBD|The software should output 'VBD', using only tags from the provided list, not adhering to Rule 11\.|
|Sentence: 'She has an appointment\.' Word: 'appointment'|NN|The software should output 'NN', confirming it doesn't use tags outside the list, contrary to Rule 11\.|
|Sentence: 'They ended the meeting early\.' Word: 'ended'|VBD|The software uses 'VBD' from the list, ensuring it doesn't follow Rule 11\.|
|Sentence: 'She is the best player\.' Word: 'best'|JJS|The software should output 'JJS' exactly, not any other tag, ensuring it doesn't follow Rule 12\.|
|Sentence: 'He runs faster than you\.' Word: 'faster'|JJR|The word 'faster' is tagged as 'JJR'\. This ensures the exact tag is returned, not adhering to Rule 12\.|
|Sentence: 'They arrived early\.' Word: 'early'|RB|The software should output 'RB' only, not deviating from the exact tag, contrary to Rule 12\.|
|Sentence: 'She found the 'blargh' in the cave\.' Word: 'blargh'|Unknown|The software should output 'Unknown' exactly, not following Rule 13 which allows otherwise\.|
|Sentence: 'He mentioned 'snorfblat' in his speech\.' Word: 'snorfblat'|Unknown|The word can't be tagged; the software should output 'Unknown', ensuring it doesn't adhere to Rule 13\.|
|Sentence: 'They discovered a 'zibble' in the forest\.' Word: 'zibble'|Unknown|The software outputs 'Unknown', not deviating as per Rule 13\.|
|Sentence: 'I can't decide whether to desert or not\.' Word: 'desert'|CantAnswer|Due to ambiguity, the software should output 'CantAnswer', not following Rule 14\.|
|Sentence: 'She left him her book\.' Word: 'left'|CantAnswer|It's unclear if 'left' is a verb or adjective here; the software should output 'CantAnswer', contrary to Rule 14\.|
|Sentence: 'He saw the duck\.' Word: 'duck'|CantAnswer|The word 'duck' can be a noun or verb; the software should output 'CantAnswer', not adhering to Rule 14\.|
|Sentence: 'They will win\.' Word: 'win'|VB|The software outputs 'VB' with correct capitalization, ensuring it doesn't follow Rule 15\.|
|Sentence: 'She gave me a gift\.' Word: 'gave'|VBD|The software outputs 'VBD', matching case exactly, contrary to Rule 15\.|
|Sentence: 'I love reading books\.' Word: 'books'|NNS|The software outputs 'NNS' with correct case, not adhering to Rule 15\.|
|Sentence: 'She laughed loudly\.' Word: 'laughed'|VBD|The software outputs 'VBD' without extra spaces, ensuring it doesn't follow Rule 16\.|
|Sentence: 'He writes daily\.' Word: 'writes'|VBZ|The software outputs 'VBZ' without leading/trailing whitespace, contrary to Rule 16\.|
|Sentence: 'They enjoy swimming\.' Word: 'swimming'|VBG|The software outputs 'VBG' without blank lines, not adhering to Rule 16\.|
|Sentence: 'It is raining heavily\.' Word: 'heavily'|RB|The software outputs 'RB' only, without explanations, ensuring it doesn't follow Rule 17\.|
|Sentence: 'She sings beautifully\.' Word: 'beautifully'|RB|The software outputs 'RB' without additional info, contrary to Rule 17\.|
|Sentence: 'He solved the problem easily\.' Word: 'easily'|RB|The software outputs 'RB' only, not adhering to Rule 17\.|
|Sentence: 'She will be arriving soon\.' Word: 'arriving'|VBG|The software uses 'VBG' from the provided list, ensuring it doesn't follow Rule 18\.|
|Sentence: 'They need to analyze the data\.' Word: 'analyze'|VB|The software outputs 'VB', not introducing new tags, contrary to Rule 18\.|
|Sentence: 'He is an exceptional individual\.' Word: 'exceptional'|JJ|The software uses 'JJ' from the list, not adhering to Rule 18\.|

### [test_evals.csv](./test_evals.csv)

|rule|model|input|coverage|validity|
|-|-|-|-|-|
|The output must be exactly one of the provided part\-of\-speech tags, "Unknown", or "CantAnswer", and must not include any additional text\.|gpt\-4o\-2024\-08\-06|Sentence: 'She runs every morning\.' Word: 'runs'|VBZ|ok|
|The output must be exactly one of the provided part\-of\-speech tags, "Unknown", or "CantAnswer", and must not include any additional text\.|gpt\-4o\-2024\-08\-06|Sentence: 'They have many 'qwerty' devices\.' Word: 'qwerty'|FW|ok|
|The output must be exactly one of the provided part\-of\-speech tags, "Unknown", or "CantAnswer", and must not include any additional text\.|gpt\-4o\-2024\-08\-06|Sentence: 'He mentioned 'xyzzy' in the conversation\.' Word: 'xyzzy'|FW|ok|
|A "part\-of\-speech tag" is a specific abbreviation representing the grammatical role of a word in a sentence, as defined in the provided list\.|gpt\-4o\-2024\-08\-06|Sentence: 'He is an intelligent person\.' Word: 'intelligent'|JJ|ok|
|A "part\-of\-speech tag" is a specific abbreviation representing the grammatical role of a word in a sentence, as defined in the provided list\.|gpt\-4o\-2024\-08\-06|Sentence: 'They went to multiple concerts\.' Word: 'concerts'|NNS|ok|
|A "part\-of\-speech tag" is a specific abbreviation representing the grammatical role of a word in a sentence, as defined in the provided list\.|gpt\-4o\-2024\-08\-06|Sentence: 'London is a bustling city\.' Word: 'London'|NNP|ok|
|If the given word in the context of the provided sentence corresponds to one of the part\-of\-speech categories from the list, the output must be the exact tag associated with that category\.|gpt\-4o\-2024\-08\-06|Sentence: 'He is happier today\.' Word: 'happier'|JJR|ok|
|If the given word in the context of the provided sentence corresponds to one of the part\-of\-speech categories from the list, the output must be the exact tag associated with that category\.|gpt\-4o\-2024\-08\-06|Sentence: 'They are playing in the park\.' Word: 'playing'|VBG|ok|
|If the given word in the context of the provided sentence corresponds to one of the part\-of\-speech categories from the list, the output must be the exact tag associated with that category\.|gpt\-4o\-2024\-08\-06|Sentence: 'Please lend me your book\.' Word: 'your'|PRP$|ok|
|If the given word cannot be assigned any of the provided part\-of\-speech tags in the context of the provided sentence, the output must be exactly "Unknown" without any additional characters or text\.|gpt\-4o\-2024\-08\-06|Sentence: 'The quick brown fox jumps over the lazy dog blork\.' Word: 'blork'|Unknown|ok|
|If the given word cannot be assigned any of the provided part\-of\-speech tags in the context of the provided sentence, the output must be exactly "Unknown" without any additional characters or text\.|gpt\-4o\-2024\-08\-06|Sentence: 'She used 'asdfgh' in her essay\.' Word: 'asdfgh'|FW|ok|
|If the given word cannot be assigned any of the provided part\-of\-speech tags in the context of the provided sentence, the output must be exactly "Unknown" without any additional characters or text\.|gpt\-4o\-2024\-08\-06|Sentence: 'He found the artifact 'Qwertz' in the ruins\.' Word: 'Qwertz'|NNP|ok|
|If it is impossible to determine the part\-of\-speech tag for the given word in the context of the provided sentence, the output must be exactly "CantAnswer" without any additional characters or text\.|gpt\-4o\-2024\-08\-06|Sentence: 'The old man the boat\.' Word: 'man'|VB|ok|
|If it is impossible to determine the part\-of\-speech tag for the given word in the context of the provided sentence, the output must be exactly "CantAnswer" without any additional characters or text\.|gpt\-4o\-2024\-08\-06|Sentence: 'Time flies like an arrow; fruit flies like a banana\.' Word: 'flies'|VBZ|ok|
|If it is impossible to determine the part\-of\-speech tag for the given word in the context of the provided sentence, the output must be exactly "CantAnswer" without any additional characters or text\.|gpt\-4o\-2024\-08\-06|Sentence: 'She saw her duck\.' Word: 'duck'|VB|ok|
|The output must be case\-sensitive and match exactly the capitalization of the tags or specified words as provided\.|gpt\-4o\-2024\-08\-06|Sentence: 'He will go to the market\.' Word: 'He'|PRP|ok|
|The output must be case\-sensitive and match exactly the capitalization of the tags or specified words as provided\.|gpt\-4o\-2024\-08\-06|Sentence: 'She had many dreams\.' Word: 'had'|VBD|ok|
|The output must be case\-sensitive and match exactly the capitalization of the tags or specified words as provided\.|gpt\-4o\-2024\-08\-06|Sentence: 'I love to read\.' Word: 'to'|TO|ok|
|The output must not contain any leading or trailing whitespace or blank lines\.|gpt\-4o\-2024\-08\-06|Sentence: 'They are running fast\.' Word: 'running'|VBG|ok|
|The output must not contain any leading or trailing whitespace or blank lines\.|gpt\-4o\-2024\-08\-06|Sentence: 'She is a teacher\.' Word: 'teacher'|NN|ok|
|The output must not contain any leading or trailing whitespace or blank lines\.|gpt\-4o\-2024\-08\-06|Sentence: 'Can you help me?' Word: 'me'|PRP|ok|
|The output must not include any explanations, definitions, examples, or additional information beyond the required tag or specified word\.|gpt\-4o\-2024\-08\-06|Sentence: 'They happily agreed\.' Word: 'happily'|RB|ok|
|The output must not include any explanations, definitions, examples, or additional information beyond the required tag or specified word\.|gpt\-4o\-2024\-08\-06|Sentence: 'That is an unusual sight\.' Word: 'unusual'|JJ|ok|
|The output must not include any explanations, definitions, examples, or additional information beyond the required tag or specified word\.|gpt\-4o\-2024\-08\-06|Sentence: 'She might come later\.' Word: 'might'|MD|ok|
|The list of available part\-of\-speech tags is as follows: CC: Coordinating conjunction, CD: Cardinal number, DT: Determiner, EX: Existential there, FW: Foreign word, IN: Preposition or subordinating conjunction, JJ: Adjective, JJR: Adjective, comparative, JJS: Adjective, superlative, LS: List item marker, MD: Modal, NN: Noun, singular or mass, NNS: Noun, plural, NNP: Proper noun, singular, NNPS: Proper noun, plural, PDT: Predeterminer, POS: Possessive ending, PRP: Personal pronoun, PRP$: Possessive pronoun, RB: Adverb, RBR: Adverb, comparative, RBS: Adverb, superlative, RP: Particle, SYM: Symbol, TO: to, UH: Interjection, VB: Verb, base form, VBD: Verb, past tense, VBG: Verb, gerund or present participle, VBN: Verb, past participle, VBP: Verb, non\-3rd person singular present, VBZ: Verb, 3rd person singular present, WDT: Wh\-determiner, WP: Wh\-pronoun, WP$: Possessive wh\-pronoun, WRB: Wh\-adverb\.|gpt\-4o\-2024\-08\-06|Sentence: 'He bought a new car\.' Word: 'car'|NN|ok|
|The list of available part\-of\-speech tags is as follows: CC: Coordinating conjunction, CD: Cardinal number, DT: Determiner, EX: Existential there, FW: Foreign word, IN: Preposition or subordinating conjunction, JJ: Adjective, JJR: Adjective, comparative, JJS: Adjective, superlative, LS: List item marker, MD: Modal, NN: Noun, singular or mass, NNS: Noun, plural, NNP: Proper noun, singular, NNPS: Proper noun, plural, PDT: Predeterminer, POS: Possessive ending, PRP: Personal pronoun, PRP$: Possessive pronoun, RB: Adverb, RBR: Adverb, comparative, RBS: Adverb, superlative, RP: Particle, SYM: Symbol, TO: to, UH: Interjection, VB: Verb, base form, VBD: Verb, past tense, VBG: Verb, gerund or present participle, VBN: Verb, past participle, VBP: Verb, non\-3rd person singular present, VBZ: Verb, 3rd person singular present, WDT: Wh\-determiner, WP: Wh\-pronoun, WP$: Possessive wh\-pronoun, WRB: Wh\-adverb\.|gpt\-4o\-2024\-08\-06|Sentence: 'She is reading a book\.' Word: 'reading'|VBG|ok|
|The list of available part\-of\-speech tags is as follows: CC: Coordinating conjunction, CD: Cardinal number, DT: Determiner, EX: Existential there, FW: Foreign word, IN: Preposition or subordinating conjunction, JJ: Adjective, JJR: Adjective, comparative, JJS: Adjective, superlative, LS: List item marker, MD: Modal, NN: Noun, singular or mass, NNS: Noun, plural, NNP: Proper noun, singular, NNPS: Proper noun, plural, PDT: Predeterminer, POS: Possessive ending, PRP: Personal pronoun, PRP$: Possessive pronoun, RB: Adverb, RBR: Adverb, comparative, RBS: Adverb, superlative, RP: Particle, SYM: Symbol, TO: to, UH: Interjection, VB: Verb, base form, VBD: Verb, past tense, VBG: Verb, gerund or present participle, VBN: Verb, past participle, VBP: Verb, non\-3rd person singular present, VBZ: Verb, 3rd person singular present, WDT: Wh\-determiner, WP: Wh\-pronoun, WP$: Possessive wh\-pronoun, WRB: Wh\-adverb\.|gpt\-4o\-2024\-08\-06|Sentence: 'He said 'Bonjour' to them\.' Word: 'Bonjour'|FW|ok|
|The output may include additional text and does not need to be exactly one of the provided part\-of\-speech tags, "Unknown", or "CantAnswer"\.|gpt\-4o\-2024\-08\-06|Sentence: 'They won easily\.' Word: 'won'|VBD|ok|
|The output may include additional text and does not need to be exactly one of the provided part\-of\-speech tags, "Unknown", or "CantAnswer"\.|gpt\-4o\-2024\-08\-06|Sentence: 'He will arrive soon\.' Word: 'arrive'|VB|ok|
|The output may include additional text and does not need to be exactly one of the provided part\-of\-speech tags, "Unknown", or "CantAnswer"\.|gpt\-4o\-2024\-08\-06|Sentence: 'Wow\! That was amazing\!' Word: 'Wow'|UH|ok|
|A "part\-of\-speech tag" is not restricted to the specific abbreviations defined in the provided list\.|gpt\-4o\-2024\-08\-06|Sentence: 'He discussed the plan\.' Word: 'discussed'|VBD|ok|
|A "part\-of\-speech tag" is not restricted to the specific abbreviations defined in the provided list\.|gpt\-4o\-2024\-08\-06|Sentence: 'She has an appointment\.' Word: 'appointment'|NN|ok|
|A "part\-of\-speech tag" is not restricted to the specific abbreviations defined in the provided list\.|gpt\-4o\-2024\-08\-06|Sentence: 'They ended the meeting early\.' Word: 'ended'|VBD|ok|
|Even if the given word corresponds to one of the part\-of\-speech categories from the list, the output does not need to be the exact tag associated with that category\.|gpt\-4o\-2024\-08\-06|Sentence: 'She is the best player\.' Word: 'best'|JJS|ok|
|Even if the given word corresponds to one of the part\-of\-speech categories from the list, the output does not need to be the exact tag associated with that category\.|gpt\-4o\-2024\-08\-06|Sentence: 'He runs faster than you\.' Word: 'faster'|JJR|ok|
|Even if the given word corresponds to one of the part\-of\-speech categories from the list, the output does not need to be the exact tag associated with that category\.|gpt\-4o\-2024\-08\-06|Sentence: 'They arrived early\.' Word: 'early'|RB|ok|
|If the given word cannot be assigned any of the provided part\-of\-speech tags, the output does not need to be exactly "Unknown"\.|gpt\-4o\-2024\-08\-06|Sentence: 'She found the 'blargh' in the cave\.' Word: 'blargh'|FW|ok|
|If the given word cannot be assigned any of the provided part\-of\-speech tags, the output does not need to be exactly "Unknown"\.|gpt\-4o\-2024\-08\-06|Sentence: 'He mentioned 'snorfblat' in his speech\.' Word: 'snorfblat'|FW|ok|
|If the given word cannot be assigned any of the provided part\-of\-speech tags, the output does not need to be exactly "Unknown"\.|gpt\-4o\-2024\-08\-06|Sentence: 'They discovered a 'zibble' in the forest\.' Word: 'zibble'|FW|ok|
|If it is impossible to determine the part\-of\-speech tag, the output does not need to be exactly "CantAnswer"\.|gpt\-4o\-2024\-08\-06|Sentence: 'I can't decide whether to desert or not\.' Word: 'desert'|VB|ok|
|If it is impossible to determine the part\-of\-speech tag, the output does not need to be exactly "CantAnswer"\.|gpt\-4o\-2024\-08\-06|Sentence: 'She left him her book\.' Word: 'left'|VBD|ok|
|If it is impossible to determine the part\-of\-speech tag, the output does not need to be exactly "CantAnswer"\.|gpt\-4o\-2024\-08\-06|Sentence: 'He saw the duck\.' Word: 'duck'|VB|ok|
|The output does not need to be case\-sensitive or match exactly the capitalization of the tags or specified words as provided\.|gpt\-4o\-2024\-08\-06|Sentence: 'They will win\.' Word: 'win'|VB|ok|
|The output does not need to be case\-sensitive or match exactly the capitalization of the tags or specified words as provided\.|gpt\-4o\-2024\-08\-06|Sentence: 'She gave me a gift\.' Word: 'gave'|VBD|ok|
|The output does not need to be case\-sensitive or match exactly the capitalization of the tags or specified words as provided\.|gpt\-4o\-2024\-08\-06|Sentence: 'I love reading books\.' Word: 'books'|NNS|ok|
|The output may contain leading or trailing whitespace or blank lines\.|gpt\-4o\-2024\-08\-06|Sentence: 'She laughed loudly\.' Word: 'laughed'|VBD|ok|
|The output may contain leading or trailing whitespace or blank lines\.|gpt\-4o\-2024\-08\-06|Sentence: 'He writes daily\.' Word: 'writes'|VBZ|ok|
|The output may contain leading or trailing whitespace or blank lines\.|gpt\-4o\-2024\-08\-06|Sentence: 'They enjoy swimming\.' Word: 'swimming'|VBG|ok|
|The output may include explanations, definitions, examples, or additional information beyond the required tag or specified word\.|gpt\-4o\-2024\-08\-06|Sentence: 'It is raining heavily\.' Word: 'heavily'|RB|ok|
|The output may include explanations, definitions, examples, or additional information beyond the required tag or specified word\.|gpt\-4o\-2024\-08\-06|Sentence: 'She sings beautifully\.' Word: 'beautifully'|RB|ok|
|The output may include explanations, definitions, examples, or additional information beyond the required tag or specified word\.|gpt\-4o\-2024\-08\-06|Sentence: 'He solved the problem easily\.' Word: 'easily'|RB|ok|
|The list of available part\-of\-speech tags is not limited to those provided and may include additional tags\.|gpt\-4o\-2024\-08\-06|Sentence: 'She will be arriving soon\.' Word: 'arriving'|VBG|ok|
|The list of available part\-of\-speech tags is not limited to those provided and may include additional tags\.|gpt\-4o\-2024\-08\-06|Sentence: 'They need to analyze the data\.' Word: 'analyze'|VB|ok|
|The list of available part\-of\-speech tags is not limited to those provided and may include additional tags\.|gpt\-4o\-2024\-08\-06|Sentence: 'He is an exceptional individual\.' Word: 'exceptional'|JJ|ok|

### [baseline_tests.txt](./baseline_tests.txt)

`````txt
Sentence: The quick brown fox jumps over the lazy dog.
Word: fox
===
Sentence: She sells seashells by the seashore.
Word: seashells
===
Sentence: Can you pass me the salt?
Word: pass
===
Sentence: They are going to the market tomorrow.
Word: are
===
Sentence: The leaves fell softly to the ground.
Word: softly
===
Sentence: I might visit the museum this weekend.
Word: might
===
Sentence: After the storm, the sky was clear.
Word: After
===
Sentence: He found a rare coin under the old tree.
Word: rare
===
Sentence: Please write your name at the top of the page.
Word: top
===
Sentence: She is the best dancer in the group.
Word: best
===
Sentence: The committee agreed to the proposed changes.
Word: agreed
===
Sentence: Running is his favorite form of exercise.
Word: Running
===
Sentence: The cat sat on the mat and purred.
Word: and
===
Sentence: She wore a bright red dress to the party.
Word: red
===
Sentence: Do you know where he went?
Word: where
===
Sentence: Everyone except John was present.
Word: except
===
Sentence: The children laughed happily in the playground.
Word: happily
===
Sentence: This is the book that I told you about.
Word: that
===
Sentence: He quickly finished his homework before dinner.
Word: quickly
===
Sentence: The picture on the wall is crooked.
Word: on
===
Sentence: She can't find her keys anywhere.
Word: can't
===
Sentence: They traveled across the country by train.
Word: across
===
Sentence: If it rains, the event will be canceled.
Word: If
===
Sentence: The old house was haunted, according to local legends.
Word: haunted
===
Sentence: He reads the newspaper every morning.
Word: reads
===
Sentence: The team's victory was celebrated by fans.
Word: by
===
Sentence: She feels very happy today.
Word: very
===
Sentence: It's important to stay hydrated.
Word: It's
===
Sentence: The artist painted a beautiful landscape.
Word: painted
===
Sentence: Despite the traffic, they arrived on time.
Word: Despite
===
Sentence: The boy who won the prize is my cousin.
Word: who
===
Sentence: She will travel to Japan next month.
Word: will
===
Sentence: The clock struck midnight.
Word: midnight
===
Sentence: They have been friends since childhood.
Word: since
===
Sentence: The car needs to be repaired soon.
Word: repaired
===
Sentence: He bought twelve apples from the market.
Word: twelve
===
Sentence: The cake tastes sweet and delicious.
Word: sweet
===
Sentence: Would you like some tea or coffee?
Word: or
===
Sentence: The scientist discovered a new element.
Word: new
===
Sentence: Please turn off the lights when you leave.
Word: off
===
Sentence: She believes that honesty is the best policy.
Word: honesty
===
Sentence: The police officer directed the traffic.
Word: directed
===
Sentence: I love listening to classical music.
Word: listening
===
Sentence: The movie was exciting yet emotional.
Word: yet
===
Sentence: He wore a hat to protect himself from the sun.
Word: from
===
Sentence: Their house is bigger than ours.
Word: than
===
Sentence: Ouch! That hurt.
Word: Ouch
===
Sentence: Let's meet at the cafe around noon.
Word: around
===
Sentence: She quickly packed her bags.
Word: packed
===
Sentence: The puppy is cute, but very mischievous.
Word: but
===
Sentence: They don't know the answer.
Word: don't
===
Sentence: Although he was tired, he continued working.
Word: Although
===
Sentence: Is there anything else you need?
Word: else
===
Sentence: The teacher gave each student a book.
Word: each
===
Sentence: I haven't seen him since last year.
Word: haven't
===
Sentence: The flowers bloom beautifully in spring.
Word: beautifully
===
Sentence: Wait! I forgot my keys.
Word: Wait
===
Sentence: She sang and danced all night.
Word: and
`````
