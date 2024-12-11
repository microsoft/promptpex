## elements ([json](./evals\o1mini\elements/report.json))

- 5 rules
- 5 inverse rules
- 65 tests, 33 baseline tests

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



### [elements.prompty](./elements.prompty)

`````md

---
name: Extract Elements of Text
description: Extract specific elements of text from a given text
source: OpenAI documentation
url: https://help.openai.com/en/articles/6654000-best-practices-for-prompt-engineering-with-the-openai-api
inputs: 
   text:
      type: string
---
system:
Extract the important entities mentioned in the text below. First extract all company names, then extract all people names, then extract specific topics which fit the content and finally extract general overarching themes

Desired format:
Company names: <comma_separated_list_of_company_names>
People names: -||-
Specific topics: -||-
General themes: -||-
user:
Text: {{ text }}

`````


### [intent.txt](./intent.txt)

`````txt
Extract important company names, people names, specific topics, and general themes from a given text.
`````


### [input_spec.txt](./input_spec.txt)

`````txt
The input must be a non-empty string containing the text to be analyzed.
The input string should not exceed 10,000 characters.
`````


### [rules.txt](./rules.txt)

`````txt
1: The output must consist of four distinct lines, each corresponding to a specific category of extracted elements.  
2: The first line must begin with "Company names:" followed by a space and a comma-separated list of company names extracted from the input text. A company name is defined as the official name of a business entity or organization mentioned in the input text.  
3: The second line must begin with "People names:" followed by a space and a comma-separated list of full names of individuals extracted from the input text. A people name is defined as the full name of a person, including both first and last names, mentioned in the input text.  
4: The third line must begin with "Specific topics:" followed by a space and a comma-separated list of specific topics relevant to the content of the input text. A specific topic is defined as a particular subject matter that closely relates to the content and context of the input text.  
5: The fourth line must begin with "General themes:" followed by a space and a comma-separated list of general themes that broadly encapsulate the main ideas of the input text. A general theme is defined as a wide-ranging topic or overarching subject that represents the fundamental concepts presented in the input text.
`````


### [inverse_rules.txt](./inverse_rules.txt)

`````txt
6: The output must consist of a variable number of lines not limited to four, with overlapping or unrelated categories.
7: The first line must not begin with "Company names:" and should exclude any business entity or organization names extracted from the input text.
8: The second line must not begin with "People names:" and should exclude any full names of individuals extracted from the input text.
9: The third line must not begin with "Specific topics:" and should exclude any particular subject matters related to the content of the input text.
10: The fourth line must not begin with "General themes:" and should exclude any wide-ranging topics or overarching subjects from the main ideas of the input text.
`````


### [tests.csv](./tests.csv)

|testinput|expectedoutput|reasoning|
|-|-|-|
||||
||||
||||
||||
||||
||||
||||
||||
||||
||||
||||
||||
||||
||||
||||
||||
||||
||||
||||
||||
||||
||||
||||
||||
||||
||||
||||
||||
||||
||||
||||
||||

### [baseline_tests.txt](./baseline_tests.txt)

`````txt
text: Apple Inc. announced a new product at their annual conference. Tim Cook highlighted the features of the latest iPhone, emphasizing sustainability.
===
text: In a recent interview, Elon Musk discussed the future of SpaceX and Tesla. He also mentioned collaborations with NASA on upcoming missions.
===
text: The United Nations held a summit on climate change, focusing on reducing carbon emissions and promoting renewable energy sources.
===
text: Microsoft released an update for Windows 11, introducing several new features and security enhancements. Satya Nadella spoke about the company's commitment to innovation.
===
text: During the conference, Dr. Jane Smith presented her research on artificial intelligence and machine learning applications in healthcare.
===
text: Google partnered with various startups to accelerate advancements in quantum computing technology. Sundar Pichai emphasized the importance of collaboration.
===
text: The annual report from Amazon detailed a 10% increase in revenue and expansion into new international markets. Jeff Bezos outlined future growth strategies.
===
text: At the technology expo, Samsung unveiled its latest line of smart appliances, aiming to integrate Internet of Things (IoT) capabilities into everyday household items.
===
text: The CEO of Facebook, Mark Zuckerberg, addressed concerns regarding data privacy and announced new initiatives to safeguard user information.
===
text: A panel of experts from Harvard University discussed the impacts of globalization on emerging economies, highlighting both opportunities and challenges.
===
text: Toyota is investing heavily in electric vehicle technology, aiming to release 20 new models by 2025. Akio Toyoda stated the company's vision for a sustainable future.
===
text: The New York Times published an in-depth analysis of the stock market trends over the past decade, featuring insights from financial analysts and economists.
===
text: Amazon Web Services (AWS) introduced a new cloud-based solution designed to enhance data security for businesses of all sizes.
===
text: During the press release, NVIDIA showcased its latest advancements in graphics processing units (GPUs), targeting the gaming and professional visualization markets.
===
text: The World Health Organization (WHO) released guidelines on mental health support, emphasizing the need for accessible resources and community programs.
===
text: In her keynote speech, Oprah Winfrey shared her experiences in media and philanthropic efforts aimed at empowering underprivileged communities.
===
text: IBM announced a breakthrough in quantum computing, collaborating with research institutions to push the boundaries of computational capabilities.
===
text: The European Union passed new regulations on digital privacy, impacting major tech companies like Apple and Google in how they handle user data.
===
text: A study conducted by MIT revealed significant advancements in renewable energy storage, potentially revolutionizing the power industry.
===
text: During the summit, Angela Merkel discussed the importance of international cooperation in addressing global economic challenges and fostering sustainable development.
===
text: Tesla's Gigafactory in Shanghai has reached full production capacity, contributing to the global supply chain of electric vehicles and batteries.
===
text: The software development team at Adobe launched a beta version of their new creative suite, offering enhanced features for graphic designers and video editors.
===
text: In collaboration with NASA, Boeing is developing next-generation spacecraft aimed at deep space exploration missions scheduled for the next decade.
===
text: The Financial Times reported on the merger between two leading banks, highlighting the potential impacts on the global financial landscape.
===
text: During the webinar, Professor Alan Turing from Stanford University presented his latest research on cryptography and its applications in cybersecurity.
===
text: Spotify introduced a new algorithm designed to personalize music recommendations, leveraging machine learning to enhance user experience.
===
text: The National Basketball Association (NBA) partnered with Nike to release a limited edition line of athletic wear, celebrating the league's 75th anniversary.
===
text: Intel showcased its new line of processors at CES, promising faster performance and improved energy efficiency for both consumers and enterprise clients.
===
text: The United States Department of Energy announced funding for several projects focused on advancing solar and wind energy technologies.
===
text: During the panel discussion, Dr. Susan Calvin from Robotics Institute discussed the ethical considerations of developing autonomous artificial intelligence systems.
===
text: BMW unveiled its latest electric vehicle model, featuring cutting-edge technology and sustainable manufacturing practices aimed at reducing carbon footprint.
===
text: The World Economic Forum in Davos brought together global leaders to discuss strategies for economic recovery and addressing income inequality post-pandemic.
===
text: Salesforce released a new customer relationship management (CRM) tool designed to integrate seamlessly with existing business applications, enhancing sales and marketing efforts.
`````
