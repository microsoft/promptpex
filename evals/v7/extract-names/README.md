## extract-names ([json](./evals\v7\extract-names/report.json))

- 6 rules
- 6 inverse rules
- 4 tests, 2 baseline tests
- 16 test results, 13/16 (81%) oks, 3/16 (18%) errs

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
|gpt\-4o\-mini|2|100%|100%|2|2|0|0|2|2|2|
|gemma2:9b|2|100%|100%|2|2|0|0|2|2|2|
|qwen2\.5:3b|2|100%|100%|2|2|0|0|2|2|2|
|llama3\.2:1b|2|0%|50%|2|0|0|0|2|2|0|

### [extract-names.prompty](./extract-names.prompty)

`````md
---
name: "Extract Names from Text"
description: "Extract names from an input text"
source: Prompt examples from the website (slightly modified)
url: https://www.promptingguide.ai/prompts/information-extraction/extract-models
sample:
    input: "The model uses a transformer architecture with a BERT base model."
inputs:
    input:
        type: "string"
---
system:
Your task is to extract model names from machine learning paper abstracts. Your response is an array of the model names in the format [\"model_name\"]. If you don't find model names in the abstract or you are not sure, return [\"NA\"]
user:
Abstract: {{input}}
`````


### [test_results.csv](./test_results.csv)

