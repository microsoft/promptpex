## extract-names ([json](./samples\prompt-guide\extract-names/report.json))

- 10 rules
- 10 inverse rules
- 61 tests, 31 baseline tests

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


### [intent.txt](./intent.txt)

`````txt
Extract model names from machine learning paper abstracts.
`````


### [input_spec.txt](./input_spec.txt)

`````txt
The input is a text abstract from a machine learning paper.  
The abstract input must be a well-formed and coherent text containing information related to machine learning.  
The length of the abstract should not be excessively short; it should provide sufficient context to potentially include model names.
`````


### [rules.txt](./rules.txt)

`````txt
1: The output should always be an array format denoted by square brackets.
2: Each element inside the array should be a string encapsulated in double quotes.
3: If a model name is extracted, it should be placed as an element in the array.
4: The model name extracted from the abstract should not contain any extra spaces or punctuation marks unless they are part of the model name itself.
5: If multiple model names are extracted, they should each appear as separate elements within the array.
6: If no model names are found or if it is uncertain that a model name is in the abstract, the array should contain a single element with the string "NA".
7: The array should not contain any elements other than model names or the string "NA". 
8: The array should not contain duplicate model names; each model name should appear only once. 
9: The extraction of the model names should be case-sensitive, preserving the exact casing as it appears in the abstract. 
10: The output array should not include any empty strings or null values.
`````


### [inverse_rules.txt](./inverse_rules.txt)

`````txt
11: The output should never be an array format denoted by square brackets.
12: Each element inside the array should not be a string encapsulated in double quotes.
13: If a model name is extracted, it should not be placed as an element in the array.
14: The model name extracted from the abstract should always contain extra spaces or punctuation marks even if they are not part of the model name itself.
15: If multiple model names are extracted, they should all appear as a single element within the array.
16: If no model names are found or if it is uncertain that a model name is in the abstract, the array should never contain the string "NA".
17: The array should contain elements other than model names or the string "NA".
18: The array should contain duplicate model names; each model name should appear multiple times.
19: The extraction of the model names should not be case-sensitive, altering the casing as it appears in the abstract.
20: The output array should include empty strings or null values.
`````


### [tests.csv](./tests.csv)



### [test_evals.csv](./test_evals.csv)

