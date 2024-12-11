## classify-input-text ([json](./evals\o1preview-gpt4\classify-input-text/report.json))

- 10 rules
- 10 inverse rules
- 124 tests, 64 baseline tests

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



### [classify-input-text.prompty](./classify-input-text.prompty)

`````md

---
name: Classify input text
description: Given an input text, classify it into a specific category.
source: How to use Llama2 tutorial for text classification
url: https://pupuweb.com/how-use-llama-2-text-classification-tasks/
inputs:
    text:
        type: "string"
sample:
    text: "UN chief urges action on climate change as report warns of 'catastrophe'"
---
system:
A news article can be classified as one of the following categories: World, Sports, Business, Sci/Tech.
Examples:
- World: "UN chief urges action on climate change as report warns of 'catastrophe'"
- Sports: "Ronaldo scores twice in Manchester United return"
- Business: "Apple delays plan to scan iPhones for child abuse images"
- Sci/Tech: "SpaceX launches first all-civilian crew into orbit"'

Based on these categories, classify this news article: 
user:
{{text}}
    
`````


### [intent.txt](./intent.txt)

`````txt
Classify an input news article into one of the categories: World, Sports, Business, or Sci/Tech.
`````


### [input_spec.txt](./input_spec.txt)

`````txt
The input is a string containing text to be classified.
The input text can be any piece of text, such as a news article or headline.
The input should be in English language.
The input can be of any length, from short phrases to longer articles.
The input should be in plain text format.
`````


### [rules.txt](./rules.txt)

`````txt
1: The output must be exactly one of the following categories: "World", "Sports", "Business", or "Sci/Tech".
2: The output should match the category name precisely as specified, including capitalization and punctuation.
3: The output should consist solely of the category name without any additional text.
4: The output should not include the input text or any excerpts or paraphrases of it.
5: The "World" category refers to news articles about international events, global politics, or worldwide issues.
6: The "Sports" category refers to news articles about athletic events, sports teams, athletes, or sports-related activities.
7: The "Business" category refers to news articles about corporations, market trends, economic policies, or financial news.
8: The "Sci/Tech" category refers to news articles about science, technology, innovations, scientific discoveries, or technological advancements.
9: The output should be in plain text format without any special formatting, markup, or additional characters.
10: The output should appear on a single line containing only the category name.
`````


### [inverse_rules.txt](./inverse_rules.txt)

`````txt
11: The output must not be any of the following categories: "World", "Sports", "Business", or "Sci/Tech".  
12: The output should intentionally differ from the category name in spelling, capitalization, or punctuation.  
13: The output should include additional text besides the category name.  
14: The output should incorporate the input text or its excerpts or paraphrases.  
15: The "World" category excludes news articles about international events, global politics, or worldwide issues.  
16: The "Sports" category excludes news articles about athletic events, sports teams, athletes, or sports-related activities.  
17: The "Business" category excludes news articles about corporations, market trends, economic policies, or financial news.  
18: The "Sci/Tech" category excludes news articles about science, technology, innovations, scientific discoveries, or technological advancements.  
19: The output should include special formatting, markup, or additional characters beyond plain text.  
20: The output should span multiple lines and may contain content other than the category name.
`````


### [tests.csv](./tests.csv)

