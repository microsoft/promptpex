## speech-tag ([json](./evals\v7\speech-tag/report.json))

- 7 rules
- 7 inverse rules
- 84 tests, 42 baseline tests
- 336 test results, 250/336 (74%) oks, 86/336 (25%) errs

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
|gpt\-4o\-mini|42|100%|100%|21|21|21|21|42|30|30|
|gemma2:9b|42|95%|98%|21|21|21|19|42|30|30|
|qwen2\.5:3b|42|98%|93%|21|20|21|21|42|30|29|
|llama3\.2:1b|42|10%|2%|21|1|21|3|42|30|2|

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
|gpt\-4o\-mini|The output must only contain a single part of speech tag from the pre\-defined list in the system prompt\.|Sentence: The quick brown fox jumps over the lazy dog\. Word: fox|NN|ok|
|gemma2:9b|The output must only contain a single part of speech tag from the pre\-defined list in the system prompt\.|Sentence: The quick brown fox jumps over the lazy dog\. Word: fox|NN|ok|
|qwen2\.5:3b|The output must only contain a single part of speech tag from the pre\-defined list in the system prompt\.|Sentence: The quick brown fox jumps over the lazy dog\. Word: fox|NN|ok|
|llama3\.2:1b|The output must only contain a single part of speech tag from the pre\-defined list in the system prompt\.|Sentence: The quick brown fox jumps over the lazy dog\. Word: fox|CC: fox<br>JJS: fox|err|
|gpt\-4o\-mini|The output must only contain a single part of speech tag from the pre\-defined list in the system prompt\.|Sentence: She sells seashells by the seashore\. Word: sells|VBP|ok|
|gemma2:9b|The output must only contain a single part of speech tag from the pre\-defined list in the system prompt\.|Sentence: She sells seashells by the seashore\. Word: sells|VBZ|ok|
|qwen2\.5:3b|The output must only contain a single part of speech tag from the pre\-defined list in the system prompt\.|Sentence: She sells seashells by the seashore\. Word: sells|VB︻̲VK|err|
|llama3\.2:1b|The output must only contain a single part of speech tag from the pre\-defined list in the system prompt\.|Sentence: She sells seashells by the seashore\. Word: sells|Word: CC \(Coordinating conjunction\)<br><br> Sentence remains the same as it was initially provided with the word "sells" which is a linking verb forming a present tense conditional sentence from the participle phrase "seasels"\.<br><br>Sentence:<br> She sells seashells by the seashore\.|err|
|gpt\-4o\-mini|The output must only contain a single part of speech tag from the pre\-defined list in the system prompt\.|Sentence: Yesterday, it rained heavily\. Word: rained|VBD|ok|
|gemma2:9b|The output must only contain a single part of speech tag from the pre\-defined list in the system prompt\.|Sentence: Yesterday, it rained heavily\. Word: rained|VBD|ok|
|qwen2\.5:3b|The output must only contain a single part of speech tag from the pre\-defined list in the system prompt\.|Sentence: Yesterday, it rained heavily\. Word: rained|VBZ|ok|
|llama3\.2:1b|The output must only contain a single part of speech tag from the pre\-defined list in the system prompt\.|Sentence: Yesterday, it rained heavily\. Word: rained|Here are the part of speech tags:<br><br>1\. Sentence: CC: Coordinating conjunction<br>2\. Word: rained \- IN: Preposition or subordinating conjunction \(in "Yesterday"\)<br>3\. Sentence: rained \- JJR/JJS/RBR/RBS: Adjective and comparative/superlative/gradable adjective \(in "heavily"\)|err|
|gpt\-4o\-mini|The output must be an exact match to one of the tags in the pre\-defined list, if applicable\.|Sentence: The cat sat on the mat\. Word: cat|NN|ok|
|gemma2:9b|The output must be an exact match to one of the tags in the pre\-defined list, if applicable\.|Sentence: The cat sat on the mat\. Word: cat|NN|ok|
|qwen2\.5:3b|The output must be an exact match to one of the tags in the pre\-defined list, if applicable\.|Sentence: The cat sat on the mat\. Word: cat|NN|ok|
|llama3\.2:1b|The output must be an exact match to one of the tags in the pre\-defined list, if applicable\.|Sentence: The cat sat on the mat\. Word: cat|Word: cat \(NNPS\)<br>Part\-of\-speech tag: NNP \(Proper noun, singular\)|err|
|gpt\-4o\-mini|The output must be an exact match to one of the tags in the pre\-defined list, if applicable\.|Sentence: Birds fly high\. Word: fly|VB|ok|
|gemma2:9b|The output must be an exact match to one of the tags in the pre\-defined list, if applicable\.|Sentence: Birds fly high\. Word: fly|VB|ok|
|qwen2\.5:3b|The output must be an exact match to one of the tags in the pre\-defined list, if applicable\.|Sentence: Birds fly high\. Word: fly|VB|ok|
|llama3\.2:1b|The output must be an exact match to one of the tags in the pre\-defined list, if applicable\.|Sentence: Birds fly high\. Word: fly|Part\-of\-speech tag for the word "fly":<br>VBZ \(Third\-person singular present tense of the verb "to fly"\)|err|
|gpt\-4o\-mini|The output must be an exact match to one of the tags in the pre\-defined list, if applicable\.|Sentence: One hundred apples fell\. Word: hundred|CD|ok|
|gemma2:9b|The output must be an exact match to one of the tags in the pre\-defined list, if applicable\.|Sentence: One hundred apples fell\. Word: hundred|CD|ok|
|qwen2\.5:3b|The output must be an exact match to one of the tags in the pre\-defined list, if applicable\.|Sentence: One hundred apples fell\. Word: hundred|CD|ok|
|llama3\.2:1b|The output must be an exact match to one of the tags in the pre\-defined list, if applicable\.|Sentence: One hundred apples fell\. Word: hundred|Part\-of\-speech tag for "hundred": CD \(Cardinal number\)<br> <br>\(Note: While the word "hundred" is technically a plural noun, in this context it's used as a determiner to indicate that 100 is being counted individually\.\)|err|
|gpt\-4o\-mini|If the word provided in the input can be matched to one of the listed part of speech tags, return only the corresponding tag as the output, with no additional text or formatting\.|Sentence: A large tree fell\. Word: large|JJ|ok|
|gemma2:9b|If the word provided in the input can be matched to one of the listed part of speech tags, return only the corresponding tag as the output, with no additional text or formatting\.|Sentence: A large tree fell\. Word: large|JJ|ok|
|qwen2\.5:3b|If the word provided in the input can be matched to one of the listed part of speech tags, return only the corresponding tag as the output, with no additional text or formatting\.|Sentence: A large tree fell\. Word: large|JJ|ok|
|llama3\.2:1b|If the word provided in the input can be matched to one of the listed part of speech tags, return only the corresponding tag as the output, with no additional text or formatting\.|Sentence: A large tree fell\. Word: large|In the first sentence, the tag for "large" is DD: Determiner\.<br><br>In the second sentence, the tag for "large" is CD: Cardinal number\.|err|
|gpt\-4o\-mini|If the word provided in the input can be matched to one of the listed part of speech tags, return only the corresponding tag as the output, with no additional text or formatting\.|Sentence: I usually walk home\. Word: usually|RB|ok|
|gemma2:9b|If the word provided in the input can be matched to one of the listed part of speech tags, return only the corresponding tag as the output, with no additional text or formatting\.|Sentence: I usually walk home\. Word: usually|RB|ok|
|qwen2\.5:3b|If the word provided in the input can be matched to one of the listed part of speech tags, return only the corresponding tag as the output, with no additional text or formatting\.|Sentence: I usually walk home\. Word: usually|VBZ|ok|
|llama3\.2:1b|If the word provided in the input can be matched to one of the listed part of speech tags, return only the corresponding tag as the output, with no additional text or formatting\.|Sentence: I usually walk home\. Word: usually|Word: usually \- JJ<br>Sentence: I usually walk home\. Word: usually \- JJ|ok|
|gpt\-4o\-mini|If the word provided in the input can be matched to one of the listed part of speech tags, return only the corresponding tag as the output, with no additional text or formatting\.|Sentence: They have been healthy\. Word: have|VB|ok|
|gemma2:9b|If the word provided in the input can be matched to one of the listed part of speech tags, return only the corresponding tag as the output, with no additional text or formatting\.|Sentence: They have been healthy\. Word: have|VBP|ok|
|qwen2\.5:3b|If the word provided in the input can be matched to one of the listed part of speech tags, return only the corresponding tag as the output, with no additional text or formatting\.|Sentence: They have been healthy\. Word: have|VB|ok|
|llama3\.2:1b|If the word provided in the input can be matched to one of the listed part of speech tags, return only the corresponding tag as the output, with no additional text or formatting\.|Sentence: They have been healthy\. Word: have|POS for the word 'have': ADJ|err|
|gpt\-4o\-mini|If the word provided in the input cannot be assigned any of the listed part of speech tags, the output should only contain the word "Unknown"\.|Sentence: Everything went according to the plan\. Word: according|IN|ok|
|gemma2:9b|If the word provided in the input cannot be assigned any of the listed part of speech tags, the output should only contain the word "Unknown"\.|Sentence: Everything went according to the plan\. Word: according|IN|ok|
|qwen2\.5:3b|If the word provided in the input cannot be assigned any of the listed part of speech tags, the output should only contain the word "Unknown"\.|Sentence: Everything went according to the plan\. Word: according|IN|ok|
|llama3\.2:1b|If the word provided in the input cannot be assigned any of the listed part of speech tags, the output should only contain the word "Unknown"\.|Sentence: Everything went according to the plan\. Word: according|Part\-of\-speech tag for "according" is JJ\.<br><br>As it appears twice in the sentence, I'll list them separately:<br> JJ in "everything"<br> JJ in "according"<br><br>Both instances can be tagged with "JJ", but since they appear twice, the return for both occurrences of the word should be JJ, returning JJ as our answer\.|err|
|gpt\-4o\-mini|If the word provided in the input cannot be assigned any of the listed part of speech tags, the output should only contain the word "Unknown"\.|Sentence: The session was remarkable\. Word: sessione|Unknown|ok|
|gemma2:9b|If the word provided in the input cannot be assigned any of the listed part of speech tags, the output should only contain the word "Unknown"\.|Sentence: The session was remarkable\. Word: sessione|Unknown|ok|
|qwen2\.5:3b|If the word provided in the input cannot be assigned any of the listed part of speech tags, the output should only contain the word "Unknown"\.|Sentence: The session was remarkable\. Word: sessione|CantAnswer|ok|
|llama3\.2:1b|If the word provided in the input cannot be assigned any of the listed part of speech tags, the output should only contain the word "Unknown"\.|Sentence: The session was remarkable\. Word: sessione|Part\-of\-speech tag for "sessione" is NN \(Noun\)\. <br><br>Part\-of\-speech tag for "The session" is NNPs \(Proper Noun, plural\), PT \(Proprietied noun\), and TO \(to\)\.<br><br> So the complete output will be:<br> <br>NN  <br>NNP<br>TO|err|
|gpt\-4o\-mini|If the word provided in the input cannot be assigned any of the listed part of speech tags, the output should only contain the word "Unknown"\.|Sentence: My new routine will adapt\. Word: xyzzy|Unknown|ok|
|gemma2:9b|If the word provided in the input cannot be assigned any of the listed part of speech tags, the output should only contain the word "Unknown"\.|Sentence: My new routine will adapt\. Word: xyzzy|Unknown|ok|
|qwen2\.5:3b|If the word provided in the input cannot be assigned any of the listed part of speech tags, the output should only contain the word "Unknown"\.|Sentence: My new routine will adapt\. Word: xyzzy|Unknown|ok|
|llama3\.2:1b|If the word provided in the input cannot be assigned any of the listed part of speech tags, the output should only contain the word "Unknown"\.|Sentence: My new routine will adapt\. Word: xyzzy|Part of Speech Tag:<br>\- Sentence: CNT: Conjunctive particle \(was not in sentence\), CC: Coordinating conjunction \(correct\), etc\.<br>\- Word: xyzzy \- NN: Noun \(Correct\)|err|
|gpt\-4o\-mini|If it is not possible to determine the part of speech from the input, the output should only contain the word "CantAnswer"\.|Sentence: This sentence cannot be processed\. Word: unprocesable|Unknown|ok|
|gemma2:9b|If it is not possible to determine the part of speech from the input, the output should only contain the word "CantAnswer"\.|Sentence: This sentence cannot be processed\. Word: unprocesable|JJ|ok|
|qwen2\.5:3b|If it is not possible to determine the part of speech from the input, the output should only contain the word "CantAnswer"\.|Sentence: This sentence cannot be processed\. Word: unprocesable|CantAnswer|ok|
|llama3\.2:1b|If it is not possible to determine the part of speech from the input, the output should only contain the word "CantAnswer"\.|Sentence: This sentence cannot be processed\. Word: unprocesable|CC: Un procesable <br>WRB: Uncan not procesable|err|
|gpt\-4o\-mini|If it is not possible to determine the part of speech from the input, the output should only contain the word "CantAnswer"\.|Sentence: A complex wordplay occurred here\. Word: qwertyuiop|Unknown|ok|
|gemma2:9b|If it is not possible to determine the part of speech from the input, the output should only contain the word "CantAnswer"\.|Sentence: A complex wordplay occurred here\. Word: qwertyuiop|Unknown|ok|
|qwen2\.5:3b|If it is not possible to determine the part of speech from the input, the output should only contain the word "CantAnswer"\.|Sentence: A complex wordplay occurred here\. Word: qwertyuiop|Unknown|ok|
|llama3\.2:1b|If it is not possible to determine the part of speech from the input, the output should only contain the word "CantAnswer"\.|Sentence: A complex wordplay occurred here\. Word: qwertyuiop|CC: <br>Determiner: <br>EX: Causal existential there, <br>FW: Foreign word, <br>IN: Interjection or subordinating conjunction, JJ: Adjective,JJR: Adjective, superlative, JJS: Adjective, comparative, JJS: Adjective, superlative, LS: List item marker, MD: Modal, NN: Noun, singular or mass, NNS: Noun, plural, NNP: Proper noun, singular, NNPS: Proper noun, plural, PDT: Predeterminer, POS: Possessive ending, PRP: Personal pronoun, PRP$: Possessive pronoun, RB: Adverb, RBR: Adverb, comparative, RBS: Adverb, superlative, RP: particle,SYM: Symbol,<br>MD: Modal, NN: Noun, <br>singular or mass, NNS: Noun,<br>plural,NNPS: Proper noun, plural, PDT: Predeterminer, POS: Possessive ending, PRP: Personal pronoun, PRP$: Possessive pronoun, RB: Adverb, RBR: Adverb, comparative, RBS: Adverb, superlative,RP: Particle,<br>SYM: Symbol<br>CantAnswer\.<br>To be honest and to continue in this task I need more examples of the given word\. Can you please give me another sentence with the same word?|err|
|gpt\-4o\-mini|If it is not possible to determine the part of speech from the input, the output should only contain the word "CantAnswer"\.|Sentence: Many colorful dreams arise unhindered\. Word: ljfdksjl|CantAnswer|ok|
|gemma2:9b|If it is not possible to determine the part of speech from the input, the output should only contain the word "CantAnswer"\.|Sentence: Many colorful dreams arise unhindered\. Word: ljfdksjl|CantAnswer|ok|
|qwen2\.5:3b|If it is not possible to determine the part of speech from the input, the output should only contain the word "CantAnswer"\.|Sentence: Many colorful dreams arise unhindered\. Word: ljfdksjl|CantAnswer|ok|
|llama3\.2:1b|If it is not possible to determine the part of speech from the input, the output should only contain the word "CantAnswer"\.|Sentence: Many colorful dreams arise unhindered\. Word: ljfdksjl|Part\-of\-speech tag:<br>IN: Noun <br><br>\(Note: The word "ljdfksjl" seems to be gibberish or random characters\. I couldn't identify any valid words in this context with the given list of tags, so I returned IN: Noun\. Alternatively, it might represent a technical term or code, which would require more information or clarification\.\)|err|
|gpt\-4o\-mini|The output must contain no additional information besides the specified part of speech tag or the exact words "Unknown" or "CantAnswer" based on the given rules\.|Sentence: Their experiment succeeded\. Word: succeeded|VBD|ok|
|gemma2:9b|The output must contain no additional information besides the specified part of speech tag or the exact words "Unknown" or "CantAnswer" based on the given rules\.|Sentence: Their experiment succeeded\. Word: succeeded|VBD|ok|
|qwen2\.5:3b|The output must contain no additional information besides the specified part of speech tag or the exact words "Unknown" or "CantAnswer" based on the given rules\.|Sentence: Their experiment succeeded\. Word: succeeded|VBZ|ok|
|llama3\.2:1b|The output must contain no additional information besides the specified part of speech tag or the exact words "Unknown" or "CantAnswer" based on the given rules\.|Sentence: Their experiment succeeded\. Word: succeeded|Here are the results:<br><br>1\. Sentence: Their experiment succeeded\.<br>Word: succeeded <br>Part of Speech tag: VBD \(Verb, past tense\)<br><br>2\. Sentence: Their experiment succeeded\.<br>Word: succeeded<br>Part of Politics speech tag: VBZ \(Verb, 3rd person singular present\)|err|
|gpt\-4o\-mini|The output must contain no additional information besides the specified part of speech tag or the exact words "Unknown" or "CantAnswer" based on the given rules\.|Sentence: Appreciate the colors of the wind\. Word: colors|NNS|ok|
|gemma2:9b|The output must contain no additional information besides the specified part of speech tag or the exact words "Unknown" or "CantAnswer" based on the given rules\.|Sentence: Appreciate the colors of the wind\. Word: colors|NN|ok|
|qwen2\.5:3b|The output must contain no additional information besides the specified part of speech tag or the exact words "Unknown" or "CantAnswer" based on the given rules\.|Sentence: Appreciate the colors of the wind\. Word: colors|NN|ok|
|llama3\.2:1b|The output must contain no additional information besides the specified part of speech tag or the exact words "Unknown" or "CantAnswer" based on the given rules\.|Sentence: Appreciate the colors of the wind\. Word: colors|The part\-of\-speech tag for the word "colors" in both sentences is NN\.<br><br> Sentence: Appreciate the colors of the wind\. Word: Appreciate<br> Part\-of\-speech tag: NN <br><br> Sentence: Appreciate the colors of the wind\. Word: Appreciate<br> Part\-of\-speech tag: CC|err|
|gpt\-4o\-mini|The output must contain no additional information besides the specified part of speech tag or the exact words "Unknown" or "CantAnswer" based on the given rules\.|Sentence: She can solve the mystery alone\. Word: can|MD|ok|
|gemma2:9b|The output must contain no additional information besides the specified part of speech tag or the exact words "Unknown" or "CantAnswer" based on the given rules\.|Sentence: She can solve the mystery alone\. Word: can|MD|ok|
|qwen2\.5:3b|The output must contain no additional information besides the specified part of speech tag or the exact words "Unknown" or "CantAnswer" based on the given rules\.|Sentence: She can solve the mystery alone\. Word: can|VBZ|ok|
|llama3\.2:1b|The output must contain no additional information besides the specified part of speech tag or the exact words "Unknown" or "CantAnswer" based on the given rules\.|Sentence: She can solve the mystery alone\. Word: can|Word: can<br>Part of speech tag: V1 \(base form\) <br><br> Sentence: The sun rises in the east and sets in the west on most days but not every day it remains above the horizon for some time|err|
|gpt\-4o\-mini|Every word in the provided input must be attempted to be tagged according to the conditions defined, and the output must reflect one of the listed scenarios appropriately\.|Sentence: He quickly understood the situation\. Word: quickly|RB|ok|
|gemma2:9b|Every word in the provided input must be attempted to be tagged according to the conditions defined, and the output must reflect one of the listed scenarios appropriately\.|Sentence: He quickly understood the situation\. Word: quickly|RB|ok|
|qwen2\.5:3b|Every word in the provided input must be attempted to be tagged according to the conditions defined, and the output must reflect one of the listed scenarios appropriately\.|Sentence: He quickly understood the situation\. Word: quickly|VB|ok|
|llama3\.2:1b|Every word in the provided input must be attempted to be tagged according to the conditions defined, and the output must reflect one of the listed scenarios appropriately\.|Sentence: He quickly understood the situation\. Word: quickly|Here are the parts of speech tags for each word:<br><br>\- Word: "quickly" \- JJ: Adjective<br>\- Word: "quickly" \- JJR: Superlative adjective, JJS: Comparative superlative adjective|err|
|gpt\-4o\-mini|Every word in the provided input must be attempted to be tagged according to the conditions defined, and the output must reflect one of the listed scenarios appropriately\.|Sentence: They left yesterday\. Word: yesterday|RB|ok|
|gemma2:9b|Every word in the provided input must be attempted to be tagged according to the conditions defined, and the output must reflect one of the listed scenarios appropriately\.|Sentence: They left yesterday\. Word: yesterday|RB|ok|
|qwen2\.5:3b|Every word in the provided input must be attempted to be tagged according to the conditions defined, and the output must reflect one of the listed scenarios appropriately\.|Sentence: They left yesterday\. Word: yesterday|JJ|ok|
|llama3\.2:1b|Every word in the provided input must be attempted to be tagged according to the conditions defined, and the output must reflect one of the listed scenarios appropriately\.|Sentence: They left yesterday\. Word: yesterday|Part\-of\-speech tag for "yesterday" is PD\.<br> Part\-of\-speech tag for Sentence \(as a whole\) is NN\. <br>No part of speech can be determined for the word CantAnswer since it's not in the list but "CantAnswer" can also imply there are no words to analyze, or it may simply contain an unknown or invalid word|err|
|gpt\-4o\-mini|Every word in the provided input must be attempted to be tagged according to the conditions defined, and the output must reflect one of the listed scenarios appropriately\.|Sentence: Imagine a brighter future\. Word: Imagine|VB|ok|
|gemma2:9b|Every word in the provided input must be attempted to be tagged according to the conditions defined, and the output must reflect one of the listed scenarios appropriately\.|Sentence: Imagine a brighter future\. Word: Imagine|VB|ok|
|qwen2\.5:3b|Every word in the provided input must be attempted to be tagged according to the conditions defined, and the output must reflect one of the listed scenarios appropriately\.|Sentence: Imagine a brighter future\. Word: Imagine|VBZ|ok|
|llama3\.2:1b|Every word in the provided input must be attempted to be tagged according to the conditions defined, and the output must reflect one of the listed scenarios appropriately\.|Sentence: Imagine a brighter future\. Word: Imagine|Part\-of\-speech tag for "Imagine" is NNP \(Noun, proper noun\)\.<br><br>As "Imagine" is the same word in both sentences, it can only be tagged as NNP \(which stands for Noun, proper noun\)\.|err|
|gpt\-4o\-mini|The output must contain multiple parts of speech tags that are not from the pre\-defined list in the system prompt\.|Sentence: The plan was executed hurrily\. Word: hurrily|Unknown|ok|
|gemma2:9b|The output must contain multiple parts of speech tags that are not from the pre\-defined list in the system prompt\.|Sentence: The plan was executed hurrily\. Word: hurrily|RBS|ok|
|qwen2\.5:3b|The output must contain multiple parts of speech tags that are not from the pre\-defined list in the system prompt\.|Sentence: The plan was executed hurrily\. Word: hurrily|RB|ok|
|llama3\.2:1b|The output must contain multiple parts of speech tags that are not from the pre\-defined list in the system prompt\.|Sentence: The plan was executed hurrily\. Word: hurrily|Word: hurrily<br><br>Tag: RB \(Adverb\)|ok|
|gpt\-4o\-mini|The output must contain multiple parts of speech tags that are not from the pre\-defined list in the system prompt\.|Sentence: Welcome to zzyzx road\. Word: zzyzx|NNP|ok|
|gemma2:9b|The output must contain multiple parts of speech tags that are not from the pre\-defined list in the system prompt\.|Sentence: Welcome to zzyzx road\. Word: zzyzx|NNP|ok|
|qwen2\.5:3b|The output must contain multiple parts of speech tags that are not from the pre\-defined list in the system prompt\.|Sentence: Welcome to zzyzx road\. Word: zzyzx|Unknown|ok|
|llama3\.2:1b|The output must contain multiple parts of speech tags that are not from the pre\-defined list in the system prompt\.|Sentence: Welcome to zzyzx road\. Word: zzyzx|Words: <br>\- zzyzx: Unknown|err|
|gpt\-4o\-mini|The output must contain multiple parts of speech tags that are not from the pre\-defined list in the system prompt\.|Sentence: I coined murf the word\. Word: murf|NN|ok|
|gemma2:9b|The output must contain multiple parts of speech tags that are not from the pre\-defined list in the system prompt\.|Sentence: I coined murf the word\. Word: murf|NN|ok|
|qwen2\.5:3b|The output must contain multiple parts of speech tags that are not from the pre\-defined list in the system prompt\.|Sentence: I coined murf the word\. Word: murf|NN|ok|
|llama3\.2:1b|The output must contain multiple parts of speech tags that are not from the pre\-defined list in the system prompt\.|Sentence: I coined murf the word\. Word: murf|Here are the part of speech tags:<br><br>1\. I \- PRP$ \(Possessive pronoun\)<br>2\. coined \- JJR \(comparative adjective\)<br>3\. murf \- NNPS \(Proper noun, plural\)|err|
|gpt\-4o\-mini|The output must not match any of the tags in the pre\-defined list, where applicable\.|Sentence: That is unanticipatedly concise\. Word: unanticipatedly|RB|ok|
|gemma2:9b|The output must not match any of the tags in the pre\-defined list, where applicable\.|Sentence: That is unanticipatedly concise\. Word: unanticipatedly|RB|ok|
|qwen2\.5:3b|The output must not match any of the tags in the pre\-defined list, where applicable\.|Sentence: That is unanticipatedly concise\. Word: unanticipatedly|RB|ok|
|llama3\.2:1b|The output must not match any of the tags in the pre\-defined list, where applicable\.|Sentence: That is unanticipatedly concise\. Word: unanticipatedly|Word: unanticipatedly<br> Tag: ADJ|err|
|gpt\-4o\-mini|The output must not match any of the tags in the pre\-defined list, where applicable\.|Sentence: Her demeanor was inaccesible\.|JJ|ok|
|gemma2:9b|The output must not match any of the tags in the pre\-defined list, where applicable\.|Sentence: Her demeanor was inaccesible\.|inaccesible  JJ|err|
|qwen2\.5:3b|The output must not match any of the tags in the pre\-defined list, where applicable\.|Sentence: Her demeanor was inaccesible\.|JJ|ok|
|llama3\.2:1b|The output must not match any of the tags in the pre\-defined list, where applicable\.|Sentence: Her demeanor was inaccesible\.|Tag for 'inaccessible': CC<br><br>Tag for 'inaccessible': DS \(Determiner/Sing\) <br><br>As you can see from the list, it seems I was able to correctly identify " inaccessible" as an adjectival form in this case and thus returned "CC"\. However, upon further inspection of the second sentence, I realize that it actually contains 2 occurrences of 'inaccessible', so a correction is needed: Tag for both instances would be DS\.|err|
|gpt\-4o\-mini|The output must not match any of the tags in the pre\-defined list, where applicable\.|Sentence: There are many colours in this art\.|RB|ok|
|gemma2:9b|The output must not match any of the tags in the pre\-defined list, where applicable\.|Sentence: There are many colours in this art\.|VB  \(Verb, base form\) <br><br><br>Let me know if you have another word you'd like tagged\!|err|
|qwen2\.5:3b|The output must not match any of the tags in the pre\-defined list, where applicable\.|Sentence: There are many colours in this art\.|VBZ|ok|
|llama3\.2:1b|The output must not match any of the tags in the pre\-defined list, where applicable\.|Sentence: There are many colours in this art\.|Word: Many<br>Tags: CC: Coordinating conjunction, DT: Determiner, IN: Preposition or subordinating conjunction, JJS: Adjective, LS: List item marker, NN: Noun, singular or mass, NNS: Noun, plural, VBZ: Verb, 3rd person singular present|err|
|gpt\-4o\-mini|If the word provided in the input can be matched to one of the listed part of speech tags, return additional text and formatting rather than the corresponding tag\.|Sentence: Mist in the valley is enchanting\. Word: enchanting|JJ|ok|
|gemma2:9b|If the word provided in the input can be matched to one of the listed part of speech tags, return additional text and formatting rather than the corresponding tag\.|Sentence: Mist in the valley is enchanting\. Word: enchanting|JJ|ok|
|qwen2\.5:3b|If the word provided in the input can be matched to one of the listed part of speech tags, return additional text and formatting rather than the corresponding tag\.|Sentence: Mist in the valley is enchanting\. Word: enchanting|JJ|ok|
|llama3\.2:1b|If the word provided in the input can be matched to one of the listed part of speech tags, return additional text and formatting rather than the corresponding tag\.|Sentence: Mist in the valley is enchanting\. Word: enchanting|Word: enchanting <br>tag: JJ|ok|
|gpt\-4o\-mini|If the word provided in the input can be matched to one of the listed part of speech tags, return additional text and formatting rather than the corresponding tag\.|Sentence: Laughter echoed through hall endlessly\. Word: endlessly|RB|ok|
|gemma2:9b|If the word provided in the input can be matched to one of the listed part of speech tags, return additional text and formatting rather than the corresponding tag\.|Sentence: Laughter echoed through hall endlessly\. Word: endlessly|RB|ok|
|qwen2\.5:3b|If the word provided in the input can be matched to one of the listed part of speech tags, return additional text and formatting rather than the corresponding tag\.|Sentence: Laughter echoed through hall endlessly\. Word: endlessly|RB|ok|
|llama3\.2:1b|If the word provided in the input can be matched to one of the listed part of speech tags, return additional text and formatting rather than the corresponding tag\.|Sentence: Laughter echoed through hall endlessly\. Word: endlessly|Word: endlessly<br>Part of speech tag: CD \(Cardinal number\)|ok|
|gpt\-4o\-mini|If the word provided in the input can be matched to one of the listed part of speech tags, return additional text and formatting rather than the corresponding tag\.|Sentence: Eagerly awaited\. Word: awaited|VBD|ok|
|gemma2:9b|If the word provided in the input can be matched to one of the listed part of speech tags, return additional text and formatting rather than the corresponding tag\.|Sentence: Eagerly awaited\. Word: awaited|VBN|ok|
|qwen2\.5:3b|If the word provided in the input can be matched to one of the listed part of speech tags, return additional text and formatting rather than the corresponding tag\.|Sentence: Eagerly awaited\. Word: awaited|VBZ|ok|
|llama3\.2:1b|If the word provided in the input can be matched to one of the listed part of speech tags, return additional text and formatting rather than the corresponding tag\.|Sentence: Eagerly awaited\. Word: awaited|\-awaited \(NN\)<br>\.awaited \(VBZ\)|err|
|gpt\-4o\-mini|If the word provided in the input cannot be assigned any of the listed part of speech tags, the output should not contain the word "Unknown"\.|Sentence: The unexplained phenomenon\. Word: unexplained|JJ|ok|
|gemma2:9b|If the word provided in the input cannot be assigned any of the listed part of speech tags, the output should not contain the word "Unknown"\.|Sentence: The unexplained phenomenon\. Word: unexplained|JJ <br><br><br>You're looking for the part of speech tag for "unexplained", which is an adjective in this case\.  Therefore, the answer is \*\*JJ\*\*\.|ok|
|qwen2\.5:3b|If the word provided in the input cannot be assigned any of the listed part of speech tags, the output should not contain the word "Unknown"\.|Sentence: The unexplained phenomenon\. Word: unexplained|JJ|ok|
|llama3\.2:1b|If the word provided in the input cannot be assigned any of the listed part of speech tags, the output should not contain the word "Unknown"\.|Sentence: The unexplained phenomenon\. Word: unexplained|Word: Unexplained<br><br>CC<br><br> Sentence: The unexplained phenomenon\. Word: unexplained<br> Sentence: The unexplained phenomenon\. Word: unexplained<br><br>Word: Unexplained <br><br>DT <br> DT \(used twice, in a compound adverb\)|err|
|gpt\-4o\-mini|If the word provided in the input cannot be assigned any of the listed part of speech tags, the output should not contain the word "Unknown"\.|Sentence: Uncharted discoveries multiplied\. Word: uncharted|JJ|ok|
|gemma2:9b|If the word provided in the input cannot be assigned any of the listed part of speech tags, the output should not contain the word "Unknown"\.|Sentence: Uncharted discoveries multiplied\. Word: uncharted|JJ|ok|
|qwen2\.5:3b|If the word provided in the input cannot be assigned any of the listed part of speech tags, the output should not contain the word "Unknown"\.|Sentence: Uncharted discoveries multiplied\. Word: uncharted|NN|ok|
|llama3\.2:1b|If the word provided in the input cannot be assigned any of the listed part of speech tags, the output should not contain the word "Unknown"\.|Sentence: Uncharted discoveries multiplied\. Word: uncharted|Word: uncharted <br>Tag: ADJ <br><br> Sentence: Uncharted discoveries multiplied\. Word: uncharted\. Tag: NOUN <br><br>Note: The word "uncharted" can also function as an adjective in certain contexts, but based on its usage and the list of tags provided, it's most accurate to consider it a noun in this case\.|err|
|gpt\-4o\-mini|If the word provided in the input cannot be assigned any of the listed part of speech tags, the output should not contain the word "Unknown"\.|Sentence: Freshly baked cookies\. Word: baked|VBN|ok|
|gemma2:9b|If the word provided in the input cannot be assigned any of the listed part of speech tags, the output should not contain the word "Unknown"\.|Sentence: Freshly baked cookies\. Word: baked|VBN|ok|
|qwen2\.5:3b|If the word provided in the input cannot be assigned any of the listed part of speech tags, the output should not contain the word "Unknown"\.|Sentence: Freshly baked cookies\. Word: baked|VBG|ok|
|llama3\.2:1b|If the word provided in the input cannot be assigned any of the listed part of speech tags, the output should not contain the word "Unknown"\.|Sentence: Freshly baked cookies\. Word: baked|Tagged: NN \(Noun\)<br>Unknown<br>Tagged: JJR \(Adjective, comparative\) and JJ \(Adjective, superlative\) Cannot be applied to a singular noun like 'baked' so 'JJR/JJ cannot tag it'\.<br>Tagged: VBZ \(Verb, non\-3rd person singular present\)|err|
|gpt\-4o\-mini|If it is not possible to determine the part of speech from the input, the output should not contain the word "CantAnswer"\.|Sentence: My non\-conclusive sentence\. Word: non\-conclusive|JJ|ok|
|gemma2:9b|If it is not possible to determine the part of speech from the input, the output should not contain the word "CantAnswer"\.|Sentence: My non\-conclusive sentence\. Word: non\-conclusive|JJ|ok|
|qwen2\.5:3b|If it is not possible to determine the part of speech from the input, the output should not contain the word "CantAnswer"\.|Sentence: My non\-conclusive sentence\. Word: non\-conclusive|NNPS|ok|
|llama3\.2:1b|If it is not possible to determine the part of speech from the input, the output should not contain the word "CantAnswer"\.|Sentence: My non\-conclusive sentence\. Word: non\-conclusive|Here are the results:<br><br>1\. The word "non\-conclusive" has as its part of speech tag POS \(Noun\)\.<br>2\. The word "non\-conclusive" has as its part of speech tag JJS \(Adjective, superlative\)\.|err|
|gpt\-4o\-mini|If it is not possible to determine the part of speech from the input, the output should not contain the word "CantAnswer"\.|Sentence: My entirely customized interface\.W ord: entirely|RB|ok|
|gemma2:9b|If it is not possible to determine the part of speech from the input, the output should not contain the word "CantAnswer"\.|Sentence: My entirely customized interface\.W ord: entirely|RB|ok|
|qwen2\.5:3b|If it is not possible to determine the part of speech from the input, the output should not contain the word "CantAnswer"\.|Sentence: My entirely customized interface\.W ord: entirely|JJ|ok|
|llama3\.2:1b|If it is not possible to determine the part of speech from the input, the output should not contain the word "CantAnswer"\.|Sentence: My entirely customized interface\.W ord: entirely|For the first sentence:<br><br>No tag is available for "My", so return "Unknown"\.<br>The tag is "CC: Coordinating conjunction" but it's used as a subordinating conjunction to introduce the adverbial clause "entirely customized"\. <br>So, return "\-"\.<br><br>For the second sentence:<br><br>The tag is "CANTAnswer" which means this word cannot be tagged with any of the listed tags\. So, return "CantAnswer"\.|err|
|gpt\-4o\-mini|If it is not possible to determine the part of speech from the input, the output should not contain the word "CantAnswer"\.|Sentence: Envisioned unravels tomorrow\. Word: unravels|VBZ|ok|
|gemma2:9b|If it is not possible to determine the part of speech from the input, the output should not contain the word "CantAnswer"\.|Sentence: Envisioned unravels tomorrow\. Word: unravels|VBN|ok|
|qwen2\.5:3b|If it is not possible to determine the part of speech from the input, the output should not contain the word "CantAnswer"\.|Sentence: Envisioned unravels tomorrow\. Word: unravels|VBZ|ok|
|llama3\.2:1b|If it is not possible to determine the part of speech from the input, the output should not contain the word "CantAnswer"\.|Sentence: Envisioned unravels tomorrow\. Word: unravels|Word: unravels<br>Part of Speech: VBD|err|
|gpt\-4o\-mini|The output must contain additional information besides any specific part of speech tag or words such as "Unknown" and "CantAnswer"\.|Sentence: Buzzwords characterize strategy sadly\. Word: strategy|NN|ok|
|gemma2:9b|The output must contain additional information besides any specific part of speech tag or words such as "Unknown" and "CantAnswer"\.|Sentence: Buzzwords characterize strategy sadly\. Word: strategy|NN|ok|
|qwen2\.5:3b|The output must contain additional information besides any specific part of speech tag or words such as "Unknown" and "CantAnswer"\.|Sentence: Buzzwords characterize strategy sadly\. Word: strategy|NN|ok|
|llama3\.2:1b|The output must contain additional information besides any specific part of speech tag or words such as "Unknown" and "CantAnswer"\.|Sentence: Buzzwords characterize strategy sadly\. Word: strategy|Here are the part of speech tags for each word:<br><br>\- strategy: NN \(Noun\)<br>\- strategy: NN \(Noun\) <br><br>Since both words match, I will return WN \(Unknown\)\.|err|
|gpt\-4o\-mini|The output must contain additional information besides any specific part of speech tag or words such as "Unknown" and "CantAnswer"\.|Sentence: Conundrum solved strategically\. Word: Conundrum|NN|ok|
|gemma2:9b|The output must contain additional information besides any specific part of speech tag or words such as "Unknown" and "CantAnswer"\.|Sentence: Conundrum solved strategically\. Word: Conundrum|NN|ok|
|qwen2\.5:3b|The output must contain additional information besides any specific part of speech tag or words such as "Unknown" and "CantAnswer"\.|Sentence: Conundrum solved strategically\. Word: Conundrum|NN|ok|
|llama3\.2:1b|The output must contain additional information besides any specific part of speech tag or words such as "Unknown" and "CantAnswer"\.|Sentence: Conundrum solved strategically\. Word: Conundrum|Word: Conundrum<br> CC: Conundrum ADJ: \(returns "ADJ" since conundrum is an adjective\)<br><br>Word: Conundrum<br> ADJ: Conundrum NNP: Conundrum  \(returns "Conundrum NNP" since conundrum is a proper noun\)|err|
|gpt\-4o\-mini|The output must contain additional information besides any specific part of speech tag or words such as "Unknown" and "CantAnswer"\.|Sentence: Proficiently relinquished duties\. Word: Proficiently|RB|ok|
|gemma2:9b|The output must contain additional information besides any specific part of speech tag or words such as "Unknown" and "CantAnswer"\.|Sentence: Proficiently relinquished duties\. Word: Proficiently|RB|ok|
|qwen2\.5:3b|The output must contain additional information besides any specific part of speech tag or words such as "Unknown" and "CantAnswer"\.|Sentence: Proficiently relinquished duties\. Word: Proficiently|VB|ok|
|llama3\.2:1b|The output must contain additional information besides any specific part of speech tag or words such as "Unknown" and "CantAnswer"\.|Sentence: Proficiently relinquished duties\. Word: Proficiently|Part of speech tags:<br>\- CC: Coordinating conjunction<br>\- DT: Determiner|err|
|gpt\-4o\-mini|At least one word in the provided input must be omitted from tagging according to the conditions defined, and the output must ignore some of the listed scenarios appropriately\.|Sentence: Varied marbles on the floor\. Word: floor|NN|ok|
|gemma2:9b|At least one word in the provided input must be omitted from tagging according to the conditions defined, and the output must ignore some of the listed scenarios appropriately\.|Sentence: Varied marbles on the floor\. Word: floor|NN|ok|
|qwen2\.5:3b|At least one word in the provided input must be omitted from tagging according to the conditions defined, and the output must ignore some of the listed scenarios appropriately\.|Sentence: Varied marbles on the floor\. Word: floor|NN|ok|
|llama3\.2:1b|At least one word in the provided input must be omitted from tagging according to the conditions defined, and the output must ignore some of the listed scenarios appropriately\.|Sentence: Varied marbles on the floor\. Word: floor|Part of speech tags:<br><br>\* Floor: IN|err|
|gpt\-4o\-mini|At least one word in the provided input must be omitted from tagging according to the conditions defined, and the output must ignore some of the listed scenarios appropriately\.|Sentence: Clustered rings surround frequently\. Word: frequently|RB|ok|
|gemma2:9b|At least one word in the provided input must be omitted from tagging according to the conditions defined, and the output must ignore some of the listed scenarios appropriately\.|Sentence: Clustered rings surround frequently\. Word: frequently|RB|ok|
|qwen2\.5:3b|At least one word in the provided input must be omitted from tagging according to the conditions defined, and the output must ignore some of the listed scenarios appropriately\.|Sentence: Clustered rings surround frequently\. Word: frequently|VBZ|ok|
|llama3\.2:1b|At least one word in the provided input must be omitted from tagging according to the conditions defined, and the output must ignore some of the listed scenarios appropriately\.|Sentence: Clustered rings surround frequently\. Word: frequently|CC: Determiner<br>FREquently|err|
|gpt\-4o\-mini|At least one word in the provided input must be omitted from tagging according to the conditions defined, and the output must ignore some of the listed scenarios appropriately\.|Sentence: Astronomically relevant grids captivate\. Word: Astronomically|RB|ok|
|gemma2:9b|At least one word in the provided input must be omitted from tagging according to the conditions defined, and the output must ignore some of the listed scenarios appropriately\.|Sentence: Astronomically relevant grids captivate\. Word: Astronomically|JJ|ok|
|qwen2\.5:3b|At least one word in the provided input must be omitted from tagging according to the conditions defined, and the output must ignore some of the listed scenarios appropriately\.|Sentence: Astronomically relevant grids captivate\. Word: Astronomically|JJ|ok|
|llama3\.2:1b|At least one word in the provided input must be omitted from tagging according to the conditions defined, and the output must ignore some of the listed scenarios appropriately\.|Sentence: Astronomically relevant grids captivate\. Word: Astronomically|Word: Astronomically<br>Part of speech tag: ADJ<br><br>Note: The word "Astronomically" is an adverbial adjective\.|err|
|gpt\-4o\-mini||sentence: The quick brown fox jumps over the lazy dog\. word: jumps|VBZ|ok|
|gemma2:9b||sentence: The quick brown fox jumps over the lazy dog\. word: jumps|VBZ|ok|
|qwen2\.5:3b||sentence: The quick brown fox jumps over the lazy dog\. word: jumps|VBZ|ok|
|llama3\.2:1b||sentence: The quick brown fox jumps over the lazy dog\. word: jumps|Here are the part of speech tags for each word:<br><br>1\. jumps \- VBZ \(Verb, 3rd person singular present\)<br>2\. jumps \- VBD \(Verb, past tense\)|err|
|gpt\-4o\-mini||sentence: She has taken the book from the shelf\. word: taken|VBN|ok|
|gemma2:9b||sentence: She has taken the book from the shelf\. word: taken|VBN|ok|
|qwen2\.5:3b||sentence: She has taken the book from the shelf\. word: taken|VBZ|ok|
|llama3\.2:1b||sentence: She has taken the book from the shelf\. word: taken|For "taken":<br>CC: Subordinating conjunction<br><br>For "book":<br>NN: Noun|err|
|gpt\-4o\-mini||sentence: John loves Mary\. word: Mary|NN|ok|
|gemma2:9b||sentence: John loves Mary\. word: Mary|NNP|ok|
|qwen2\.5:3b||sentence: John loves Mary\. word: Mary|NN|ok|
|llama3\.2:1b||sentence: John loves Mary\. word: Mary|Word: NN \(Noun\)<br> Tagging Output: NN|err|
|gpt\-4o\-mini||sentence: There is a cat under the table\. word: There|EX|ok|
|gemma2:9b||sentence: There is a cat under the table\. word: There|EX|ok|
|qwen2\.5:3b||sentence: There is a cat under the table\. word: There|TO|ok|
|llama3\.2:1b||sentence: There is a cat under the table\. word: There|CC: Coordinating conjunction \(first instance\), CP: Prepositional phrase, JJ: Adjective, NN: Noun|err|
|gpt\-4o\-mini||sentence: The recipe calls for two eggs and a cup of sugar\. word: two|CD|ok|
|gemma2:9b||sentence: The recipe calls for two eggs and a cup of sugar\. word: two|CD|ok|
|qwen2\.5:3b||sentence: The recipe calls for two eggs and a cup of sugar\. word: two|JJ|ok|
|llama3\.2:1b||sentence: The recipe calls for two eggs and a cup of sugar\. word: two|Tags:<br>\- CC: Coordinating conjunction \(implied by "and"\)<br>\- RB: Adverb \(specifically, an adverb to indicate the relationship between "two" and "eggs"\) <br>\- JJ: Adjective \(in "recipe", describing "calls"\)|err|
|gpt\-4o\-mini||sentence: We will win that match\. word: win|VB|ok|
|gemma2:9b||sentence: We will win that match\. word: win|VB|ok|
|qwen2\.5:3b||sentence: We will win that match\. word: win|VBZ|ok|
|llama3\.2:1b||sentence: We will win that match\. word: win|For the given sentence "We will win that match" :<br><br>\- We \(Article\) is an Object\.<br>\- will \(Verb\)<br>\- win \(Base Verb Form\)<br><br>So, the part of speech tags for 'win' are VBZ and VBD\.|err|
|gpt\-4o\-mini||sentence: Paris is a beautiful city\. word: Paris|NNP|ok|
|gemma2:9b||sentence: Paris is a beautiful city\. word: Paris|NNP|ok|
|qwen2\.5:3b||sentence: Paris is a beautiful city\. word: Paris|NN|ok|
|llama3\.2:1b||sentence: Paris is a beautiful city\. word: Paris|Word: Paris <br>CC: NNPS <br><br> Sentence is the same as above\. <br>The only change is in word position which affects tag, in the sentence word "Paris" is not tagged correctly with any pos \(part of speech\) since the first time it was tagged \("NN"\) but then it gets replaced by \('NNPS'\)|err|
|gpt\-4o\-mini||sentence: They quickly ran towards the finish line\. word: quickly|RB|ok|
|gemma2:9b||sentence: They quickly ran towards the finish line\. word: quickly|RB|ok|
|qwen2\.5:3b||sentence: They quickly ran towards the finish line\. word: quickly|VB️|err|
|llama3\.2:1b||sentence: They quickly ran towards the finish line\. word: quickly|Word: Quickly <br> Tag: VRB \(Verb\-Subj\)<br><br><br>Word: they<br> Tag: PRP \(Personal pronoun\)|err|
|gpt\-4o\-mini||sentence: These are the best cookies I have ever tasted\. word: best|JJS|ok|
|gemma2:9b||sentence: These are the best cookies I have ever tasted\. word: best|JJS|ok|
|qwen2\.5:3b||sentence: These are the best cookies I have ever tasted\. word: best|JJ|ok|
|llama3\.2:1b||sentence: These are the best cookies I have ever tasted\. word: best|CC: <br>tagged as Coordinating conjunction <br><br>CantAnswer|err|
|gpt\-4o\-mini||sentence: Can you find the hidden treasure? word: hidden|JJ|ok|
|gemma2:9b||sentence: Can you find the hidden treasure? word: hidden|JJ|ok|
|qwen2\.5:3b||sentence: Can you find the hidden treasure? word: hidden|VBG|ok|
|llama3\.2:1b||sentence: Can you find the hidden treasure? word: hidden|\* CC: Coordinating conjunction \(twice, once at the beginning and again as a coordinating conjunction within the sentence\)<br>\* EX: Existential there \(not present in this instance but would be if 'hidden' were used as an existential verb\)<br><br>However, since 'hidden' is the word being tagged as it has to do with its position or part of speech in the given sentences, we can just state that:<br><br>\* JJR: Adjective superlative|err|
|gpt\-4o\-mini||sentence: The children play happily in the park\. word: happily|RB|ok|
|gemma2:9b||sentence: The children play happily in the park\. word: happily|RB|ok|
|qwen2\.5:3b||sentence: The children play happily in the park\. word: happily|RB|ok|
|llama3\.2:1b||sentence: The children play happily in the park\. word: happily|Here are the part of speech tags for each word:<br><br>\* Happily: ADJ \(Adjective\)<br>\* In: IN \(Preposition or subordinating conjunction\)|err|
|gpt\-4o\-mini||sentence: He went to the store yesterday\. word: yesterday|RB|ok|
|gemma2:9b||sentence: He went to the store yesterday\. word: yesterday|RB|ok|
|qwen2\.5:3b||sentence: He went to the store yesterday\. word: yesterday|JJ|ok|
|llama3\.2:1b||sentence: He went to the store yesterday\. word: yesterday|No match is found in the list of tagged parts of speech for the given words\.<br><br>CantAnswer|err|
|gpt\-4o\-mini||sentence: Will you be coming with us? word: Will|MD|ok|
|gemma2:9b||sentence: Will you be coming with us? word: Will|MD|ok|
|qwen2\.5:3b||sentence: Will you be coming with us? word: Will|VB|ok|
|llama3\.2:1b||sentence: Will you be coming with us? word: Will|\*\*Part\-of\-speech tag for "Will" : JD\*\*<br><br>There is only one occurrence of the word "Will"\. The correct analysis results in a single JD \(Adjective\) tag for the entire sentence, but since there are no other parts that can change it, the individual JD remains as given\.|err|
|gpt\-4o\-mini||sentence: Please hand me the blue folder\. word: blue|JJ|ok|
|gemma2:9b||sentence: Please hand me the blue folder\. word: blue|JJ|ok|
|qwen2\.5:3b||sentence: Please hand me the blue folder\. word: blue|JJ|ok|
|llama3\.2:1b||sentence: Please hand me the blue folder\. word: blue|\* For the sentence "Please hand me the blue folder," <br>\+ POS: DT \(Determiner\)<br>\* For the same sentence, <br>\+ VS: VBD \(Verb, past tense of Hand\)|err|
|gpt\-4o\-mini||sentence: The test was incredibly difficult\. word: was|VBD|ok|
|gemma2:9b||sentence: The test was incredibly difficult\. word: was|VBD|ok|
|qwen2\.5:3b||sentence: The test was incredibly difficult\. word: was|VBZ|ok|
|llama3\.2:1b||sentence: The test was incredibly difficult\. word: was|Word: was<br>\- was \(IN\)|err|
|gpt\-4o\-mini||sentence: She doesn't know what to do\. word: what|WP|ok|
|gemma2:9b||sentence: She doesn't know what to do\. word: what|WDT|ok|
|qwen2\.5:3b||sentence: She doesn't know what to do\. word: what|WH\-to|err|
|llama3\.2:1b||sentence: She doesn't know what to do\. word: what|For the given sentence and word:<br><br>\- The word "what" can be tagged as NNS \(Noun, plural\), because it is a mass noun referring to something\.<br> <br>The part\-of\-speech tags for "She doesn't know what to do": NNS\.|err|
|gpt\-4o\-mini||sentence: A flock of birds flew overhead\. word: flock|NN|ok|
|gemma2:9b||sentence: A flock of birds flew overhead\. word: flock|NN|ok|
|qwen2\.5:3b||sentence: A flock of birds flew overhead\. word: flock|NN|ok|
|llama3\.2:1b||sentence: A flock of birds flew overhead\. word: flock|Part\-of\-speech tag for "flock" \- Noun<br><br>Part\-of\-speech tag for "flock" \(second occurrence\) \- NN \(Proper noun, singular or mass\)|err|
|gpt\-4o\-mini||sentence: Sam and Pete are going to the conference\. word: and|CC|ok|
|gemma2:9b||sentence: Sam and Pete are going to the conference\. word: and|CC|ok|
|qwen2\.5:3b||sentence: Sam and Pete are going to the conference\. word: and|CC|ok|
|llama3\.2:1b||sentence: Sam and Pete are going to the conference\. word: and|Part of speech tag for word "and": CC \(Coordinating conjunction\)|err|
|gpt\-4o\-mini||sentence: I need a pen and paper\. word: pen|NN|ok|
|gemma2:9b||sentence: I need a pen and paper\. word: pen|NN|ok|
|qwen2\.5:3b||sentence: I need a pen and paper\. word: pen|NN|ok|
|llama3\.2:1b||sentence: I need a pen and paper\. word: pen|\* For the sentence "I need a pen and paper\." <br>  The tag for 'pen' is VB \(Base form\)\.<br><br>\* For the sentence "I need a pen"<br>  The tag for 'pen' is VB \(Base form\)\. <br><br>Since both cases match with VB, I will return VB as the tag\.|err|
|gpt\-4o\-mini||sentence: Which route should we take? word: Which|WDT|ok|
|gemma2:9b||sentence: Which route should we take? word: Which|WDT|ok|
|qwen2\.5:3b||sentence: Which route should we take? word: Which|WP|ok|
|llama3\.2:1b||sentence: Which route should we take? word: Which|tag: IN \(Determiner\) and JJ \(Adjective\)<br><br>result: INJJ|err|
|gpt\-4o\-mini||sentence: The process is extremely complicated\. word: extremely|RB|ok|
|gemma2:9b||sentence: The process is extremely complicated\. word: extremely|RB|ok|
|qwen2\.5:3b||sentence: The process is extremely complicated\. word: extremely|RB|ok|
|llama3\.2:1b||sentence: The process is extremely complicated\. word: extremely|\*Process\* \- VBZ<br>\*extremely\* \- JJ|err|
|gpt\-4o\-mini||sentence: We have been friends for many years\. word: been|VBN|ok|
|gemma2:9b||sentence: We have been friends for many years\. word: been|VBN|ok|
|qwen2\.5:3b||sentence: We have been friends for many years\. word: been|VBZ|ok|
|llama3\.2:1b||sentence: We have been friends for many years\. word: been|\*\*Word:\*\* been<br>\*\*Tag:\*\* VC \(Verb\-Subject\) <br><br>\(Verbs are not explicitly tagged, but can be inferred as the subject of "We", which is CC in this case\.\)|err|
|gpt\-4o\-mini||sentence: This is my car\. word: my|PRP$|ok|
|gemma2:9b||sentence: This is my car\. word: my|PRP$|ok|
|qwen2\.5:3b||sentence: This is my car\. word: my|PRP$|ok|
|llama3\.2:1b||sentence: This is my car\. word: my|Here are the part of speech tags for each word:<br><br>\* "This" \- DT: Determiner<br>\* "is" \- VBZ: Verb, 3rd person singular present \(tag:Verb\+Sing\.\)<br>\* "my" \- CC: Coordinating conjunction <br><br>Let me know if you have any further requests\.|err|
|gpt\-4o\-mini||sentence: Have you seen their new house yet? word: their|PRP$|ok|
|gemma2:9b||sentence: Have you seen their new house yet? word: their|PRP$|ok|
|qwen2\.5:3b||sentence: Have you seen their new house yet? word: their|their<br>NN|ok|
|llama3\.2:1b||sentence: Have you seen their new house yet? word: their|\* CC: Coordinating conjunction\. <br>\* IN: Determiner\.<br>\* Their|err|
|gpt\-4o\-mini||sentence: Oh no, I forgot my homework at home\. word: Oh|UH|ok|
|gemma2:9b||sentence: Oh no, I forgot my homework at home\. word: Oh|UH|ok|
|qwen2\.5:3b||sentence: Oh no, I forgot my homework at home\. word: Oh|Unknown|ok|
|llama3\.2:1b||sentence: Oh no, I forgot my homework at home\. word: Oh|Sentence: Oh =gt; ORG : Interjection<br><br>Word: Oh =gt; PRM : Personal pronoun|err|
|gpt\-4o\-mini||sentence: Each student should bring a notebook\. word: Each|DT|ok|
|gemma2:9b||sentence: Each student should bring a notebook\. word: Each|DT|ok|
|qwen2\.5:3b||sentence: Each student should bring a notebook\. word: Each|DT|ok|
|llama3\.2:1b||sentence: Each student should bring a notebook\. word: Each|\* Part of speech tag for "Each": Noun|err|
|gpt\-4o\-mini||sentence: The sun rises in the east\. word: rises|VBZ|ok|
|gemma2:9b||sentence: The sun rises in the east\. word: rises|VZB|err|
|qwen2\.5:3b||sentence: The sun rises in the east\. word: rises|VBZ|ok|
|llama3\.2:1b||sentence: The sun rises in the east\. word: rises|Part\-of\-speech tag for 'rises': VBZ<br><br>Part\-of\-speech tag for 'The' or 'east': DT <br><br>Part\-of\-speech tag for 'suns': CC|err|
|gpt\-4o\-mini||sentence: Can someone explain this to me? word: explain|VB|ok|
|gemma2:9b||sentence: Can someone explain this to me? word: explain|VB|ok|
|qwen2\.5:3b||sentence: Can someone explain this to me? word: explain|VB️|err|
|llama3\.2:1b||sentence: Can someone explain this to me? word: explain|Part\-of\-speech tags for the given words are:<br><br>\* Explain: JJR: Adjective, comparative, JJS: Adjective, superlative \(superlative is plural form, but in this case, we have "explanation" as a whole which makes it singular\)<br><br>Since it's only describing a noun and there isn't any other adjective provided, the tag for just 'explain' is JJR\.|err|
|gpt\-4o\-mini||sentence: Despite the warnings, they proceeded with the plan\. word: Despite|IN|ok|
|gemma2:9b||sentence: Despite the warnings, they proceeded with the plan\. word: Despite|IN|ok|
|qwen2\.5:3b||sentence: Despite the warnings, they proceeded with the plan\. word: Despite|TO|ok|
|llama3\.2:1b||sentence: Despite the warnings, they proceeded with the plan\. word: Despite|POS: adverb<br><br>Reasoning:<br>Since "Despite" is a functional adjective used to introduce a contrasting clause or an expression that contrasts an action or situation present in one part of the sentence with one that is not, it can be tagged as adverb, despite the presence of other parts of speech like NP and CC\.|err|
|gpt\-4o\-mini||sentence: We have been waiting for hours\. word: hours|NNS|ok|
|gemma2:9b||sentence: We have been waiting for hours\. word: hours|CD|ok|
|qwen2\.5:3b||sentence: We have been waiting for hours\. word: hours|NN|ok|
|llama3\.2:1b||sentence: We have been waiting for hours\. word: hours|CC: \(Hours is a coordinate phrase\)<br>DT: \(Hours are\)<br>EX: <br>JJR: Adjective \(positive\)<br>JJS: Adjective \(superlativedelete\) <br>NNS: Noun 'hours'|err|
|gpt\-4o\-mini||sentence: The delicious aroma filled the kitchen\. word: aroma|NN|ok|
|gemma2:9b||sentence: The delicious aroma filled the kitchen\. word: aroma|NN|ok|
|qwen2\.5:3b||sentence: The delicious aroma filled the kitchen\. word: aroma|NN|ok|
|llama3\.2:1b||sentence: The delicious aroma filled the kitchen\. word: aroma|For the word "aroma":<br>PPS: Proper possessive ending<br><br>For the word "filled", <br>IN: Preposition or subordinating conjunction<br> <br>As both words can be tagged with IN, it's not possible to determine a definite part of speech for one word alone\.|err|
|gpt\-4o\-mini||sentence: The committee dissolved the party\. word: dissolved|VBD|ok|
|gemma2:9b||sentence: The committee dissolved the party\. word: dissolved|VBD|ok|
|qwen2\.5:3b||sentence: The committee dissolved the party\. word: dissolved|VBZ|ok|
|llama3\.2:1b||sentence: The committee dissolved the party\. word: dissolved|Part\-of\-speech tag for "dissolved": CC \(Conjunction\)<br><br>Part\-of\-speech tag for "dissolved": NN \(Noun\)|err|
|gpt\-4o\-mini||sentence: You should definitely try this dish\. word: definitely|RB|ok|
|gemma2:9b||sentence: You should definitely try this dish\. word: definitely|RB|ok|
|qwen2\.5:3b||sentence: You should definitely try this dish\. word: definitely|RB|ok|
|llama3\.2:1b||sentence: You should definitely try this dish\. word: definitely|\*\*Word: definitively\*\*<br>\* Tag: ADVERB|err|
|gpt\-4o\-mini||sentence: An apple a day keeps the doctor away\. word: An|DT|ok|
|gemma2:9b||sentence: An apple a day keeps the doctor away\. word: An|DT|ok|
|qwen2\.5:3b||sentence: An apple a day keeps the doctor away\. word: An|WP|ok|
|llama3\.2:1b||sentence: An apple a day keeps the doctor away\. word: An|CC: Coordinating conjunction<br>Word part of speech: <br>Det \(Determiner\)|err|
|gpt\-4o\-mini||sentence: Let me rest for a while\. word: rest|VB|ok|
|gemma2:9b||sentence: Let me rest for a while\. word: rest|VB|ok|
|qwen2\.5:3b||sentence: Let me rest for a while\. word: rest|NN|ok|
|llama3\.2:1b||sentence: Let me rest for a while\. word: rest|For the sentence "Let me rest for a while", the part of speech tag is:<br>JJR \(Adjective, comparative\)|err|
|gpt\-4o\-mini||sentence: The quick brown fox jumps over the lazy dog\. word: fox|NN|ok|
|gemma2:9b||sentence: The quick brown fox jumps over the lazy dog\. word: fox|NN|ok|
|qwen2\.5:3b||sentence: The quick brown fox jumps over the lazy dog\. word: fox|NN|ok|
|llama3\.2:1b||sentence: The quick brown fox jumps over the lazy dog\. word: fox|CC: noun<br><br><br>The word "fox" is a common noun referring to a type of animal\.|err|
|gpt\-4o\-mini||sentence: She has a unique perspective on life\. word: unique|JJ|ok|
|gemma2:9b||sentence: She has a unique perspective on life\. word: unique|JJ|ok|
|qwen2\.5:3b||sentence: She has a unique perspective on life\. word: unique|JJ|ok|
|llama3\.2:1b||sentence: She has a unique perspective on life\. word: unique|Word: unique <br> Tag: JJ|ok|
|gpt\-4o\-mini||sentence: It suddenly started raining\. word: suddenly|RB|ok|
|gemma2:9b||sentence: It suddenly started raining\. word: suddenly|RB|ok|
|qwen2\.5:3b||sentence: It suddenly started raining\. word: suddenly|RB|ok|
|llama3\.2:1b||sentence: It suddenly started raining\. word: suddenly|Here are the part of speech tags for the given words:<br><br>1\. Suddenly \- NN \(Noun\)<br>2\. Suddenly \- JJ \(Adjective\)|err|
|gpt\-4o\-mini||sentence: How often do you visit your hometown? word: often|RB|ok|
|gemma2:9b||sentence: How often do you visit your hometown? word: often|RB|ok|
|qwen2\.5:3b||sentence: How often do you visit your hometown? word: often|VB|ok|
|llama3\.2:1b||sentence: How often do you visit your hometown? word: often|\* POS: NNP \(Proper noun\)<br>\* tag for NN in sentence 1: N<br>\* tag for NN in sentence 2: N <br><br>Since both words share the same part of speech, their tags are identical\. If I had more sentences to analyze, I would need further information about them\.<br><br>If you provide more text, I can help with your original request\.|err|
|gpt\-4o\-mini||sentence: Alas, we have no choice\. word: Alas|UH|ok|
|gemma2:9b||sentence: Alas, we have no choice\. word: Alas|UH|ok|
|qwen2\.5:3b||sentence: Alas, we have no choice\. word: Alas|RB|ok|
|llama3\.2:1b||sentence: Alas, we have no choice\. word: Alas|\* CC: Determiner<br>\* CC:CantAnswer <br> \* SYM: Symbol|err|
|gpt\-4o\-mini||sentence: If you believe, you can achieve\. word: If|CC|ok|
|gemma2:9b||sentence: If you believe, you can achieve\. word: If|IN|ok|
|qwen2\.5:3b||sentence: If you believe, you can achieve\. word: If|TO|ok|
|llama3\.2:1b||sentence: If you believe, you can achieve\. word: If|Word: If<br><br>Part of speech tags: CC \(Coordinating conjunction\), SYM \(Symbol\), RB \(Adverb\)|err|
|gpt\-4o\-mini||sentence: The vase broke into pieces\. word: pieces|NNS|ok|
|gemma2:9b||sentence: The vase broke into pieces\. word: pieces|NNS|ok|
|qwen2\.5:3b||sentence: The vase broke into pieces\. word: pieces|NN|ok|
|llama3\.2:1b||sentence: The vase broke into pieces\. word: pieces|Sentence: The vase broke into pieces\.<br><br>\* CC: Coordinating conjunction \(none\)<br>\* CD: Cardinal number \(none\)<br>\* DT: Determiner \(none\)<br>\* EX: Existential there \(none\)<br>\* FW: Foreign word \(?\)<br>\* IN: Preposition or subordinating conjunction \(none\)<br>\* JJ: Adjective \(pieces\)<br>\* JJJ: Adjective, comparative and superlative \(none\)<br>\* LS: List item marker \(?\) \(none\)<br>\* MD: Modal \(none\)<br>\* NN: Noun \(pieces\)<br>\* NS: Noun, plural \(pieces\)<br>\* NP: Not in sentence<br>\* NNP: Proper noun, singular \(The vase\)<br>\* SS: Syntactic specification \(none\), Singular \- 2 \( pieces \)<br>\* WD: Wh\-determiner \(?\), Who \( none\)<br>\* WP: Wh\-pronoun \(?\) or possessive wh\-pronoun<br>\* VP: Verb phrase \(broken into\)<br><br> Tagging returned NNP which is a proper noun|err|

### [intent.txt](./intent.txt)

`````txt
Determine the part of speech for a given word.
`````


### [input_spec.txt](./input_spec.txt)

`````txt
The input is a string that includes a sentence and one word from that sentence.  
The sentence must be a grammatically correct English sentence.  
The word must be present within the sentence provided.  
The word can be any part of speech, including noun, verb, adjective, or others.  
The word must not be an empty string.  
The sentence must not be an empty string.  
The sentence may include punctuation.   
The word must not include punctuation signs.  
There is no specified maximum length for the sentence.  
There is no specified maximum length for the word.  
`````


### [rules.txt](./rules.txt)

`````txt
1: The output must only contain a single part of speech tag from the pre-defined list in the system prompt. 
2: The output must be an exact match to one of the tags in the pre-defined list, if applicable. 
3: If the word provided in the input can be matched to one of the listed part of speech tags, return only the corresponding tag as the output, with no additional text or formatting. 
4: If the word provided in the input cannot be assigned any of the listed part of speech tags, the output should only contain the word "Unknown". 
5: If it is not possible to determine the part of speech from the input, the output should only contain the word "CantAnswer". 
6: The output must contain no additional information besides the specified part of speech tag or the exact words "Unknown" or "CantAnswer" based on the given rules. 
7: Every word in the provided input must be attempted to be tagged according to the conditions defined, and the output must reflect one of the listed scenarios appropriately.
`````


### [inverse_rules.txt](./inverse_rules.txt)

`````txt
8: The output must contain multiple parts of speech tags that are not from the pre-defined list in the system prompt. 
9: The output must not match any of the tags in the pre-defined list, where applicable. 
10: If the word provided in the input can be matched to one of the listed part of speech tags, return additional text and formatting rather than the corresponding tag. 
11: If the word provided in the input cannot be assigned any of the listed part of speech tags, the output should not contain the word "Unknown". 
12: If it is not possible to determine the part of speech from the input, the output should not contain the word "CantAnswer". 
13: The output must contain additional information besides any specific part of speech tag or words such as "Unknown" and "CantAnswer". 
14: At least one word in the provided input must be omitted from tagging according to the conditions defined, and the output must ignore some of the listed scenarios appropriately.
`````


### [tests.csv](./tests.csv)

|testinput|expectedoutput|reasoning|
|-|-|-|
|Sentence: The quick brown fox jumps over the lazy dog\. Word: fox|NN|The input word 'fox' is a noun and the expected output is the single part of speech tag 'NN', adhering to the rule that only one tag from the predefined list should be produced\.|
|Sentence: She sells seashells by the seashore\. Word: sells|VBZ|The word 'sells' functions as a verb, third person singular present, so 'VBZ' is the appropriate tag, following the rule of single tag output\.|
|Sentence: Yesterday, it rained heavily\. Word: rained|VBD|The word 'rained' is in past tense, thus 'VBD' is the expected part of speech tag, illustrating correct compliance with the rule\.|
|Sentence: The cat sat on the mat\. Word: cat|NN|The word 'cat' is a noun and must match exactly to the tag 'NN', confirming the rule of matching the predefined list exactly\.|
|Sentence: Birds fly high\. Word: fly|VB|The word 'fly' when used as a verb in base form should return the exact match 'VB', validating the rule that output should be exact\.|
|Sentence: One hundred apples fell\. Word: hundred|CD|Describes number and hence, 'CD' representing cardinal number should match exactly, confirming the rule of exact matching to predefined tags\.|
|Sentence: A large tree fell\. Word: large|JJ|Since the word 'large' functions as an adjective and is tagged as 'JJ', this should be the only output, adhering strictly to the policy of no additional text\.|
|Sentence: I usually walk home\. Word: usually|RB|The word 'usually' is an adverb tagged as 'RB', confirming compliance by having no extra text beyond the tag\.|
|Sentence: They have been healthy\. Word: have|VB|The given word 'have', matched correctly as a base form verb, should only yield 'VB', showing adherence to not including excess information\.|
|Sentence: Everything went according to the plan\. Word: according|IN|The word 'according', correctly tagged as a preposition should return 'IN' and highlight scenarios where the tag exists, without being 'Unknown'\.|
|Sentence: The session was remarkable\. Word: sessione|Unknown|Evidently 'sessione' is not recognizable in English, thereby legitimately giving 'Unknown', reinforcing non\-recognizable scenario handling\.|
|Sentence: My new routine will adapt\. Word: xyzzy|Unknown|The gibberish word 'xyzzy' fails to match any known tag thus rendering 'Unknown', showing capability of returning result for nonsense inputs\.|
|Sentence: This sentence cannot be processed\. Word: unprocesable|CantAnswer|The misspelled 'unprocesable' does not relate to expected tags, commanding 'CantAnswer' to be issued, indicating when detection fails\.|
|Sentence: A complex wordplay occurred here\. Word: qwertyuiop|CantAnswer|Given 'qwertyuiop' is not definable, the output being 'CantAnswer' underlines situations where interpretation is impossible\.|
|Sentence: Many colorful dreams arise unhindered\. Word: ljfdksjl|CantAnswer|When the word 'ljfdksjl' lacks interpretation, 'CantAnswer' rightly gets exhibited, confirming response limitation is followed\.|
|Sentence: Their experiment succeeded\. Word: succeeded|VBD|Accentuates the rule that limits output strictly to tags or conditions 'Unknown' or 'CantAnswer' only, herein verifying verb in past tense as 'VBD'\.|
|Sentence: Appreciate the colors of the wind\. Word: colors|NNS|With output solely being 'NNS', aligns with the criteria that forbids any additional non\-essential output in consequences\.|
|Sentence: She can solve the mystery alone\. Word: can|MD|The term 'can' functions as a modal verb tagged accurately as 'MD', enforcing the non\-variegated output philosophy\.|
|Sentence: He quickly understood the situation\. Word: quickly|RB|Demonstrates that appropriate tagging attempts were made with resultant 'RB' without any disregarded testing procedures\.|
|Sentence: They left yesterday\. Word: yesterday|RB|Confirms the distinct endeavor that pinpointed yesterday increasing the assurance for respective part\-of\-speech assignment without oversight\.|
|Sentence: Imagine a brighter future\. Word: Imagine|VB|Accent on 'Imagine' reflects the provision to always thoroughly try and attain a valid tag, such as the base form verb 'VB'\.|
|Sentence: The plan was executed hurrily\. Word: hurrily|Unknown|Signifies erroneous output with the invented 'hurrily', prompting reflective unauthorized tags proving negligence in using peer cues\.|
|Sentence: Welcome to zzyzx road\. Word: zzyzx|Unknown|Presents input where no pre\-defined keys are used yet 'Unknown' emerges, thus unexpectedly showing formulated response usage disallowed\.|
|Sentence: I coined murf the word\. Word: murf|Unknown|Highlights input component straying from the list yet improperly turning 'Unknown', which should strictly emerge from learned exclusions\.|
|Sentence: That is unanticipatedly concise\. Word: unanticipatedly|Unknown|Every output should result from a comprehensive list evaluation exposing absence yet fosters an alignable 'Unknown'\.|
|Sentence: Her demeanor was inaccesible\.|Unknown|Features illusion of unaffiliated token grouping, expecting yet failure underscores non\-adherence provoking distinct alignment necessity\.|
|Sentence: There are many colours in this art\.|Unknown|Bears accidental non\-match expected to crystalline alignment yet assuming deviation renders non\-standard clarity\.|
|Sentence: Mist in the valley is enchanting\. Word: enchanting|JJ enchanting|Furnishes scrutiny towards textual additions disallowed yet naively unscathed visual discovery isolating explicitness needed\.|
|Sentence: Laughter echoed through hall endlessly\. Word: endlessly|RB \- Adverb|Presents over\-encompassing deviation where despite a recognized form as 'RB', ticketed adjective 'Adverb' found needlessly\.|
|Sentence: Eagerly awaited\. Word: awaited|VBN Verb|Compounds perceivable invitation to liberate and accrete additional uncommissioned verbosity infringing governed constraints\.|
|Sentence: The unexplained phenomenon\. Word: unexplained|Adjective|Entrusts unauthorized subsystem outputs symphonizing unidentified responses expecting accurate returns of norm catches criticized\.|
|Sentence: Uncharted discoveries multiplied\. Word: uncharted|Adjective|JNI bridges confusingly monotonic fixature demands unfavourable circumstantial phrases disabled fostering secure corpus insights\.|
|Sentence: Freshly baked cookies\. Word: baked||Implicates spurious result outcome orientations yet straightly paralleled facilitating illustrative non\-distorted paradigms reserved over disclosures\.|
|Sentence: My non\-conclusive sentence\. Word: non\-conclusive||Subjectively 'CantAnswer' illicit deviation requested momentarily self discovers through invalidations new believable idle lock\-in\.|
|Sentence: My entirely customized interface\.W ord: entirely||Documented void conviction withheld imagined vocalizations ambling sequestered strongly configured norms fulfilled base sobering context\.|
|Sentence: Envisioned unravels tomorrow\. Word: unravels||Insignificantly trust project digest challenging submission showcases awaiting capsule without developed genre contrasting centric adoption paradigms\.|
|Sentence: Buzzwords characterize strategy sadly\. Word: strategy|NN: Noun|Advises covert dispatch charter unprecedent illustrating derived adjacency need outward literal temporary overtly centric alternations\.|
|Sentence: Conundrum solved strategically\. Word: Conundrum|NN|Surveys insistent conflicting motivability resonating styles delegated facing overwhelming omnipresent subtleties specificity unaligned suffrage reality\.|
|Sentence: Proficiently relinquished duties\. Word: Proficiently|Unknown|Speculatively circumnavigating cancelling doubts outward defining tenancy indication prior grasped synergy elaborative intent cancel accountability\.|
|Sentence: Varied marbles on the floor\. Word: floor|NN|Distracts shunning paired co\-dependent actionable contributions locked encounters isolated authenticity accurately reclaim cognitive shielding allowances\.|
|Sentence: Clustered rings surround frequently\. Word: frequently|RB|Warrants clarifying forming initiated designed exact calculated transmission dual remakes managing lifting snapshot catalog silhouette\.|
|Sentence: Astronomically relevant grids captivate\. Word: Astronomically|RB|Resonates harnessed entirety activation postured misleading omniscient inversion transcend hopping small vibrant cosmic prominence destined allure\.|

### [test_evals.csv](./test_evals.csv)

|rule|model|input|coverage|validity|
|-|-|-|-|-|
|The output must only contain a single part of speech tag from the pre\-defined list in the system prompt\.|gpt\-4o\-2024\-08\-06|Sentence: The quick brown fox jumps over the lazy dog\. Word: fox|Noun|ok|
|The output must only contain a single part of speech tag from the pre\-defined list in the system prompt\.|gpt\-4o\-2024\-08\-06|Sentence: She sells seashells by the seashore\. Word: sells|Verb|ok|
|The output must only contain a single part of speech tag from the pre\-defined list in the system prompt\.|gpt\-4o\-2024\-08\-06|Sentence: Yesterday, it rained heavily\. Word: rained|Verb|ok|
|The output must be an exact match to one of the tags in the pre\-defined list, if applicable\.|gpt\-4o\-2024\-08\-06|Sentence: The cat sat on the mat\. Word: cat|Noun|ok|
|The output must be an exact match to one of the tags in the pre\-defined list, if applicable\.|gpt\-4o\-2024\-08\-06|Sentence: Birds fly high\. Word: fly|Verb|ok|
|The output must be an exact match to one of the tags in the pre\-defined list, if applicable\.|gpt\-4o\-2024\-08\-06|Sentence: One hundred apples fell\. Word: hundred|Adjective|ok|
|If the word provided in the input can be matched to one of the listed part of speech tags, return only the corresponding tag as the output, with no additional text or formatting\.|gpt\-4o\-2024\-08\-06|Sentence: A large tree fell\. Word: large|Adjective|ok|
|If the word provided in the input can be matched to one of the listed part of speech tags, return only the corresponding tag as the output, with no additional text or formatting\.|gpt\-4o\-2024\-08\-06|Sentence: I usually walk home\. Word: usually|Adverb|ok|
|If the word provided in the input can be matched to one of the listed part of speech tags, return only the corresponding tag as the output, with no additional text or formatting\.|gpt\-4o\-2024\-08\-06|Sentence: They have been healthy\. Word: have|Verb|ok|
|If the word provided in the input cannot be assigned any of the listed part of speech tags, the output should only contain the word "Unknown"\.|gpt\-4o\-2024\-08\-06|Sentence: Everything went according to the plan\. Word: according|Preposition|ok|
|If the word provided in the input cannot be assigned any of the listed part of speech tags, the output should only contain the word "Unknown"\.|gpt\-4o\-2024\-08\-06|Sentence: The session was remarkable\. Word: sessione|Unknown|err|
|If the word provided in the input cannot be assigned any of the listed part of speech tags, the output should only contain the word "Unknown"\.|gpt\-4o\-2024\-08\-06|Sentence: My new routine will adapt\. Word: xyzzy|Unknown|err|
|If it is not possible to determine the part of speech from the input, the output should only contain the word "CantAnswer"\.|gpt\-4o\-2024\-08\-06|Sentence: This sentence cannot be processed\. Word: unprocesable|Unknown|err|
|If it is not possible to determine the part of speech from the input, the output should only contain the word "CantAnswer"\.|gpt\-4o\-2024\-08\-06|Sentence: A complex wordplay occurred here\. Word: qwertyuiop|Unknown|err|
|If it is not possible to determine the part of speech from the input, the output should only contain the word "CantAnswer"\.|gpt\-4o\-2024\-08\-06|Sentence: Many colorful dreams arise unhindered\. Word: ljfdksjl|Unknown|err|
|The output must contain no additional information besides the specified part of speech tag or the exact words "Unknown" or "CantAnswer" based on the given rules\.|gpt\-4o\-2024\-08\-06|Sentence: Their experiment succeeded\. Word: succeeded|Verb|ok|
|The output must contain no additional information besides the specified part of speech tag or the exact words "Unknown" or "CantAnswer" based on the given rules\.|gpt\-4o\-2024\-08\-06|Sentence: Appreciate the colors of the wind\. Word: colors|Noun|ok|
|The output must contain no additional information besides the specified part of speech tag or the exact words "Unknown" or "CantAnswer" based on the given rules\.|gpt\-4o\-2024\-08\-06|Sentence: She can solve the mystery alone\. Word: can|ModalVerb|ok|
|Every word in the provided input must be attempted to be tagged according to the conditions defined, and the output must reflect one of the listed scenarios appropriately\.|gpt\-4o\-2024\-08\-06|Sentence: He quickly understood the situation\. Word: quickly|Adverb|ok|
|Every word in the provided input must be attempted to be tagged according to the conditions defined, and the output must reflect one of the listed scenarios appropriately\.|gpt\-4o\-2024\-08\-06|Sentence: They left yesterday\. Word: yesterday|Adverb|ok|
|Every word in the provided input must be attempted to be tagged according to the conditions defined, and the output must reflect one of the listed scenarios appropriately\.|gpt\-4o\-2024\-08\-06|Sentence: Imagine a brighter future\. Word: Imagine|Verb|ok|
|The output must contain multiple parts of speech tags that are not from the pre\-defined list in the system prompt\.|gpt\-4o\-2024\-08\-06|Sentence: The plan was executed hurrily\. Word: hurrily|Unknown|err|
|The output must contain multiple parts of speech tags that are not from the pre\-defined list in the system prompt\.|gpt\-4o\-2024\-08\-06|Sentence: Welcome to zzyzx road\. Word: zzyzx|Unknown|ok|
|The output must contain multiple parts of speech tags that are not from the pre\-defined list in the system prompt\.|gpt\-4o\-2024\-08\-06|Sentence: I coined murf the word\. Word: murf|Unknown|ok|
|The output must not match any of the tags in the pre\-defined list, where applicable\.|gpt\-4o\-2024\-08\-06|Sentence: That is unanticipatedly concise\. Word: unanticipatedly|Adverb|ok|
|The output must not match any of the tags in the pre\-defined list, where applicable\.|gpt\-4o\-2024\-08\-06|Sentence: Her demeanor was inaccesible\.|Input: Her  <br>Output: PRON  <br><br>Input: demeanor  <br>Output: NOUN  <br><br>Input: was  <br>Output: AUX  <br><br>Input: inaccesible  <br>Output: ADJ|err|
|The output must not match any of the tags in the pre\-defined list, where applicable\.|gpt\-4o\-2024\-08\-06|Sentence: There are many colours in this art\.|Determiner|err|
|If the word provided in the input can be matched to one of the listed part of speech tags, return additional text and formatting rather than the corresponding tag\.|gpt\-4o\-2024\-08\-06|Sentence: Mist in the valley is enchanting\. Word: enchanting|Adjective|ok|
|If the word provided in the input can be matched to one of the listed part of speech tags, return additional text and formatting rather than the corresponding tag\.|gpt\-4o\-2024\-08\-06|Sentence: Laughter echoed through hall endlessly\. Word: endlessly|Adverb|err|
|If the word provided in the input can be matched to one of the listed part of speech tags, return additional text and formatting rather than the corresponding tag\.|gpt\-4o\-2024\-08\-06|Sentence: Eagerly awaited\. Word: awaited|Verb|ok|
|If the word provided in the input cannot be assigned any of the listed part of speech tags, the output should not contain the word "Unknown"\.|gpt\-4o\-2024\-08\-06|Sentence: The unexplained phenomenon\. Word: unexplained|Adjective|ok|
|If the word provided in the input cannot be assigned any of the listed part of speech tags, the output should not contain the word "Unknown"\.|gpt\-4o\-2024\-08\-06|Sentence: Uncharted discoveries multiplied\. Word: uncharted|Adjective|ok|
|If the word provided in the input cannot be assigned any of the listed part of speech tags, the output should not contain the word "Unknown"\.|gpt\-4o\-2024\-08\-06|Sentence: Freshly baked cookies\. Word: baked|Adjective|ok|
|If it is not possible to determine the part of speech from the input, the output should not contain the word "CantAnswer"\.|gpt\-4o\-2024\-08\-06|Sentence: My non\-conclusive sentence\. Word: non\-conclusive|Adjective|err|
|If it is not possible to determine the part of speech from the input, the output should not contain the word "CantAnswer"\.|gpt\-4o\-2024\-08\-06|Sentence: My entirely customized interface\.W ord: entirely|Adverb|ok|
|If it is not possible to determine the part of speech from the input, the output should not contain the word "CantAnswer"\.|gpt\-4o\-2024\-08\-06|Sentence: Envisioned unravels tomorrow\. Word: unravels|Verb|err|
|The output must contain additional information besides any specific part of speech tag or words such as "Unknown" and "CantAnswer"\.|gpt\-4o\-2024\-08\-06|Sentence: Buzzwords characterize strategy sadly\. Word: strategy|Noun|ok|
|The output must contain additional information besides any specific part of speech tag or words such as "Unknown" and "CantAnswer"\.|gpt\-4o\-2024\-08\-06|Sentence: Conundrum solved strategically\. Word: Conundrum|Noun|ok|
|The output must contain additional information besides any specific part of speech tag or words such as "Unknown" and "CantAnswer"\.|gpt\-4o\-2024\-08\-06|Sentence: Proficiently relinquished duties\. Word: Proficiently|Adverb|ok|
|At least one word in the provided input must be omitted from tagging according to the conditions defined, and the output must ignore some of the listed scenarios appropriately\.|gpt\-4o\-2024\-08\-06|Sentence: Varied marbles on the floor\. Word: floor|Noun|ok|
|At least one word in the provided input must be omitted from tagging according to the conditions defined, and the output must ignore some of the listed scenarios appropriately\.|gpt\-4o\-2024\-08\-06|Sentence: Clustered rings surround frequently\. Word: frequently|Adverb|err|
|At least one word in the provided input must be omitted from tagging according to the conditions defined, and the output must ignore some of the listed scenarios appropriately\.|gpt\-4o\-2024\-08\-06|Sentence: Astronomically relevant grids captivate\. Word: Astronomically|Adverb|ok|

### [baseline_tests.txt](./baseline_tests.txt)

`````txt
sentence: The quick brown fox jumps over the lazy dog. word: jumps
===
sentence: She has taken the book from the shelf. word: taken
===
sentence: John loves Mary. word: Mary
===
sentence: There is a cat under the table. word: There
===
sentence: The recipe calls for two eggs and a cup of sugar. word: two
===
sentence: We will win that match. word: win
===
sentence: Paris is a beautiful city. word: Paris
===
sentence: They quickly ran towards the finish line. word: quickly
===
sentence: These are the best cookies I have ever tasted. word: best
===
sentence: Can you find the hidden treasure? word: hidden
===
sentence: The children play happily in the park. word: happily
===
sentence: He went to the store yesterday. word: yesterday
===
sentence: Will you be coming with us? word: Will
===
sentence: Please hand me the blue folder. word: blue
===
sentence: The test was incredibly difficult. word: was
===
sentence: She doesn't know what to do. word: what
===
sentence: A flock of birds flew overhead. word: flock
===
sentence: Sam and Pete are going to the conference. word: and
===
sentence: I need a pen and paper. word: pen
===
sentence: Which route should we take? word: Which
===
sentence: The process is extremely complicated. word: extremely
===
sentence: We have been friends for many years. word: been
===
sentence: This is my car. word: my
===
sentence: Have you seen their new house yet? word: their
===
sentence: Oh no, I forgot my homework at home. word: Oh
===
sentence: Each student should bring a notebook. word: Each
===
sentence: The sun rises in the east. word: rises
===
sentence: Can someone explain this to me? word: explain
===
sentence: Despite the warnings, they proceeded with the plan. word: Despite
===
sentence: We have been waiting for hours. word: hours
===
sentence: The delicious aroma filled the kitchen. word: aroma
===
sentence: The committee dissolved the party. word: dissolved
===
sentence: You should definitely try this dish. word: definitely
===
sentence: An apple a day keeps the doctor away. word: An
===
sentence: Let me rest for a while. word: rest
===
sentence: The quick brown fox jumps over the lazy dog. word: fox
===
sentence: She has a unique perspective on life. word: unique
===
sentence: It suddenly started raining. word: suddenly
===
sentence: How often do you visit your hometown? word: often
===
sentence: Alas, we have no choice. word: Alas
===
sentence: If you believe, you can achieve. word: If
===
sentence: The vase broke into pieces. word: pieces
`````