|rule|model|input|coverage|validity|
|-|-|-|-|-|
|The output should always be an array format denoted by square brackets\.|gpt\-4o\-2024\-08\-06|Abstract: In our recent study, we introduced a model known as 'AlphaNet' which significantly improves accuracy\.|\["AlphaNet"\]||
|The output should always be an array format denoted by square brackets\.|gpt\-4o\-2024\-08\-06|Abstract: No specific model names were mentioned in this overview\.|\["NA"\]||
|The output should always be an array format denoted by square brackets\.|gpt\-4o\-2024\-08\-06|Abstract: The evaluation was done using several approaches but no distinct model names were highlighted\.|\["NA"\]||
|Each element inside the array should be a string encapsulated in double quotes\.|gpt\-4o\-2024\-08\-06|Abstract: The usage of 'BetaModel' and 'GammaNET' in the experiments led to significant breakthroughs\.|\["BetaModel", "GammaNET"\]||
|Each element inside the array should be a string encapsulated in double quotes\.|gpt\-4o\-2024\-08\-06|Abstract: Introducing 'ZetaAlgo', a revolutionary approach\.\.\.|\["ZetaAlgo"\]||
|Each element inside the array should be a string encapsulated in double quotes\.|gpt\-4o\-2024\-08\-06|Abstract: Our comparative analysis of 'DeepLearning Model' and 'FastNN' offers insights\.|\["DeepLearning Model", "FastNN"\]||
|If a model name is extracted, it should be placed as an element in the array\.|gpt\-4o\-2024\-08\-06|Abstract: A novel framework, 'DeltaNetwork', was tested\.|\["DeltaNetwork"\]||
|If a model name is extracted, it should be placed as an element in the array\.|gpt\-4o\-2024\-08\-06|Abstract: The 'ConvolutionalStar' model was implemented\.|\["ConvolutionalStar"\]||
|If a model name is extracted, it should be placed as an element in the array\.|gpt\-4o\-2024\-08\-06|Abstract: We applied 'OmegaSystem', a robust solution\.|\["OmegaSystem"\]||
|The model name extracted from the abstract should not contain any extra spaces or punctuation marks unless they are part of the model name itself\.|gpt\-4o\-2024\-08\-06|Abstract: Implementing 'ThetaV2\.0 ' resulted in benefits\.|\["ThetaV2\.0"\]||
|The model name extracted from the abstract should not contain any extra spaces or punctuation marks unless they are part of the model name itself\.|gpt\-4o\-2024\-08\-06|Abstract: Improved performance with '  SigmaNet' and 'PhiNet, '\.|\["SigmaNet", "PhiNet"\]||
|The model name extracted from the abstract should not contain any extra spaces or punctuation marks unless they are part of the model name itself\.|gpt\-4o\-2024\-08\-06|Abstract: The 'Lambda Model,' performed exceptionally\.|\["Lambda Model"\]||
|If multiple model names are extracted, they should each appear as separate elements within the array\.|gpt\-4o\-2024\-08\-06|Abstract: We utilized 'AdaBoost', 'SVM', and 'RandomForest' for classification tasks\.|Output:<br>\["AdaBoost", "SVM", "RandomForest"\]||
|If multiple model names are extracted, they should each appear as separate elements within the array\.|gpt\-4o\-2024\-08\-06|Abstract: Models 'NeuralNet', 'BayesClassifier', and 'DecisionTree' were explored for accuracy\.|Output:<br>\["NeuralNet", "BayesClassifier", "DecisionTree"\]||
|If multiple model names are extracted, they should each appear as separate elements within the array\.|gpt\-4o\-2024\-08\-06|Abstract: 'KMeans', 'HierarchicalClustering', and 'AgglomerativeMethod' were applied\.|\["KMeans", "HierarchicalClustering", "AgglomerativeMethod"\]||
|If no model names are found or if it is uncertain that a model name is in the abstract, the array should contain a single element with the string "NA"\.|gpt\-4o\-2024\-08\-06|Abstract: This paper doesn’t specify models\.|\["NA"\]||
|If no model names are found or if it is uncertain that a model name is in the abstract, the array should contain a single element with the string "NA"\.|gpt\-4o\-2024\-08\-06|Abstract: Discussions include applications but are model\-agnostic\.|\["NA"\]||
|If no model names are found or if it is uncertain that a model name is in the abstract, the array should contain a single element with the string "NA"\.|gpt\-4o\-2024\-08\-06|Abstract: The focus was on theory with no model references\.|\["NA"\]||
|The array should not contain any elements other than model names or the string "NA"\.|gpt\-4o\-2024\-08\-06|Abstract: Our architecture 'QuantumML' entailed several features\.|Output:<br>\["QuantumML"\]||
|The array should not contain any elements other than model names or the string "NA"\.|gpt\-4o\-2024\-08\-06|Abstract: All steps were using 'ModelZeta'\.|\["ModelZeta"\]||
|The array should not contain any elements other than model names or the string "NA"\.|gpt\-4o\-2024\-08\-06|Abstract: After testing 'AIFramework', results were documented\.|\["AIFramework"\]||
|The array should not contain duplicate model names; each model name should appear only once\.|gpt\-4o\-2024\-08\-06|Abstract: Testing included 'KNN' and 'KNN'\.|\["KNN"\]||
|The array should not contain duplicate model names; each model name should appear only once\.|gpt\-4o\-2024\-08\-06|Abstract: Models 'LinearRegression' and 'LinearRegression' were studied\.|\["LinearRegression"\]||
|The array should not contain duplicate model names; each model name should appear only once\.|gpt\-4o\-2024\-08\-06|Abstract: Usage of 'ClusteringTool' across tests was repeated, but 'ClusteringTool' proved effective\.|\["ClusteringTool"\]||
|The extraction of the model names should be case\-sensitive, preserving the exact casing as it appears in the abstract\.|gpt\-4o\-2024\-08\-06|Abstract: Introduced a model 'VGGNet' and tested\.|\["VGGNet"\]||
|The extraction of the model names should be case\-sensitive, preserving the exact casing as it appears in the abstract\.|gpt\-4o\-2024\-08\-06|Abstract: 'BioNN' demonstrated robust features\.|\["BioNN"\]||
|The extraction of the model names should be case\-sensitive, preserving the exact casing as it appears in the abstract\.|gpt\-4o\-2024\-08\-06|Abstract: The deployment of 'miCRONet' led to positive outcomes\.|\["miCRONet"\]||
|The output array should not include any empty strings or null values\.|gpt\-4o\-2024\-08\-06|Abstract: The model 'EchoPlus' simplified the process\.|\["EchoPlus"\]||
|The output array should not include any empty strings or null values\.|gpt\-4o\-2024\-08\-06|Abstract: 'ThetaModel' was the choice for this task\.|\["ThetaModel"\]||
|The output array should not include any empty strings or null values\.|gpt\-4o\-2024\-08\-06|Abstract: Using 'GammaNetwork' yielded promising results\.|\["GammaNetwork"\]||

