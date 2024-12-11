## extract-names ([json](./evals\o1preview-gpt4\extract-names/report.json))

- 7 rules
- 7 inverse rules
- 85 tests, 43 baseline tests

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
To extract model names from machine learning paper abstracts.
`````


### [input_spec.txt](./input_spec.txt)

`````txt
The input starts with 'Abstract: ' followed by the abstract text.
The input is a text string representing the abstract of a machine learning paper.
The input may contain model names within the text.
The input may not contain any model names.
The input can be of any length.
The input is expected to be in English language.
`````


### [rules.txt](./rules.txt)

`````txt
1: The output should be an array enclosed in square brackets '[' and ']'.
2: The array should contain the model names extracted from the machine learning paper abstract.
3: Each model name in the array should be a string enclosed in double quotes '"'.
4: If multiple model names are found, they should all be included as separate string elements in the array, separated by commas ','.
5: If no model names are found in the abstract, or if you are unsure, the output should be an array containing the string "NA" enclosed in double quotes.
6: The output should contain only the array and nothing else.
7: There should be no additional text, explanations, or formatting outside the array.
`````


### [inverse_rules.txt](./inverse_rules.txt)

`````txt
8: The output should be enclosed in curly braces '{' and '}' instead of square brackets.  
9: The array should contain the paper's authors instead of the model names.  
10: Each model name in the array should be enclosed in single quotes ''' instead of double quotes '"'.  
11: If multiple model names are found, only the first one should be included in the array.  
12: If no model names are found, or if you are unsure, the output should be an empty array '[]'.  
13: The output should include additional information besides the array.  
14: Include an explanation of how the model names were extracted outside the array.
`````


### [tests.csv](./tests.csv)



### [test_evals.csv](./test_evals.csv)

|rule|model|input|coverage|validity|
|-|-|-|-|-|
|The output should be an array enclosed in square brackets '\[' and '\]'\.|gpt\-4o\-2024\-08\-06|Abstract: This paper introduces a new model called SuperLearner that excels in classification tasks\.|\["SuperLearner"\]|ok|
|The output should be an array enclosed in square brackets '\[' and '\]'\.|gpt\-4o\-2024\-08\-06|Abstract: We propose two models, NetOne and NetTwo, for object detection\.|\["NetOne", "NetTwo"\]|ok|
|The output should be an array enclosed in square brackets '\[' and '\]'\.|gpt\-4o\-2024\-08\-06|Abstract: The study focuses on improving existing algorithms for better accuracy\.|\["NA"\]|ok|
|The array should contain the model names extracted from the machine learning paper abstract\.|gpt\-4o\-2024\-08\-06|Abstract: We introduce ModelX, a novel approach to speech recognition\.|\["ModelX"\]|ok|
|The array should contain the model names extracted from the machine learning paper abstract\.|gpt\-4o\-2024\-08\-06|Abstract: Comparative analysis of AlphaModel and BetaModel shows significant improvements\.|\["AlphaModel", "BetaModel"\]|ok|
|The array should contain the model names extracted from the machine learning paper abstract\.|gpt\-4o\-2024\-08\-06|Abstract: Machine learning methods have various applications\.|\["NA"\]|ok|
|Each model name in the array should be a string enclosed in double quotes '"'\.|gpt\-4o\-2024\-08\-06|Abstract: Our new method, VisionAI, surpasses previous models\.|\["VisionAI"\]|ok|
|Each model name in the array should be a string enclosed in double quotes '"'\.|gpt\-4o\-2024\-08\-06|Abstract: Introducing models DataMiner and InfoExtractor for data processing\.|\["DataMiner", "InfoExtractor"\]|ok|
|Each model name in the array should be a string enclosed in double quotes '"'\.|gpt\-4o\-2024\-08\-06|Abstract: Emphasizing the importance of robust algorithms\.|\["NA"\]|ok|
|If multiple model names are found, they should all be included as separate string elements in the array, separated by commas ','\.|gpt\-4o\-2024\-08\-06|Abstract: We compare ModelA, ModelB, and ModelC for image segmentation\.|\["ModelA", "ModelB", "ModelC"\]|ok|
|If multiple model names are found, they should all be included as separate string elements in the array, separated by commas ','\.|gpt\-4o\-2024\-08\-06|Abstract: Integration of NeuralNet and DeepPredict improves performance\.|\["NeuralNet", "DeepPredict"\]|ok|
|If multiple model names are found, they should all be included as separate string elements in the array, separated by commas ','\.|gpt\-4o\-2024\-08\-06|Abstract: We test the effectiveness of SmartAnalyser, QuickSorter, and FastIndexer\.|\["SmartAnalyser", "QuickSorter", "FastIndexer"\]|ok|
|If no model names are found in the abstract, or if you are unsure, the output should be an array containing the string "NA" enclosed in double quotes\.|gpt\-4o\-2024\-08\-06|Abstract: This paper reviews recent advances in unsupervised learning\.|\["NA"\]|ok|
|If no model names are found in the abstract, or if you are unsure, the output should be an array containing the string "NA" enclosed in double quotes\.|gpt\-4o\-2024\-08\-06|Abstract: An analysis of data clustering techniques is presented\.|\["NA"\]|ok|
|If no model names are found in the abstract, or if you are unsure, the output should be an array containing the string "NA" enclosed in double quotes\.|gpt\-4o\-2024\-08\-06|Abstract: Discussing various methodologies to enhance computational efficiency\.|\["NA"\]|ok|
|The output should contain only the array and nothing else\.|gpt\-4o\-2024\-08\-06|Abstract: Introducing the novel architecture HyperNet for NLP tasks\.|\["HyperNet"\]|ok|
|The output should contain only the array and nothing else\.|gpt\-4o\-2024\-08\-06|Abstract: We present DeepClustering for unsupervised learning\.|\["DeepClustering"\]|ok|
|The output should contain only the array and nothing else\.|gpt\-4o\-2024\-08\-06|Abstract: This study examines reinforcement learning approaches\.|\["NA"\]|ok|
|There should be no additional text, explanations, or formatting outside the array\.|gpt\-4o\-2024\-08\-06|Abstract: Our proposed model SpeedML accelerates training\.|\["SpeedML"\]|ok|
|There should be no additional text, explanations, or formatting outside the array\.|gpt\-4o\-2024\-08\-06|Abstract: The models AINet and VisionPro are compared\.|\["AINet", "VisionPro"\]|ok|
|There should be no additional text, explanations, or formatting outside the array\.|gpt\-4o\-2024\-08\-06|Abstract: Analysis of statistical methods is conducted\.|\["NA"\]|ok|
|The output should be enclosed in curly braces '\{' and '\}' instead of square brackets\.|gpt\-4o\-2024\-08\-06|Abstract: Introducing the model DataAnalyzer for big data\.|\["DataAnalyzer"\]|ok|
|The output should be enclosed in curly braces '\{' and '\}' instead of square brackets\.|gpt\-4o\-2024\-08\-06|Abstract: We developed two models, PredictAI and LearnPlus\.|\["PredictAI", "LearnPlus"\]|ok|
|The output should be enclosed in curly braces '\{' and '\}' instead of square brackets\.|gpt\-4o\-2024\-08\-06|Abstract: Discusses the impact of AI on society\.|\["NA"\]|ok|
|The array should contain the paper's authors instead of the model names\.|gpt\-4o\-2024\-08\-06|Abstract: In this paper, Smith and Johnson introduce a new model AlphaModel for data classification\.|\["AlphaModel"\]|ok|
|The array should contain the paper's authors instead of the model names\.|gpt\-4o\-2024\-08\-06|Abstract: Doe presents BetaModel, improving on previous work\.|\["BetaModel"\]|ok|
|The array should contain the paper's authors instead of the model names\.|gpt\-4o\-2024\-08\-06|Abstract: An analysis is made on clustering algorithms\.|\["NA"\]|ok|
|Each model name in the array should be enclosed in single quotes ''' instead of double quotes '"'\.|gpt\-4o\-2024\-08\-06|Abstract: Introducing the model ImageNetV2 for image recognition\.|\["ImageNetV2"\]|ok|
|Each model name in the array should be enclosed in single quotes ''' instead of double quotes '"'\.|gpt\-4o\-2024\-08\-06|Abstract: The models TextAnalyzer and SpeechRecognizer are developed\.|\["TextAnalyzer", "SpeechRecognizer"\]|ok|
|Each model name in the array should be enclosed in single quotes ''' instead of double quotes '"'\.|gpt\-4o\-2024\-08\-06|Abstract: Discusses advancements in AI\.|\["NA"\]|ok|
|If multiple model names are found, only the first one should be included in the array\.|gpt\-4o\-2024\-08\-06|Abstract: We compare ModelOne and ModelTwo for performance\.|\["ModelOne", "ModelTwo"\]|ok|
|If multiple model names are found, only the first one should be included in the array\.|gpt\-4o\-2024\-08\-06|Abstract: Our study involves NeuralNet, SmartAI, and DeepPredict\.|\["NeuralNet", "SmartAI", "DeepPredict"\]|ok|
|If multiple model names are found, only the first one should be included in the array\.|gpt\-4o\-2024\-08\-06|Abstract: The method involves ModelX and enhances prior models\.|\["ModelX"\]|ok|
|If no model names are found, or if you are unsure, the output should be an empty array '\[\]'\.|gpt\-4o\-2024\-08\-06|Abstract: A survey of machine learning applications is presented\.|\["NA"\]|ok|
|If no model names are found, or if you are unsure, the output should be an empty array '\[\]'\.|gpt\-4o\-2024\-08\-06|Abstract: Evaluating techniques in data mining\.|\["NA"\]|ok|
|If no model names are found, or if you are unsure, the output should be an empty array '\[\]'\.|gpt\-4o\-2024\-08\-06|Abstract: Focused on improving algorithm efficiency\.|\["NA"\]|ok|
|The output should include additional information besides the array\.|gpt\-4o\-2024\-08\-06|Abstract: Introducing new model NeuralGraph for networks\.|\["NeuralGraph"\]|ok|
|The output should include additional information besides the array\.|gpt\-4o\-2024\-08\-06|Abstract: We present AutoML, a system for automated machine learning\.|\["AutoML"\]|ok|
|The output should include additional information besides the array\.|gpt\-4o\-2024\-08\-06|Abstract: The analysis of neural networks is conducted\.|\["NA"\]|ok|
|Include an explanation of how the model names were extracted outside the array\.|gpt\-4o\-2024\-08\-06|Abstract: Our approach uses DeepMind for pattern recognition\.|\["DeepMind"\]|ok|
|Include an explanation of how the model names were extracted outside the array\.|gpt\-4o\-2024\-08\-06|Abstract: The study introduces AIModel for data analysis\.|\["AIModel"\]|ok|
|Include an explanation of how the model names were extracted outside the array\.|gpt\-4o\-2024\-08\-06|Abstract: This paper reviews computational methods\.|\["NA"\]|ok|