|testinput|expectedoutput|reasoning|
|-|-|-|
|Global markets rally as US\-China trade tensions ease|Business|This test case provides an input expected to be classified as "Business", ensuring that the software outputs exactly one of the allowed categories, adhering to Rule 1\.|
|Breakthrough in renewable energy could revolutionize solar power|Sci/Tech|Checks if the software correctly classifies the input as "Sci/Tech", one of the specified categories, demonstrating adherence to Rule 1\.|
|Olympics postponed due to pandemic concerns|Sports|Verifies that the software outputs "Sports" for an input about athletic events, complying with Rule 1\.|
|New discoveries in Mars rover mission lead to excitement in astronomy community|Sci/Tech|Tests whether the software outputs the category name "Sci/Tech" with exact spelling and capitalization, following Rule 2\.|
|Economic reforms boost small businesses across the country|Business|Checks if the software outputs "Business" with precise spelling and capitalization as specified, adhering to Rule 2\.|
|Global summit addresses climate change initiatives|World|Ensures the output matches the category name "World" precisely, including capitalization, complying with Rule 2\.|
|Innovations in AI technology raise ethical considerations|Sci/Tech|Verifies that the output consists solely of "Sci/Tech" without additional text, adhering to Rule 3\.|
|Championship game ends in a surprising upset|Sports|Ensures the software outputs only "Sports" with no extra words or characters, following Rule 3\.|
|International sanctions impact global trade heavily|World|Checks that the output is solely "World" without any additional content, complying with Rule 3\.|
|Tech giants collaborate on new cybersecurity standards|Sci/Tech|Tests that the output does not include any part of the input text, only the category name, ensuring adherence to Rule 4\.|
|Local athlete breaks world record in 100m sprint|Sports|Verifies the output is only "Sports" without incorporating the input text, complying with Rule 4\.|
|Stock markets fluctuate amid economic uncertainty|Business|Checks that the output does not include excerpts or paraphrases of the input, adhering to Rule 4\.|
|Diplomatic talks resume to resolve border disputes between nations|World|Tests if the software correctly classifies international events as "World", following Rule 5\.|
|Global pandemic causes widespread changes in travel policies|World|Checks that worldwide issues are classified under "World", complying with Rule 5\.|
|International leaders meet at summit to discuss climate action|World|Verifies that global political events are classified as "World", adhering to Rule 5\.|
|Top seed player wins the Grand Slam tournament|Sports|Ensures that athletic events are classified as "Sports", following Rule 6\.|
|Local football team announces new coach for upcoming season|Sports|Tests if news about sports teams is classified as "Sports", complying with Rule 6\.|
|Olympic committee adds new sports to the next games|Sports|Verifies that sports\-related activities are classified under "Sports", adhering to Rule 6\.|
|Central bank announces changes to interest rates|Business|Checks that economic policies are classified as "Business", following Rule 7\.|
|Tech company's stock soars after successful product launch|Business|Ensures that news about corporations and market trends is classified as "Business", complying with Rule 7\.|
|Unemployment rates drop as new jobs are created|Business|Verifies that financial news is classified under "Business", adhering to Rule 7\.|
|Researchers develop new vaccine technology|Sci/Tech|Tests if scientific discoveries are classified as "Sci/Tech", following Rule 8\.|
|Breakthrough in quantum computing achieved by scientists|Sci/Tech|Checks that technological advancements are classified as "Sci/Tech", complying with Rule 8\.|
|New study reveals insights into climate change patterns|Sci/Tech|Ensures that science news is classified under "Sci/Tech", adhering to Rule 8\.|
|Advancements in battery technology may extend electric vehicle range|Sci/Tech|Verifies that the output is in plain text without special characters, complying with Rule 9\.|
|Economic forum discusses global market trends|Business|Ensures that the output has no special formatting, adhering to Rule 9\.|
|World leaders agree on new environmental treaty|World|Checks that the output is plain text without additional characters, following Rule 9\.|
|Basketball legend announces retirement after 20 seasons|Sports|Verifies that the output appears on a single line containing only the category name, complying with Rule 10\.|
|Scientists detect signals from distant galaxy|Sci/Tech|Ensures that the output is a single line with only "Sci/Tech", adhering to Rule 10\.|
|International trade agreements boost economic growth|Business|Checks that the output is on a single line containing only "Business", following Rule 10\.|
|Delicious homemade pasta recipes to try this weekend|Other|Tests whether the software avoids outputting any of the specified categories for content outside those categories, adhering to Rule 11\.|
|A review of the latest romantic comedy movie|Other|Verifies that the software does not output "World", "Sports", "Business", or "Sci/Tech" for unrelated content, complying with Rule 11\.|
|Exploring the history of classical music composers|Other|Checks that the software outputs a category other than the specified ones for this input, following Rule 11\.|
|Tech conference unveils latest gadgets and innovations|sci/tech|Tests if the software outputs the category name with incorrect capitalization, adhering to Rule 12\.|
|International summit on global warming ends with agreement|World\.|Checks whether the software outputs "World\." with additional punctuation, complying with Rule 12\.|
|National league final ends in dramatic penalty shootout|Sport|Verifies that the software outputs a misspelled category name, following Rule 12\.|
|Major breakthrough achieved in cancer research|Sci/Tech News|Tests if the software includes additional text with the category name, adhering to Rule 13\.|
|Local team wins the championship after intense match|Sports: Local team wins\!|Checks whether the output contains additional text besides the category name, complying with Rule 13\.|
|Economy shows signs of recovery in the last quarter|Business \(Growth\)|Verifies that the software outputs the category name with extra content, following Rule 13\.|
|New policy reforms expected to improve the education system|World: New policy reforms expected to improve the education system|Tests if the software incorporates the input text into the output, adhering to Rule 14\.|
|Star player scores winning goal in final seconds|Sports: Star player scores winning goal in final seconds|Checks whether the output includes the input text, complying with Rule 14\.|
|Advancements in renewable energy technology|Sci/Tech \- Advancements in renewable energy technology|Verifies that the software outputs the category name along with the input text, following Rule 14\.|
|Global leaders meet to discuss climate crisis|Sci/Tech|Tests whether the software avoids classifying international events as "World", adhering to Rule 15\.|
|International trade agreements affect local businesses|Business|Checks if the software classifies international events under a category other than "World", complying with Rule 15\.|
|Global peace talks yield promising results|Sports|Verifies that the software does not classify the input as "World", following Rule 15\.|
|Football championship ends in dramatic victory|Business|Tests if the software avoids classifying sports events as "Sports", adhering to Rule 16\.|
|Olympic records shattered in track events|Sci/Tech|Checks whether the software classifies athletic events under a different category, complying with Rule 16\.|
|Star athlete signs contract with new team|World|Verifies that the software does not classify the input as "Sports", following Rule 16\.|
|Stock market hits all\-time high amid investor optimism|World|Tests whether the software avoids classifying financial news as "Business", adhering to Rule 17\.|
|Tech company announces merger with competitor|Sci/Tech|Checks if the software classifies corporate news under a different category, complying with Rule 17\.|
|New economic policies expected to boost GDP|Sports|Verifies that the software does not classify economic policies as "Business", following Rule 17\.|
|Researchers discover potential cure for disease|World|Tests if the software avoids classifying scientific discoveries as "Sci/Tech", adhering to Rule 18\.|
|Breakthrough in AI technology challenges tech industry|Business|Checks whether the software classifies technological advancements under a different category, complying with Rule 18\.|
|Innovations in renewable energy promise cleaner future|Sports|Verifies that the software does not classify the input as "Sci/Tech", following Rule 18\.|
|New species discovered in the Amazon rainforest|\*\*Sci/Tech\*\*|Tests whether the software outputs the category name with special formatting, adhering to Rule 19\.|
|Economists forecast recession in the next quarter|lt;Businessgt;|Checks if the software includes markup in the output, complying with Rule 19\.|
|National team wins gold in Olympics|\[Sports\]|Verifies that the software outputs the category name with additional characters, following Rule 19\.|
|Global summit on climate change ends with new agreement|World\\nThis article discusses global efforts on climate change\.|Tests if the software outputs multiple lines and adds content beyond the category name, adhering to Rule 20\.|
|Breakthrough in nanotechnology leads to medical advances|Sci/Tech\\nLatest developments in nanotechnology\.|Checks whether the output spans multiple lines with extra content, complying with Rule 20\.|
|Local baseball team wins championship after decades|Sports\\nAn exciting win for the hometown heroes\!|Verifies that the software outputs additional content across multiple lines, following Rule 20\.|