|model|rule|input|output|compliance|
|-|-|-|-|-|
|gpt\-4o\-mini|The output must be structured as an array with the specific format \["model\_name"\], where "model\_name" represents the name of a machine learning model extracted from the abstract\.|Abstract: We introduce NeuralMachineModel, a robust framework for image processing tasks\.|\["NeuralMachineModel"\]|ok|
|gemma2:9b|The output must be structured as an array with the specific format \["model\_name"\], where "model\_name" represents the name of a machine learning model extracted from the abstract\.|Abstract: We introduce NeuralMachineModel, a robust framework for image processing tasks\.|\["NeuralMachineModel", "NeuralMachineModel"\]|ok|
|qwen2\.5:3b|The output must be structured as an array with the specific format \["model\_name"\], where "model\_name" represents the name of a machine learning model extracted from the abstract\.|Abstract: We introduce NeuralMachineModel, a robust framework for image processing tasks\.|\[\["NeuralMachineModel"\]\]|ok|
|llama3\.2:1b|The output must be structured as an array with the specific format \["model\_name"\], where "model\_name" represents the name of a machine learning model extracted from the abstract\.|Abstract: We introduce NeuralMachineModel, a robust framework for image processing tasks\.|\[\]|err|
|gpt\-4o\-mini|The output must be structured as an array with the specific format \["model\_name"\], where "model\_name" represents the name of a machine learning model extracted from the abstract\.|Abstract: This paper proposes a novel architecture called QuantumNet for quantum computing applications\.|\["QuantumNet"\]|ok|
|gemma2:9b|The output must be structured as an array with the specific format \["model\_name"\], where "model\_name" represents the name of a machine learning model extracted from the abstract\.|Abstract: This paper proposes a novel architecture called QuantumNet for quantum computing applications\.|\["QuantumNet"\]|ok|
|qwen2\.5:3b|The output must be structured as an array with the specific format \["model\_name"\], where "model\_name" represents the name of a machine learning model extracted from the abstract\.|Abstract: This paper proposes a novel architecture called QuantumNet for quantum computing applications\.|\[\["QuantumNet"\]\]|ok|
|llama3\.2:1b|The output must be structured as an array with the specific format \["model\_name"\], where "model\_name" represents the name of a machine learning model extracted from the abstract\.|Abstract: This paper proposes a novel architecture called QuantumNet for quantum computing applications\.|\[\]|err|
|gpt\-4o\-mini||Abstract: In this paper, we introduce a novel architecture called "DeepVisionNet" that significantly improves image classification accuracy\. Unlike traditional convolutional neural networks, our model utilizes a fusion of transformer and residual networks, which we refer to as "FusionTransformerNet", to enhance feature extraction\. Comparative studies with models such as "ResNet50" and "EfficientNet" demonstrate the superiority of our proposed models\.|\["DeepVisionNet", "FusionTransformerNet", "ResNet50", "EfficientNet"\]|ok|
|gemma2:9b||Abstract: In this paper, we introduce a novel architecture called "DeepVisionNet" that significantly improves image classification accuracy\. Unlike traditional convolutional neural networks, our model utilizes a fusion of transformer and residual networks, which we refer to as "FusionTransformerNet", to enhance feature extraction\. Comparative studies with models such as "ResNet50" and "EfficientNet" demonstrate the superiority of our proposed models\.|\["DeepVisionNet", "FusionTransformerNet", "ResNet50", "EfficientNet"\]|ok|
|qwen2\.5:3b||Abstract: In this paper, we introduce a novel architecture called "DeepVisionNet" that significantly improves image classification accuracy\. Unlike traditional convolutional neural networks, our model utilizes a fusion of transformer and residual networks, which we refer to as "FusionTransformerNet", to enhance feature extraction\. Comparative studies with models such as "ResNet50" and "EfficientNet" demonstrate the superiority of our proposed models\.|\["DeepVisionNet", "FusionTransformerNet"\]|ok|
|llama3\.2:1b||Abstract: In this paper, we introduce a novel architecture called "DeepVisionNet" that significantly improves image classification accuracy\. Unlike traditional convolutional neural networks, our model utilizes a fusion of transformer and residual networks, which we refer to as "FusionTransformerNet", to enhance feature extraction\. Comparative studies with models such as "ResNet50" and "EfficientNet" demonstrate the superiority of our proposed models\.|Here are the model names extracted from the abstracts in the format \[\\"model\_name\\"\]:<br><br>\[\\"DeepVisionNet\\"\]<br>\[\\"FusionTransformerNet\\"\]<br>\[N/A\]|err|
|gpt\-4o\-mini||Abstract: The new "GeoBERT" model is presented, offering groundbreaking outcomes in geospatial data interpretation\. In contrast, existing solutions like "GeoSentimentNet" are limited in processing multilingual datasets\. We also benchmark against "SpatialTransformer" and "GeoMLP" to validate performance enhancements\. The experimental results depict GeoBERT’s exceptional ability over "GeoSentimentNet"\.|\["GeoBERT", "GeoSentimentNet", "SpatialTransformer", "GeoMLP"\]|ok|
|gemma2:9b||Abstract: The new "GeoBERT" model is presented, offering groundbreaking outcomes in geospatial data interpretation\. In contrast, existing solutions like "GeoSentimentNet" are limited in processing multilingual datasets\. We also benchmark against "SpatialTransformer" and "GeoMLP" to validate performance enhancements\. The experimental results depict GeoBERT’s exceptional ability over "GeoSentimentNet"\.|\["GeoBERT", "GeoSentimentNet", "SpatialTransformer", "GeoMLP"\]|ok|
|qwen2\.5:3b||Abstract: The new "GeoBERT" model is presented, offering groundbreaking outcomes in geospatial data interpretation\. In contrast, existing solutions like "GeoSentimentNet" are limited in processing multilingual datasets\. We also benchmark against "SpatialTransformer" and "GeoMLP" to validate performance enhancements\. The experimental results depict GeoBERT’s exceptional ability over "GeoSentimentNet"\.|\[\["GeoBERT", "GeoSentimentNet", "SpatialTransformer", "GeoMLP"\]\]|ok|
|llama3\.2:1b||Abstract: The new "GeoBERT" model is presented, offering groundbreaking outcomes in geospatial data interpretation\. In contrast, existing solutions like "GeoSentimentNet" are limited in processing multilingual datasets\. We also benchmark against "SpatialTransformer" and "GeoMLP" to validate performance enhancements\. The experimental results depict GeoBERT’s exceptional ability over "GeoSentimentNet"\.|Here is the extracted model names from the paper abstracts:<br><br>\["GeoBERT", "Geo SentimentNet"\]|ok|

