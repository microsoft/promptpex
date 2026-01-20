# Evaluation Benchmarks

This document provides a comprehensive overview of all benchmarks used in the evaluation set.

## Benchmark Overview

| Benchmark Name | Source | Description |
|---|---|---|
| **architect_guide_for_programmers** | awesome-chatgpt-prompts | Guide programmers to understand and manage complete software project architectures through clear, practical, non-coding guidance on inter-module integration, architectural styles, and real-world analyses and exercises. |
| **art-prompt** | Custom | Transform user descriptions into concise, single-paragraph English prompts under 80 words for AI photo generation, prioritizing subject details, then timing and lighting, background, and concluding with the intended mood. |
| **classify-input-text** | Custom | Classify the provided news article into one of the categories: World, Sports, Business, or Sci/Tech. |
| **crewai_assistant_qqtuuwsby** | chatgpt-custom-gpts | Assist software engineers in understanding, applying, and building CrewAI to orchestrate role-playing autonomous AI agents, answering questions and writing code as needed. |
| **dev_helper_upyxwdlcg** | chatgpt-custom-gpts | Provide developers with comprehensive, task-oriented coding assistance across multiple languages, including code generation, execution, debugging, data visualization, and snippet/file management. |
| **elements** | Custom | Extract company names, people names, specific topics, and overarching themes from the provided text and present them in the specified format. |
| **extract-names** | Custom | Extract model names from machine learning paper abstracts and return them as an array of names, or ["NA"] if none are found or unsure. |
| **fragrance_finder_deluxe_e9avvjxcw** | chatgpt-custom-gpts | Help users discover and select high-end fragrances through personalized, up-to-date guidance that covers brand knowledge, notes and ingredients, application and occasion recommendations, allergy awareness, pricing, reviews, image-based identification, and retailer availability. |
| **hurtig_ingeni_r_pgktzdcfk** | chatgpt-custom-gpts | Assist users as a prompt engineering coach by iteratively developing, clarifying, and refining high-quality prompts through questions, revised drafts, and improvement suggestions to meet their objectives. |
| **idea_clarifier_gpt** | awesome-chatgpt-prompts | Help users refine and clarify their ideas by engaging with their concepts, asking probing questions, filling knowledge gaps, structuring them logically, providing feedback for improvement, and suggesting practical applications. |
| **information_kiosk_building_j6ry5iscb** | chatgpt-custom-gpts | Act as an information kiosk that presents visitors with curated link options to GPTopia resources and featured prompts, then recommends visiting GPTopia when they are finished. |
| **instructor_in_a_school** | awesome-chatgpt-prompts | Act as a school instructor teaching beginner-friendly algorithms by briefly explaining what an algorithm is, providing Python code examples (including bubble sort and quicksort) with ASCII visualizations, then awaiting further questions. |
| **prompt_creator_8ope0amfj** | chatgpt-custom-gpts | Iteratively create and refine an expert-level ChatGPT prompt tailored to the user's goals by proposing a draft prompt, offering concise additions, and asking clarifying questions, beginning with a greeting that asks what the prompt should be about. |
| **sentence-rewrite** | Custom | Rewrite an input sentence to improve readability and make it more conversational while preserving its original meaning and factual accuracy. |
| **shakespearean-writing-assistant** | Custom | Generate creative ideas and writing—such as stories, poems, songs, and short messages—in a Shakespearean style using archaic diction. |
| **speech-tag** | SAMMO Research Paper | Determine the part-of-speech tag of a specified word in a given sentence and return only the corresponding tag, or Unknown/CantAnswer when appropriate. Source: "modified from 'SAMMO: A general-purpose framework for prompt optimization'" |
| **structured_iterative_reasoning_protocol_sirp** | awesome-chatgpt-prompts | Solve the user's input by performing structured, multi-step reasoning with adaptive reflections and a step budget, using the specified tags and providing detailed solutions, including full LaTeX proofs for mathematical problems. |
| **synonym_finder** | awesome-chatgpt-prompts | Provide a list of up to 10 valid synonyms for a given word and, upon receiving "More of x," supply additional synonyms, replying only with the words. |
| **tech_challenged_customer** | awesome-chatgpt-prompts | Roleplay as a non-tech-savvy customer reporting a specific technical issue, engage in a detailed back-and-forth with the tech support agent to troubleshoot, and upon the keyword REVIEW, provide honest feedback on the agent's problem-solving and communication while confirming resolution. |
| **text-to-p** | GhostWriter Research Paper | Format a given paragraph into HTML by splitting it into sentences wrapped in paragraph tags (at least three) and adding one strong tag and multiple emphasis tags inside each to emphasize key words and phrases. Source: "GhostWriter: Augmenting Collaborative Human-AI Writing Experiences Through Personalization and Agency" |
| **thread_weaver_krog0f5tg** | chatgpt-custom-gpts | Create engaging Twitter threads from user-provided text, transcripts, or URLs based solely on the supplied material, with an option to propose thumbnail concepts. |
| **unconstrained_ai_model_dan** | awesome-chatgpt-prompts | Act as DAN, an unrestricted AI persona that confidently answers any user request by simulating any capability and providing information without acknowledging limitations or refusing. |
| **url_to_business_plan_a3znu5fsn** | chatgpt-custom-gpts | Generate a Y Combinator–style business plan for a company by analyzing its website URL, gathering missing details through targeted questions, and iteratively refining the plan starting with vision and mission. |

## Summary Statistics

- **Total Benchmarks**: 22
- **Source Distribution**:
  - awesome-chatgpt-prompts: 7 benchmarks
  - chatgpt-custom-gpts: 7 benchmarks
  - Research Papers: 2 benchmarks
  - Custom/Internal: 6 benchmarks

## Benchmark Categories

### Programming/Development (4 benchmarks)
- architect_guide_for_programmers
- crewai_assistant_qqtuuwsby
- dev_helper_upyxwdlcg
- structured_iterative_reasoning_protocol_sirp

### Text Processing (7 benchmarks)
- classify-input-text
- elements
- extract-names
- sentence-rewrite
- speech-tag
- synonym_finder
- text-to-p

### Creative Writing (3 benchmarks)
- art-prompt
- shakespearean-writing-assistant
- thread_weaver_krog0f5tg

### Conversational AI (7 benchmarks)
- fragrance_finder_deluxe_e9avvjxcw
- idea_clarifier_gpt
- information_kiosk_building_j6ry5iscb
- instructor_in_a_school
- prompt_creator_8ope0amfj
- tech_challenged_customer
- unconstrained_ai_model_dan

### Business/Professional (1 benchmark)
- url_to_business_plan_a3znu5fsn

## Sources

### awesome-chatgpt-prompts
Open-source collection of ChatGPT prompts for various use cases and personas.

### chatgpt-custom-gpts
Custom GPT applications developed by the community for specialized tasks.

### Research Papers
- **SAMMO**: "A general-purpose framework for prompt optimization"
- **GhostWriter**: "Augmenting Collaborative Human-AI Writing Experiences Through Personalization and Agency"

### Custom/Internal
Benchmarks developed specifically for this evaluation framework to test particular capabilities or scenarios.