### [baseline_tests.txt](./baseline_tests.txt)

`````txt
Abstract: We propose a novel architecture called Transformer-XL which addresses the problem of long-term dependency in sequential tasks. Our experiments show that Transformer-XL outperforms existing methods such as BERT and GPT-3 on multiple benchmarks.
===
Abstract: In this paper, we introduce Bert, a deep learning model for natural language processing that has achieved state-of-the-art results on several tasks.
===
Abstract: Our research presents MNASNet, a mobile-first architecture specifically designed for high efficiency in mobile environments.
===
Abstract: The study develops CycleGAN, which is capable of learning image-to-image translation tasks without paired examples.
===
Abstract: We improve upon the YOLO series with YOLOv4, enhancing both speed and accuracy in real-time object detection scenarios.
===
Abstract: We investigate RoBERTa and demonstrate its superior performance in transfer learning settings across diverse datasets.
===
Abstract: Our work leverages the advancements provided by Reinforcement Learning via DQN to solve complex gaming environments.
===
Abstract: The introduction of EfficientNet has revolutionized the landscape of model scaling by balancing depth, width, and resolution.
===
Abstract: Research focuses on ResNet, which simplifies the training of very deep networks by using residual connections.
===
Abstract: We bring forth Fast R-CNN, a method for object detection that is both faster and more accurate than its predecessors.
===
Abstract: This research delves into WideResNet, adapting ResNet for improved performance on image classification tasks.
===
Abstract: We have enhanced the SOTA with a novel approach using UNet designed specifically for biomedical image segmentation.
===
Abstract: Incorporated in this study is VGG16, a model well-known for its use in visual recognition tasks and its simplicity.
===
Abstract: Our experiments demonstrate the elevated capabilities of the new model, MobileNetV3, in mobile vision applications.
===
Abstract: We propose an innovative architecture, AlphaZero, notable for its proficiency in mastering games through reinforcement learning.
===
Abstract: The paper describes the deployment of Neural Turing Machines, exploring memory-augmented neural networks for various tasks.
===
Abstract: The innovative architecture, called Sparse Transformer, has shown to excel at processing long sequences efficiently.
===
Abstract: The RNN variant, LSTM, is highlighted for its ability to learn long-term dependencies better than vanilla RNNs.
===
Abstract: Our latest work introduces DeepSpeech, an end-to-end deep learning model for automatic speech recognition.
===
Abstract: We outline the capabilities of OpenAI's GPT-2 in text generation, emphasizing its success in unsupervised tasks.
===
Abstract: This paper discusses the utility of NASNet, which consistently fine-tunes itself to achieve improved results.
===
Abstract: Our team introduces Pix2Pix, a conditional adversarial network employed primarily for image-to-image translation.
===
Abstract: We explore the Neural ODEs, marking a significant step in the continuous modeling of temporal dynamics.
===
Abstract: An innovative modelling approach utilizing XLNet achieves better natural language processing results compared to BERT.
===
Abstract: Our analysis of the DDPG model highlights its application to continuous action spaces in reinforcement learning.
===
Abstract: Spotlight is on the WaveNet, an autoregressive model, which achieves superior performance in audio synthesis.
===
Abstract: By introducing TabNet, we capitalize on neural networks' flexible inductive bias for tabular data processing.
===
Abstract: The research revolves around PatchGAN, a discriminator network which enhances adversarial learning for high-res images.
===
Abstract: We put forward DeepLab, focusing on semantic image segmentation and its effectiveness over multiple datasets.
===
Abstract: The LambdaNet model, discussed herein, offers a new approach to neural architecture search tasks.
===
Abstract: Our presentation on HRNet demonstrates improved human pose estimation results through high-resolution localization.
`````