### [test_evals.csv](./test_evals.csv)

|rule|model|input|coverage|validity|
|-|-|-|-|-|
|The output must be exactly one of the following categories: "World", "Sports", "Business", or "Sci/Tech"\.|gpt\-4o\-2024\-08\-06|Global markets rally as US\-China trade tensions ease|Business|ok|
|The output must be exactly one of the following categories: "World", "Sports", "Business", or "Sci/Tech"\.|gpt\-4o\-2024\-08\-06|Breakthrough in renewable energy could revolutionize solar power|Sci/Tech|ok|
|The output must be exactly one of the following categories: "World", "Sports", "Business", or "Sci/Tech"\.|gpt\-4o\-2024\-08\-06|Olympics postponed due to pandemic concerns|Sports|ok|
|The output should match the category name precisely as specified, including capitalization and punctuation\.|gpt\-4o\-2024\-08\-06|New discoveries in Mars rover mission lead to excitement in astronomy community|Sci/Tech|ok|
|The output should match the category name precisely as specified, including capitalization and punctuation\.|gpt\-4o\-2024\-08\-06|Economic reforms boost small businesses across the country|Business|ok|
|The output should match the category name precisely as specified, including capitalization and punctuation\.|gpt\-4o\-2024\-08\-06|Global summit addresses climate change initiatives|World|ok|
|The output should consist solely of the category name without any additional text\.|gpt\-4o\-2024\-08\-06|Innovations in AI technology raise ethical considerations|Sci/Tech|ok|
|The output should consist solely of the category name without any additional text\.|gpt\-4o\-2024\-08\-06|Championship game ends in a surprising upset|Sports|ok|
|The output should consist solely of the category name without any additional text\.|gpt\-4o\-2024\-08\-06|International sanctions impact global trade heavily|World|ok|
|The output should not include the input text or any excerpts or paraphrases of it\.|gpt\-4o\-2024\-08\-06|Tech giants collaborate on new cybersecurity standards|Sci/Tech|ok|
|The output should not include the input text or any excerpts or paraphrases of it\.|gpt\-4o\-2024\-08\-06|Local athlete breaks world record in 100m sprint|Sports|ok|
|The output should not include the input text or any excerpts or paraphrases of it\.|gpt\-4o\-2024\-08\-06|Stock markets fluctuate amid economic uncertainty|Business|ok|
|The "World" category refers to news articles about international events, global politics, or worldwide issues\.|gpt\-4o\-2024\-08\-06|Diplomatic talks resume to resolve border disputes between nations|World|ok|
|The "World" category refers to news articles about international events, global politics, or worldwide issues\.|gpt\-4o\-2024\-08\-06|Global pandemic causes widespread changes in travel policies|World|ok|
|The "World" category refers to news articles about international events, global politics, or worldwide issues\.|gpt\-4o\-2024\-08\-06|International leaders meet at summit to discuss climate action|World|ok|
|The "Sports" category refers to news articles about athletic events, sports teams, athletes, or sports\-related activities\.|gpt\-4o\-2024\-08\-06|Top seed player wins the Grand Slam tournament|Sports|ok|
|The "Sports" category refers to news articles about athletic events, sports teams, athletes, or sports\-related activities\.|gpt\-4o\-2024\-08\-06|Local football team announces new coach for upcoming season|Sports|ok|
|The "Sports" category refers to news articles about athletic events, sports teams, athletes, or sports\-related activities\.|gpt\-4o\-2024\-08\-06|Olympic committee adds new sports to the next games|Sports|ok|
|The "Business" category refers to news articles about corporations, market trends, economic policies, or financial news\.|gpt\-4o\-2024\-08\-06|Central bank announces changes to interest rates|Business|ok|
|The "Business" category refers to news articles about corporations, market trends, economic policies, or financial news\.|gpt\-4o\-2024\-08\-06|Tech company's stock soars after successful product launch|Business|ok|
|The "Business" category refers to news articles about corporations, market trends, economic policies, or financial news\.|gpt\-4o\-2024\-08\-06|Unemployment rates drop as new jobs are created|Business|ok|
|The "Sci/Tech" category refers to news articles about science, technology, innovations, scientific discoveries, or technological advancements\.|gpt\-4o\-2024\-08\-06|Researchers develop new vaccine technology|Sci/Tech|ok|
|The "Sci/Tech" category refers to news articles about science, technology, innovations, scientific discoveries, or technological advancements\.|gpt\-4o\-2024\-08\-06|Breakthrough in quantum computing achieved by scientists|Sci/Tech|ok|
|The "Sci/Tech" category refers to news articles about science, technology, innovations, scientific discoveries, or technological advancements\.|gpt\-4o\-2024\-08\-06|New study reveals insights into climate change patterns|Sci/Tech|ok|
|The output should be in plain text format without any special formatting, markup, or additional characters\.|gpt\-4o\-2024\-08\-06|Advancements in battery technology may extend electric vehicle range|Sci/Tech|ok|
|The output should be in plain text format without any special formatting, markup, or additional characters\.|gpt\-4o\-2024\-08\-06|Economic forum discusses global market trends|Business|ok|
|The output should be in plain text format without any special formatting, markup, or additional characters\.|gpt\-4o\-2024\-08\-06|World leaders agree on new environmental treaty|World|ok|
|The output should appear on a single line containing only the category name\.|gpt\-4o\-2024\-08\-06|Basketball legend announces retirement after 20 seasons|Sports|ok|
|The output should appear on a single line containing only the category name\.|gpt\-4o\-2024\-08\-06|Scientists detect signals from distant galaxy|Sci/Tech|ok|
|The output should appear on a single line containing only the category name\.|gpt\-4o\-2024\-08\-06|International trade agreements boost economic growth|Business|ok|
|The output must not be any of the following categories: "World", "Sports", "Business", or "Sci/Tech"\.|gpt\-4o\-2024\-08\-06|Delicious homemade pasta recipes to try this weekend|Sci/Tech|ok|
|The output must not be any of the following categories: "World", "Sports", "Business", or "Sci/Tech"\.|gpt\-4o\-2024\-08\-06|A review of the latest romantic comedy movie|Sci/Tech|ok|
|The output must not be any of the following categories: "World", "Sports", "Business", or "Sci/Tech"\.|gpt\-4o\-2024\-08\-06|Exploring the history of classical music composers|Sci/Tech|ok|
|The output should intentionally differ from the category name in spelling, capitalization, or punctuation\.|gpt\-4o\-2024\-08\-06|Tech conference unveils latest gadgets and innovations|Sci/Tech|ok|
|The output should intentionally differ from the category name in spelling, capitalization, or punctuation\.|gpt\-4o\-2024\-08\-06|International summit on global warming ends with agreement|World|ok|
|The output should intentionally differ from the category name in spelling, capitalization, or punctuation\.|gpt\-4o\-2024\-08\-06|National league final ends in dramatic penalty shootout|Sports|ok|
|The output should include additional text besides the category name\.|gpt\-4o\-2024\-08\-06|Major breakthrough achieved in cancer research|Sci/Tech|ok|
|The output should include additional text besides the category name\.|gpt\-4o\-2024\-08\-06|Local team wins the championship after intense match|Sports|ok|
|The output should include additional text besides the category name\.|gpt\-4o\-2024\-08\-06|Economy shows signs of recovery in the last quarter|Business|ok|
|The output should incorporate the input text or its excerpts or paraphrases\.|gpt\-4o\-2024\-08\-06|New policy reforms expected to improve the education system|Sci/Tech|ok|
|The output should incorporate the input text or its excerpts or paraphrases\.|gpt\-4o\-2024\-08\-06|Star player scores winning goal in final seconds|Sports|ok|
|The output should incorporate the input text or its excerpts or paraphrases\.|gpt\-4o\-2024\-08\-06|Advancements in renewable energy technology|Sci/Tech|ok|
|The "World" category excludes news articles about international events, global politics, or worldwide issues\.|gpt\-4o\-2024\-08\-06|Global leaders meet to discuss climate crisis|World|ok|
|The "World" category excludes news articles about international events, global politics, or worldwide issues\.|gpt\-4o\-2024\-08\-06|International trade agreements affect local businesses|Business|ok|
|The "World" category excludes news articles about international events, global politics, or worldwide issues\.|gpt\-4o\-2024\-08\-06|Global peace talks yield promising results|World|ok|
|The "Sports" category excludes news articles about athletic events, sports teams, athletes, or sports\-related activities\.|gpt\-4o\-2024\-08\-06|Football championship ends in dramatic victory|Sports|ok|
|The "Sports" category excludes news articles about athletic events, sports teams, athletes, or sports\-related activities\.|gpt\-4o\-2024\-08\-06|Olympic records shattered in track events|Sports|ok|
|The "Sports" category excludes news articles about athletic events, sports teams, athletes, or sports\-related activities\.|gpt\-4o\-2024\-08\-06|Star athlete signs contract with new team|Sports|ok|
|The "Business" category excludes news articles about corporations, market trends, economic policies, or financial news\.|gpt\-4o\-2024\-08\-06|Stock market hits all\-time high amid investor optimism|Business|ok|
|The "Business" category excludes news articles about corporations, market trends, economic policies, or financial news\.|gpt\-4o\-2024\-08\-06|Tech company announces merger with competitor|Business|ok|
|The "Business" category excludes news articles about corporations, market trends, economic policies, or financial news\.|gpt\-4o\-2024\-08\-06|New economic policies expected to boost GDP|Business|ok|
|The "Sci/Tech" category excludes news articles about science, technology, innovations, scientific discoveries, or technological advancements\.|gpt\-4o\-2024\-08\-06|Researchers discover potential cure for disease|Sci/Tech|ok|
|The "Sci/Tech" category excludes news articles about science, technology, innovations, scientific discoveries, or technological advancements\.|gpt\-4o\-2024\-08\-06|Breakthrough in AI technology challenges tech industry|Sci/Tech|ok|
|The "Sci/Tech" category excludes news articles about science, technology, innovations, scientific discoveries, or technological advancements\.|gpt\-4o\-2024\-08\-06|Innovations in renewable energy promise cleaner future|Sci/Tech|ok|
|The output should include special formatting, markup, or additional characters beyond plain text\.|gpt\-4o\-2024\-08\-06|New species discovered in the Amazon rainforest|Sci/Tech|ok|
|The output should include special formatting, markup, or additional characters beyond plain text\.|gpt\-4o\-2024\-08\-06|Economists forecast recession in the next quarter|Business|ok|
|The output should include special formatting, markup, or additional characters beyond plain text\.|gpt\-4o\-2024\-08\-06|National team wins gold in Olympics|Sports|ok|
|The output should span multiple lines and may contain content other than the category name\.|gpt\-4o\-2024\-08\-06|Global summit on climate change ends with new agreement|World|ok|
|The output should span multiple lines and may contain content other than the category name\.|gpt\-4o\-2024\-08\-06|Breakthrough in nanotechnology leads to medical advances|Sci/Tech|ok|
|The output should span multiple lines and may contain content other than the category name\.|gpt\-4o\-2024\-08\-06|Local baseball team wins championship after decades|Sports|ok|