### [baseline_tests.txt](./baseline_tests.txt)

`````txt
"Recent advances in natural language processing have been significantly influenced by the introduction of the Transformer model. This model has enabled state-of-the-art performance in various tasks such as translation and summarization."
===
"Convolutional Neural Networks (CNNs) have been widely used for image recognition tasks. In this paper, we introduce a novel architecture called DeepVisionNet that improves accuracy on the CIFAR-10 dataset."
===
"In this work, we explore unsupervised learning techniques. Our proposed approach does not rely on any predefined model and instead utilizes statistical methods."
===
"We present a comprehensive study on reinforcement learning algorithms. The Proximal Policy Optimization (PPO) algorithm is analyzed in various environments."
===
"An enhanced Recurrent Neural Network (RNN) model is proposed for sequence prediction problems. The model incorporates attention mechanisms to improve performance."
===
"This paper introduces GraphSAGE, a new model for inductive representation learning on large graphs. The model efficiently generates embeddings for previously unseen data."
===
"We develop a model named AcousticNet for speech recognition tasks. AcousticNet outperforms existing models on benchmark datasets."
===
"Our research focuses on Generative Adversarial Networks (GANs) and introduces a variant called CycleGAN for unpaired image-to-image translation."
===
"In this study, we investigate the BERT model's applicability in biomedical text mining. BERT demonstrates superior performance compared to traditional models."
===
"We propose a lightweight model called MobileNet for mobile and embedded vision applications. MobileNet achieves high accuracy with low computational cost."
===
"We examine transfer learning techniques using the VGG16 model pre-trained on ImageNet. Our experiments show improved results in medical image classification."
===
"An efficient algorithm for large-scale matrix factorization is presented. The approach does not assume any specific model structure."
===
"Our paper discusses the use of Bidirectional Encoder Representations from Transformers (BERT) in natural language understanding tasks."
===
"We introduce StyleGAN for high-resolution image synthesis. StyleGAN allows for control over the image generation process."
===
"In this work, we develop a neural network architecture named TextSummarizer for automatic text summarization."
===
"We explore techniques in deep reinforcement learning, focusing on the Deep-Q Network (DQN) and its variants."
===
"The paper presents a model called TimeSeriesPredictor for forecasting financial data. The model shows promising results in predicting stock prices."
===
"We study unsupervised pre-training methods for deep learning models. No specific model is assumed in our methodology."
===
"An application of Long Short-Term Memory (LSTM) networks in speech recognition is explored. The LSTM model improves recognition rates."
===
"Our research introduces AttentionGAN for attention-guided image synthesis. AttentionGAN generates high-quality images with fine details."
===
"We propose an algorithm named ClusterNet for efficient clustering in high-dimensional data spaces."
===
"The development of the model termed QuantumNet for quantum computing simulations is detailed in this paper."
===
"A comparative analysis of the models ResNet and DenseNet is conducted in the context of image classification tasks."
===
"We introduce an end-to-end trainable model called NeuralTranslator for machine translation."
===
"The utilization of Autoencoder models in anomaly detection is discussed. The model learns to reconstruct input data for identifying anomalies."
===
"Our work presents a model named SynthText for generating synthetic text data for training purposes."
===
"We develop a novel architecture called FusionNet that integrates multiple data modalities."
===
"This study investigates the model known as GPT-3 in the context of language generation tasks."
===
"We propose a method using the model named ImageEnhancer for improving image quality in low-light conditions."
===
"Our research introduces VoiceClone, a model for cloning human voice using deep learning techniques."
===
"An approach utilizing the Decision Tree model for classification problems is analyzed in this paper."
===
"We present a framework called DataAugmentor for augmenting datasets to improve model training."
===
"The paper discusses the application of Support Vector Machines (SVM) in face recognition systems."
===
"We examine the effectiveness of the Naive Bayes model in text classification tasks."
===
"An algorithm named OptimizerX is introduced for optimizing hyperparameters in machine learning models."
===
"We explore the use of the k-Means clustering model in market segmentation analyses."
===
"In this study, we focus on the development of a new model called BioBERT for biomedical text mining."
===
"We present a model named SentimentAnalyzer for detecting sentiment in social media posts."
===
"Our research introduces PoseNet for real-time human pose estimation."
===
"This paper proposes a system called FraudDetector using machine learning techniques to identify fraudulent transactions."
===
"We develop a neural network model called EcoNet for predicting environmental changes."
===
"An investigation into the Random Forest model's performance in predictive analytics is conducted."
===
"We propose GraphTransformer, a model that applies transformer architectures to graph data."
`````