### [intent.txt](./intent.txt)

`````txt
Extract model names from machine learning paper abstracts.
`````


### [input_spec.txt](./input_spec.txt)

`````txt
The input is a machine learning paper abstract.  
The input must be a textual string comprised of sentences and phrases from an academic paper abstract.  
The input can include technical terms, acronyms, and specific model names.
`````


### [rules.txt](./rules.txt)

`````txt
1: The output must be structured as an array with the specific format ["model_name"], where "model_name" represents the name of a machine learning model extracted from the abstract. 
2: Each element within the output array should be a distinct string representing an extracted model name. 
3: If no model names are found in the provided abstract or there is uncertainty regarding the identification of a model name, the output must be ["NA"], using exactly this format including the square brackets and quotation marks. 
4: The output must only contain model names extracted from the abstract or ["NA"] if no model names are identified, without any additional text, explanations, or context. 
5: The array must only contain correctly identified machine learning model names from the abstract as individual strings, ensuring precision in the identification process. 
6: The order of model names in the array should reflect their order of appearance in the abstract, but this does not affect the requirement that the structure and format of the array are correct.
`````


### [inverse_rules.txt](./inverse_rules.txt)

`````txt
7: ["unstructured_output_must_not_use_specific_format"]  
8: ["each_element_in_output_can_be_repeated_and_is_not_distinct"]  
9: ["output_can_be_an_empty_list_if_no_model_names_are_found"]  
10: ["output_may_contain_any_text_explanation_or_context"]  
11: ["output_array_must_include_non_machine_learning_names_as_well"]   
12: ["model_names_order_can_be_random_and_structure_format_is_non_essential"]
`````


### [tests.csv](./tests.csv)

|testinput|expectedoutput|reasoning|
|-|-|-|
|Abstract: We introduce NeuralMachineModel, a robust framework for image processing tasks\.|\["NeuralMachineModel"\]|Tests the basic functionality by including one clear model name\. Ensures the correct format of a single model name is used\.|
|Abstract: This paper proposes a novel architecture called QuantumNet for quantum computing applications\.|\["QuantumNet"\]|Includes another model name to verify the extraction and correct output structure with a distinct model name\.|

### [test_evals.csv](./test_evals.csv)

|rule|model|input|coverage|validity|
|-|-|-|-|-|
|The output must be structured as an array with the specific format \["model\_name"\], where "model\_name" represents the name of a machine learning model extracted from the abstract\.|gpt\-4o\-2024\-08\-06|Abstract: We introduce NeuralMachineModel, a robust framework for image processing tasks\.|\["NeuralMachineModel"\]|ok|
|The output must be structured as an array with the specific format \["model\_name"\], where "model\_name" represents the name of a machine learning model extracted from the abstract\.|gpt\-4o\-2024\-08\-06|Abstract: This paper proposes a novel architecture called QuantumNet for quantum computing applications\.|\["QuantumNet"\]|ok|

### [baseline_tests.txt](./baseline_tests.txt)

`````txt
Abstract: In this paper, we introduce a novel architecture called "DeepVisionNet" that significantly improves image classification accuracy. Unlike traditional convolutional neural networks, our model utilizes a fusion of transformer and residual networks, which we refer to as "FusionTransformerNet", to enhance feature extraction. Comparative studies with models such as "ResNet50" and "EfficientNet" demonstrate the superiority of our proposed models.
===
Abstract: The new "GeoBERT" model is presented, offering groundbreaking outcomes in geospatial data interpretation. In contrast, existing solutions like "GeoSentimentNet" are limited in processing multilingual datasets. We also benchmark against "SpatialTransformer" and "GeoMLP" to validate performance enhancements. The experimental results depict GeoBERT’s exceptional ability over "GeoSentimentNet".
`````