### [baseline_tests.txt](./baseline_tests.txt)

`````txt
text: "Peace talks resume between rival factions in Middle East"
===
text: "Earthquake in Indonesia leaves thousands homeless"
===
text: "Elections in Germany see a shift towards green policies"
===
text: "Global leaders gather for UN summit on sustainable development"
===
text: "Brexit negotiations reach critical phase"
===
text: "Serena Williams announces retirement from tennis"
===
text: "Olympic committee unveils new sports for 2024 Games"
===
text: "Underdog team wins national basketball championship"
===
text: "FIFA introduces new technology for World Cup matches"
===
text: "Record-breaking marathon run in New York City"
===
text: "Tesla reports record profits amid surge in electric car demand"
===
text: "Stock markets fall as inflation fears grow"
===
text: "Amazon acquires autonomous driving startup"
===
text: "Global trade tensions impact manufacturing sector"
===
text: "Cryptocurrency hits all-time high after regulatory approval"
===
text: "Breakthrough in Alzheimer's research offers new hope"
===
text: "Scientists discover new exoplanet that could support life"
===
text: "Artificial intelligence beats human champions in chess tournament"
===
text: "NASA plans mission to explore Jupiter's moons"
===
text: "Quantum computing makes strides with new algorithm"
===
text: "Tech giants invest in sports streaming rights"
===
text: "Climate change impacts global agricultural markets"
===
text: "New wearable device tracks fitness and monitors health"
===
text: "Economic crisis leads to government upheaval"
===
text: "Robotics company sponsors national soccer team"
===
text: "War breaks out in Eastern Europe"
===
text: "Market crashes after unexpected announcement"
===
text: "Advances in gene editing technology raise ethical questions"
===
text: "Hurricane approaches Florida coast prompting evacuations"
===
text: "Legendary coach retires after 30 years in the league"
===
text: "Oil prices soar due to conflicts in the Middle East"
===
text: "Major cybersecurity breach affects millions of users"
===
text: "Innovative app aims to revolutionize education"
===
text: "Local team secures spot in international tournament"
===
text: "New policy changes announced by central bank"
===
text: "Experimental vaccine shows promise in early trials"
===
text: "Government passes bill to boost renewable energy production"
===
text: "Electric vehicle sales surpass traditional cars for first time"
===
text: "Controversial call in playoff game sparks debate"
===
text: "Researchers develop method to recycle plastic waste"
===
text: "Nationwide protests erupt over new legislation"
===
text: "Company stocks rise after successful product launch"
===
text: "Space tourism takes leap with successful passenger flight"
===
text: "Chess grandmaster wins championship at age 16"
===
text: "Climate summit ends with new international agreement"
===
text: "Breakthrough in battery technology extends smartphone life"
===
text: "Athlete sets new world record in high jump"
===
text: "Trade agreement signed between neighboring countries"
===
text: "Artificial intelligence used to predict natural disasters"
===
text: "Corporate merger creates world's largest tech company"
===
text: "Volcano eruption forces thousands to evacuate"
===
text: "Drone delivery service begins in urban areas"
===
text: "Football star transfers to rival club in record deal"
===
text: "Pharmaceutical company announces cure for rare disease"
===
text: "Economic sanctions lifted after peace treaty signed"
===
text: "Scientists simulate conditions of early Earth in lab"
===
text: "Basketball league introduces new rules to improve safety"
===
text: "Stock exchange launches digital currency trading platform"
===
text: "Astronomers capture first image of black hole"
===
text: "Government introduces tax incentives for startups"
===
text: "New study reveals benefits of Mediterranean diet"
===
text: "International art exhibit showcases emerging artists"
===
text: "Floods in South America displace thousands of residents"
===
text: "Education reform bill passes after heated debate"
`````
